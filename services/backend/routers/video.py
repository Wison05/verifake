# pyright: reportMissingImports=false, reportMissingModuleSource=false, reportUninitializedInstanceVariable=false

import subprocess
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel

from services.ai.common.job_paths import build_job_paths
from services.backend.services.download import run_download
from services.backend.services.processor import (
    run_video_stage1_preprocess_job,
    save_and_split,
)

router = APIRouter()

tasks_db = {}


class VideoStage1PreprocessRequest(BaseModel):
    file_path: str
    job_id: str | None = None


@router.post("/instagram", summary="인스타그램 영상 수집", tags=["Video"])
async def receive_instagram(
    background_tasks: BackgroundTasks,
    title: str = Form(..., description="영상 제목"),
    link: str = Form(..., description="인스타그램 영상 링크"),
):
    if "instagram.com" not in link:
        raise HTTPException(status_code=400, detail="유효한 인스타그램 링크가 아닙니다.")

    task_id = str(uuid4())
    tasks_db[task_id] = {"status": "PENDING", "verdict": None, "title": title}
    background_tasks.add_task(run_download, task_id, link, tasks_db)

    return {
        "task_id": task_id,
        "timestamp": datetime.now().isoformat(),
        "message": "수집 요청이 완료되었습니다.",
    }


@router.post("/video", summary="영상 파일 수집", tags=["Video"])
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
async def get_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="해당 task_id를 찾을 수 없습니다.")

    task = tasks_db[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "verdict": task["verdict"],
        "video_path": task.get("video_path"),
        "audio_path": task.get("audio_path"),
        "error": task.get("error"),
        "timestamp": datetime.now().isoformat(),
    }


@router.post("/video-stage1/preprocess", summary="Stage1 A 전처리 실행", tags=["Video"])
def preprocess_video_stage1(req: VideoStage1PreprocessRequest):
    try:
        input_path = Path(req.file_path)

        if not input_path.exists():
            raise HTTPException(status_code=400, detail="파일이 존재하지 않습니다.")

        result = run_video_stage1_preprocess_job(input_path, job_id=req.job_id)
        job_paths = build_job_paths(result["job_id"])

        return {
            "job_id": result["job_id"],
            "status": result["status"],
            "preprocessing_json": job_paths["preprocessing_json_path"].as_posix(),
        }

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="ffmpeg 실행 실패")

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
