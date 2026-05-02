# pyright: reportMissingImports=false

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from services.backend.services.download import run_download
from services.backend.services.processor import save_and_split
from services.backend.database import get_db       # 추가: get_db 임포트
from services.backend.services.download import run_download
from services.backend import models
from services.backend import database

router = APIRouter()

tasks_db = {}


@router.post("/instagram", summary="인스타그램 영상 수집", tags=["Upload"])
async def receive_instagram(
    background_tasks: BackgroundTasks,
    title: str = Form(..., description="영상 제목"),
    link: str = Form(..., description="인스타그램 영상 링크"),
    db: Session = Depends(get_db) # DB 세션 주입
):
    if "instagram.com" not in link:
        raise HTTPException(status_code=400, detail="유효한 인스타그램 링크가 아닙니다.")

    task_id = str(uuid4())
    new_task = models.VideoMetadata(
        task_id=task_id,
        origin_url=link,
        status="PENDING"
    )
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
):
    task_id = str(uuid4())
    content = await videoFile.read()
    download_dir, video_path, audio_path = save_and_split(task_id, videoFile.filename, content)
    tasks_db[task_id] = {
        "status": "DONE",
        "verdict": None,
        "title": title,
        "download_dir": download_dir,
        "video_path": video_path,
        "audio_path": audio_path,
    }

    return {
        "task_id": task_id,
        "timestamp": datetime.now().isoformat(),
        "message": "수집 요청이 완료되었습니다.",
    }


@router.get("/status/{task_id}", summary="분석 상태 조회", tags=["Status"])
async def get_status(task_id: str, db: Session = Depends(database.get_db)):
    
    # 1. MySQL DB에서 해당 task_id를 가진 데이터를 찾습니다.
    task = db.query(models.VideoMetadata).filter(models.VideoMetadata.task_id == task_id).first()

    # 2. 만약 DB에 없다면 404 에러를 냅니다.
    if not task:
        raise HTTPException(status_code=404, detail="해당 task_id를 DB에서 찾을 수 없습니다.")

    # 3. DB에 있는 성공 데이터를 반환합니다.
    return {
        "task_id": task.task_id,
        "status": task.status,
        "origin_url": task.origin_url,
        "video_path": task.storage_path,
        "audio_path": task.audio_path,
        "phash_value": task.phash_value,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }