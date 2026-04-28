# pyright: reportMissingImports=false, reportMissingModuleSource=false, reportUninitializedInstanceVariable=false

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
import uuid
import subprocess

from services.backend.processor import separate_streams
from services.ai.pipelines.video_stage1.detect import run_video_stage1_detection

router = APIRouter()

# 요청 데이터 형식
class SplitRequest(BaseModel):
    file_path: str


class VideoStage1DetectRequest(BaseModel):
    preprocessing_json: str


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


@router.post("/video-stage1/detect")
def detect_video_stage1(req: VideoStage1DetectRequest):
    preprocessing_json_path = Path(req.preprocessing_json)

    if not preprocessing_json_path.exists():
        raise HTTPException(
            status_code=400,
            detail="preprocessing.json 파일이 존재하지 않습니다.",
        )

    try:
        detection = run_video_stage1_detection(str(preprocessing_json_path))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    job_root = preprocessing_json_path.parent.parent
    return {
        "job_id": detection["job_id"],
        "status": detection.get("status", "success"),
        "detection_json": str(job_root / "output" / "detection.json"),
        "result_json": str(job_root / "output" / "result.json"),
    }
