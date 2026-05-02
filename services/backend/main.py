# pyright: reportMissingImports=false

import static_ffmpeg
static_ffmpeg.add_paths()

from fastapi import FastAPI
from services.backend.routers import video, instagram, audio
from services.backend.database import engine
from services.backend import models

import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VeriFake API",
    description="영상 업로드 및 분석 상태 조회 API 문서",
    version="1.0.0"
)
# 기본 루트 경로 (서버 상태 확인용)
@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "running", "database": "MySQL Connected"}

app.include_router(video.router, prefix="/api/v1")
app.include_router(video.router, prefix="/media")
app.include_router(instagram.router, prefix="/api/v1")
app.include_router(audio.router, prefix="/api/v1/audio")
