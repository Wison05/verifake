# pyright: reportMissingImports=false, reportUnknownMemberType=false

import static_ffmpeg
_ = static_ffmpeg.add_paths()

from fastapi import FastAPI
from services.backend.routers import instagram, media

app = FastAPI(
    title="VeriFake API",
    description="영상 업로드, 영상/음성 분리, 상태 조회 API 문서",
    version="1.0.0"
)

app.include_router(instagram.router, prefix="/api/v1")
app.add_api_route(
    "/media/video-stage1/explain",
    media.explain_video_stage1,
    methods=["POST"],
    summary="영상/음성 result.json 기반 LLM 설명 생성",
    tags=["Media"],
)
