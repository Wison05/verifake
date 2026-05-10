# pyright: reportMissingImports=false, reportMissingModuleSource=false, reportUninitializedInstanceVariable=false
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.ai.common.job_paths import build_job_paths
from services.ai.pipelines.video_stage1.config import get_stage1_storage_root
from services.ai.pipelines.video_stage1.detect import run_video_stage1_detection
from services.ai.pipelines.video_stage1.exceptions import Stage1UnavailableError
from services.backend.services.processor import run_video_stage1_preprocess_job

router = APIRouter()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
VALID_JOB_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")

_GENERIC_ERROR = "내부 서버 오류가 발생했습니다."
_PREPROCESS_RUNTIME_ERROR = "Stage1 A AI 런타임이 준비되지 않았습니다."
_DETECT_RUNTIME_ERROR = "Stage1 B AI 런타임이 준비되지 않았습니다."


# ---------------------------------------------------------------------------
# 요청 스키마
# ---------------------------------------------------------------------------

class VideoStage1PreprocessRequest(BaseModel):
    file_path: str
    job_id: str | None = None


class VideoStage1DetectRequest(BaseModel):
    preprocessing_json: str


# ---------------------------------------------------------------------------
# 경로 검증 헬퍼
# ---------------------------------------------------------------------------

def _get_stage1_storage_root() -> Path:
    raw = Path(get_stage1_storage_root())
    return (PROJECT_ROOT / raw).resolve() if not raw.is_absolute() else raw.resolve()


def _is_within_directory(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def _resolve_existing_path(raw_path: str) -> Path:
    resolved = Path(raw_path).expanduser().resolve()
    if not resolved.exists():
        raise HTTPException(status_code=400, detail="파일이 존재하지 않습니다.")
    return resolved


def _validate_project_file_path(raw_path: str) -> Path:
    resolved = _resolve_existing_path(raw_path)
    if not _is_within_directory(resolved, PROJECT_ROOT):
        raise HTTPException(status_code=400, detail="프로젝트 내부 파일만 허용됩니다.")
    return resolved


def _validate_preprocessing_json_path(raw_path: str) -> Path:
    resolved = _resolve_existing_path(raw_path)
    storage_root = _get_stage1_storage_root()
    if resolved.name != "preprocessing.json" or not _is_within_directory(resolved, storage_root):
        raise HTTPException(
            status_code=400,
            detail="Stage1 storage_root 내부 preprocessing.json만 허용됩니다.",
        )
    return resolved


def _validate_job_id(job_id: str | None) -> None:
    if job_id is not None and not VALID_JOB_ID_PATTERN.fullmatch(job_id):
        raise HTTPException(status_code=400, detail="job_id 형식이 올바르지 않습니다.")


# ---------------------------------------------------------------------------
# 엔드포인트
# ---------------------------------------------------------------------------

@router.post("/video-stage1/preprocess", summary="Stage1 A 전처리 실행", tags=["Video"])
def preprocess_video_stage1(req: VideoStage1PreprocessRequest) -> dict:
    try:
        _validate_job_id(req.job_id)
        input_path = _validate_project_file_path(req.file_path)

        result = run_video_stage1_preprocess_job(input_path, job_id=req.job_id)
        storage_root = _get_stage1_storage_root()
        job_paths = build_job_paths(result["job_id"], storage_root=storage_root)

        return {
            "job_id": result["job_id"],
            "status": result["status"],
            "preprocessing_json": job_paths["preprocessing_json_path"].as_posix(),
        }

    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="ffmpeg 실행 실패")
    except Stage1UnavailableError:
        raise HTTPException(status_code=500, detail=_PREPROCESS_RUNTIME_ERROR)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail=_GENERIC_ERROR)


@router.post("/video-stage1/detect", summary="Stage1 B 탐지 실행", tags=["Video"])
def detect_video_stage1(req: VideoStage1DetectRequest) -> dict:
    preprocessing_json_path = _validate_preprocessing_json_path(req.preprocessing_json)

    try:
        detection = run_video_stage1_detection(str(preprocessing_json_path))
    except Stage1UnavailableError:
        raise HTTPException(status_code=500, detail=_DETECT_RUNTIME_ERROR)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=_GENERIC_ERROR) from exc

    storage_root = _get_stage1_storage_root()
    job_paths = build_job_paths(detection["job_id"], storage_root=storage_root)

    return {
        "job_id": detection["job_id"],
        "status": detection.get("status", "success"),
        "detection_json": job_paths["detection_json_path"].as_posix(),
        "result_json": job_paths["result_json_path"].as_posix(),
    }
