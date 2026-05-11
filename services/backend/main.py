# pyright: reportMissingImports=false, reportUnknownMemberType=false

import logging

import static_ffmpeg
try:
    static_ffmpeg.add_paths()
except Exception as exc:
    logging.getLogger(__name__).warning(
        "static_ffmpeg add_paths() failed, skipping runtime auto-download: %s",
        exc,
    )

from fastapi import FastAPI
import PIL.Image

if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

app = FastAPI(
    title="VeriFake API",
    description="영상/얼굴 판별, 모델 추론 API 서버",
    version="1.0.0",
)
logger = logging.getLogger(__name__)

database_connected = False
try:
    from services.backend.database import engine
    from services.backend import models

    models.Base.metadata.create_all(bind=engine)
    database_connected = True
except Exception as exc:
    logger.warning("Database initialization skipped: %s", exc)


from typing import Optional


def _load_router(module_name: str, *, prefix: Optional[str] = None) -> None:
    try:
        module = __import__(f"services.backend.routers.{module_name}", fromlist=[module_name])
    except Exception as exc:
        logger.warning("%s router disabled during import: %s", module_name, exc)
        return

    if prefix is None:
        app.add_api_route(
            "/media/video-stage1/explain",
            module.explain_video_stage1,
            methods=["POST"],
            summary="영상/얼굴 result.json 기반 LLM 결과 생성",
            tags=["Media"],
        )
        return

    try:
        app.include_router(module.router, prefix=prefix)
    except Exception as exc:
        logger.warning("%s router disabled while registering: %s", module_name, exc)


_load_router("video", prefix="/api/v1")
_load_router("instagram", prefix="/api/v1")
_load_router("audio", prefix="/api/v1/audio")
_load_router("user", prefix="/api/v1")
_load_router("media", prefix=None)


@app.get("/", tags=["Health Check"])
def read_root():
    return {
        "status": "running",
        "database": "connected" if database_connected else "disabled",
    }
