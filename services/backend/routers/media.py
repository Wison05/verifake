import subprocess
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.ai.common.job_paths import build_job_paths
from services.backend.processor import run_video_stage1_preprocess_job, separate_streams

router = APIRouter()

# 요청 데이터 형식
class SplitRequest(BaseModel):
    file_path: str


class VideoStage1PreprocessRequest(BaseModel):
    file_path: str
    job_id: str | None = None


@router.post("/split")
def split_media(req: SplitRequest):
    try:
        job_id = str(uuid.uuid4())
        input_path = Path(req.file_path)

        # 파일 존재 확인
        if not input_path.exists():
            raise HTTPException(status_code=400, detail="파일이 존재하지 않습니다.")

        video, audio = separate_streams(input_path, job_id)

        return {
            "job_id": job_id,
            "video": video,
            "audio": audio
        }

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="ffmpeg 실행 실패")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/video-stage1/preprocess")
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
