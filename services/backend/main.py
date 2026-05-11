# pyright: reportMissingImports=false, reportUnknownMemberType=false

import PIL.Image
import static_ffmpeg

static_ffmpeg.add_paths()

# ANTIALIAS는 Pillow 10에서 제거됨
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from fastapi import FastAPI
from services.backend.routers import video, instagram, audio, user, media
from services.backend.database import engine
from services.backend import models

from services.backend import models
from services.backend.database import engine
from services.backend.routers import audio, instagram, user, video

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VeriFake API",
    description="영상 업로드 및 분석 상태 조회 API 문서",
    version="1.0.0",
)


@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "running", "database": "MySQL Connected"}


app.include_router(video.router, prefix="/api/v1")
app.include_router(instagram.router, prefix="/api/v1")
app.add_api_route(
    "/media/video-stage1/explain",
    media.explain_video_stage1,
    methods=["POST"],
    summary="영상/음성 result.json 기반 LLM 설명 생성",
    tags=["Media"],
)
app.include_router(audio.router, prefix="/api/v1/audio")
app.include_router(user.router, prefix="/api/v1")
