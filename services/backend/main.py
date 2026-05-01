# pyright: reportMissingImports=false

import static_ffmpeg
_ = static_ffmpeg.add_paths()

from fastapi import FastAPI
from services.backend.routers import instagram

app = FastAPI(
    title="VeriFake API",
    description="영상 업로드, 영상/음성 분리, 상태 조회 API 문서",
    version="1.0.0"
)

app.include_router(instagram.router, prefix="/api/v1")
