from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import uuid
import subprocess

from services.backend.processor import separate_streams

router = APIRouter()

# 요청 데이터 형식
class SplitRequest(BaseModel):
    file_path: str


@router.post("/split")
def split_media(req: SplitRequest):
    try:
        job_id = str(uuid.uuid4())
        input_path = Path(req.file_path)

        # 파일 존재 확인
        if not input_path.exists():
            raise HTTPException(status_code=400, detail="파일이 존재하지 않습니다.")

        # 분리 실행
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