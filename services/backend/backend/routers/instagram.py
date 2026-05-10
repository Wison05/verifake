# pyright: reportMissingImports=false
from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from services.backend import crud, models
from services.backend.database import get_db
from services.backend.services.download import run_download
from services.backend.services.processor import save_and_split

router = APIRouter()


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

    background_tasks.add_task(run_download, task_id, link)

    return {
        "task_id": task_id,
        "status": "PENDING",
        "timestamp": datetime.now().isoformat(),
        "message": "수집 요청이 완료되었습니다.",
    }


@router.post("/video", summary="영상 파일 수집", tags=["Upload"])
async def receive_video(
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
        status="DONE",
    )
    db.add(new_task)
    db.commit()

    return {
        "task_id": task_id,
        "timestamp": datetime.now().isoformat(),
        "message": "수집 요청이 완료되었습니다.",
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
