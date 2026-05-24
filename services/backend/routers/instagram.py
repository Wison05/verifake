# pyright: reportMissingImports=false
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from services.backend import crud, models
from services.backend.database import SessionLocal, get_db
from services.backend.services.download import run_download
from services.backend.services.processor import save_and_split
from services.backend.services.video_analyzer import parse_result_json, run_video_detect_job
from services.backend.tasks import create_video_detect_job

router = APIRouter()


# ---------------------------------------------------------------------------
# 내부 헬퍼: 전처리 → 탐지 파이프라인 (BackgroundTask 에서 호출)
# ---------------------------------------------------------------------------

def _run_video_pipeline(task_id: str, video_path: str) -> None:
    """전처리(preprocess) → 탐지(detect) → DB 저장 백그라운드 파이프라인.

    1. video stage1 preprocess 실행
    2. 생성된 preprocessing.json 으로 detect job 등록 및 실행
    3. result.json 파싱 → VideoMetadata.verdict / deepfake_score 저장
    """
    from services.ai.pipelines.video_stage1.config import get_stage1_storage_root
    from services.ai.common.job_paths import build_job_paths
    from services.backend.routers.video import run_video_stage1_preprocess_job

    db: Session = SessionLocal()
    try:
        task = db.query(models.VideoMetadata).filter(
            models.VideoMetadata.task_id == task_id
        ).first()
        if not task:
            return

        # ── 상태: 전처리 중 ──────────────────────────────────────────────
        task.status = "PREPROCESSING"
        db.commit()

        # 1. Stage1 전처리
        try:
            preprocess_result = run_video_stage1_preprocess_job(
                Path(video_path), job_id=task_id
            )
        except Exception as exc:
            task.status = "FAILED"
            db.commit()
            print(f"[pipeline] preprocess failed for {task_id}: {exc}")
            return

        storage_root = Path(get_stage1_storage_root())
        if not storage_root.is_absolute():
            storage_root = (Path(__file__).resolve().parents[3] / storage_root).resolve()

        job_paths = build_job_paths(preprocess_result["job_id"], storage_root=storage_root)
        preprocessing_json: Path = job_paths["preprocessing_json_path"]

        if not preprocessing_json.exists():
            task.status = "FAILED"
            db.commit()
            print(f"[pipeline] preprocessing.json not found for {task_id}")
            return

        # ── 상태: AI 탐지 중 ─────────────────────────────────────────────
        task.status = "ANALYZING"
        db.commit()

        # 2. Stage1 탐지 job 등록 & 동기 실행
        artifacts_dir = str(Path("storage/jobs") / task_id / "output")
        create_video_detect_job(task_id, str(preprocessing_json.resolve()), artifacts_dir)
        run_video_detect_job(task_id, preprocessing_json)  # blocking in background thread

        # 3. result.json 파싱 → DB 저장
        result_path = Path(artifacts_dir) / "result.json"
        if not result_path.exists():
            # detect job 이 결과를 저장한 경로를 tasks_db 에서 확인
            from services.backend.tasks import get_video_detect_job
            job = get_video_detect_job(task_id)
            if job and job.get("result_path"):
                result_path = Path(job["result_path"])

        if result_path.exists():
            try:
                verdict, score = parse_result_json(result_path)
                # B1이 DB 마이그레이션 완료 전까지 컬럼이 없을 수 있으므로 방어 처리
                if hasattr(task, "verdict"):
                    task.verdict = verdict
                if hasattr(task, "deepfake_score"):
                    task.deepfake_score = score
                task.status = "COMPLETED"
            except Exception as exc:
                print(f"[pipeline] result parse failed for {task_id}: {exc}")
                task.status = "FAILED"
        else:
            task.status = "FAILED"
            print(f"[pipeline] result.json not found for {task_id}")

        db.commit()

    except Exception as exc:
        db.rollback()
        try:
            task = db.query(models.VideoMetadata).filter(
                models.VideoMetadata.task_id == task_id
            ).first()
            if task:
                task.status = "FAILED"
                db.commit()
        except Exception:
            pass
        print(f"[pipeline] unexpected error for {task_id}: {exc}")
    finally:
        db.close()


def _run_download_then_pipeline(task_id: str, url: str) -> None:
    """인스타그램 다운로드 완료 후 비디오 파이프라인 자동 트리거.

    run_download 는 async 함수이므로 새 이벤트 루프로 실행한 뒤
    성공 시 _run_video_pipeline 을 이어서 호출합니다.
    다운로드 실패 시 status 를 FAILED 로 업데이트합니다.
    """
    import asyncio

    # async run_download 를 동기 맥락에서 실행
    try:
        asyncio.run(run_download(task_id, url))
    except Exception as exc:
        print(f"[download] failed for {task_id}: {exc}")
        _set_task_status(task_id, "FAILED")
        return

    # 다운로드 후 DB 에서 video_path 조회
    db: Session = SessionLocal()
    try:
        task = db.query(models.VideoMetadata).filter(
            models.VideoMetadata.task_id == task_id
        ).first()
        if not task or not task.storage_path:
            _set_task_status(task_id, "FAILED")
            return
        video_path = task.storage_path
    finally:
        db.close()

    # 파이프라인 실행
    _run_video_pipeline(task_id, video_path)


def _set_task_status(task_id: str, status: str) -> None:
    db: Session = SessionLocal()
    try:
        task = db.query(models.VideoMetadata).filter(
            models.VideoMetadata.task_id == task_id
        ).first()
        if task:
            task.status = status
            db.commit()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# 엔드포인트
# ---------------------------------------------------------------------------

@router.post("/instagram", summary="인스타그램 영상 수집", tags=["Upload"])
async def receive_instagram(
    background_tasks: BackgroundTasks,
    title: str = Form(..., description="영상 제목"),
    link: str = Form(..., description="인스타그램 영상 링크"),
    db: Session = Depends(get_db),
) -> dict:
    if "instagram.com" not in link:
        raise HTTPException(status_code=400, detail="유효한 인스타그램 링크가 아닙니다.")

    task_id = str(uuid4())
    new_task = models.VideoMetadata(task_id=task_id, origin_url=link, status="PENDING")
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # 다운로드 완료 후 자동으로 video 파이프라인 트리거
    background_tasks.add_task(_run_download_then_pipeline, task_id, link)

    return {
        "task_id": task_id,
        "status": "PENDING",
        "timestamp": datetime.now().isoformat(),
        "message": "수집 요청이 완료되었습니다.",
    }


@router.post("/video", summary="영상 파일 수집", tags=["Upload"])
async def receive_video(
    background_tasks: BackgroundTasks,
    title: str = Form(..., description="영상 제목"),
    videoFile: UploadFile = File(..., description="업로드할 영상 파일"),
    db: Session = Depends(get_db),
) -> dict:
    task_id = str(uuid4())
    content = await videoFile.read()
    download_dir, video_path, audio_path = save_and_split(task_id, videoFile.filename, content)

    new_task = models.VideoMetadata(
        task_id=task_id,
        download_dir=download_dir,
        storage_path=video_path,
        audio_path=audio_path,
        status="PENDING",  # 파이프라인이 완료되면 COMPLETED 로 업데이트됨
    )
    db.add(new_task)
    db.commit()

    # 업로드 완료 즉시 AI 파이프라인 백그라운드 실행
    background_tasks.add_task(_run_video_pipeline, task_id, video_path)

    return {
        "task_id": task_id,
        "status": "PENDING",
        "timestamp": datetime.now().isoformat(),
        "message": "수집 요청이 완료되었습니다. 분석이 백그라운드에서 시작됩니다.",
    }


@router.get("/status/{task_id}", summary="분석 상태 조회", tags=["Status"])
async def get_status(task_id: str, db: Session = Depends(get_db)) -> dict:
    task = crud.get_task_by_id(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="해당 task_id를 DB에서 찾을 수 없습니다.")

    return {
        "task_id": task.task_id,
        "user_id": task.user_id,
        "status": task.status,
        "origin_url": task.origin_url,
        "video_path": task.storage_path,
        "audio_path": task.audio_path,
        "phash_value": task.phash_value,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }
