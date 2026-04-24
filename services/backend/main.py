import static_ffmpeg
static_ffmpeg.add_paths()

from fastapi import FastAPI
from services.backend.routers import media
from services.backend import download_service

app = FastAPI(
    title="VeriFake API",
    description="영상 업로드 및 분석 상태 조회 API 문서",
    version="1.0.0"
)

app.include_router(media.router, prefix="/media")
app.include_router(download_service.router, prefix="/api/v1")