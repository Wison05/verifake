# pyright: reportMissingImports=false, reportUnknownMemberType=false

import os
from typing import Any

import PIL.Image
import static_ffmpeg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

static_ffmpeg.add_paths()

# ANTIALIAS는 Pillow 10에서 제거됨
if not hasattr(PIL.Image, "ANTIALIAS"):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from services.backend.routers import video, instagram, audio, user, media, history
from services.backend.database import engine
from services.backend import models


# ============ 환경변수 로드 ============

def _get_cors_origins() -> list[str]:
    """CORS 허용 오리진 로드
    
    환경변수 CORS_ORIGINS (쉼표 구분)에서 로드하거나,
    없으면 기본값 사용
    """
    cors_origins = os.getenv("CORS_ORIGINS", "")
    if cors_origins:
        return [origin.strip() for origin in cors_origins.split(",")]
    
    # 기본값: 로컬 개발 + 모바일 앱
    return [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "capacitor://localhost",  # React Native (Capacitor)
    ]


def _get_app_environment() -> str:
    """실행 환경 로드 (development, staging, production)"""
    return os.getenv("APP_ENV", "development")


# ============ 데이터베이스 초기화 ============

models.Base.metadata.create_all(bind=engine)


# ============ FastAPI 앱 초기화 ============

app = FastAPI(
    title="VeriFake API",
    description="영상 업로드 및 분석 상태 조회 API 문서",
    version="1.0.0",
)


# ============ CORS 미들웨어 ============

cors_origins = _get_cors_origins()
app_env = _get_app_environment()

# 개발 환경에서는 모든 오리진 허용, 프로덕션에서는 제한
allow_all_origins = app_env == "development"

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if not allow_all_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "User-Agent",
    ],
    max_age=3600,  # preflight 캐시 1시간
)

if app_env != "production":
    print(f"🔓 CORS 허용 오리진 ({app_env}): {cors_origins}")


# ============ 헬스 체크 ============

@app.get("/", tags=["Health Check"])
def read_root() -> dict[str, Any]:
    """서버 상태 확인"""
    return {
        "status": "running",
        "database": "MySQL Connected",
        "environment": app_env,
    }


@app.get("/health", tags=["Health Check"])
def health_check() -> dict[str, str]:
    """헬스 체크 엔드포인트"""
    return {"status": "ok"}


# ============ 라우터 등록 ============

# 영상 분석 (Stage1 A/B)
app.include_router(video.router, prefix="/api/v1")

# 인스타그램 다운로드
app.include_router(instagram.router, prefix="/api/v1")

# 미디어 처리 (영상/음성 분리, LLM 설명)
app.include_router(media.router, prefix="/api/v1/media", tags=["Media"])

# 오디오 분석
app.include_router(audio.router, prefix="/api/v1/audio", tags=["Audio"])

# 사용자 관리
app.include_router(user.router, prefix="/api/v1", tags=["User"])

app.include_router(history.router, prefix="/api/v1")  # [+ 추가]

app.add_api_route(
    "/media/video-stage1/explain",
    media.explain_video_stage1,
    methods=["POST"],
    summary="영상/음성 result.json 기반 LLM 설명 생성",
    tags=["Media"],
)

if __name__ == "__main__":
    import uvicorn
    
    # 환경변수에서 호스트, 포트 로드
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    
    print(f"🚀 VeriFake API 시작: {host}:{port} ({app_env})")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=app_env != "production",
    )
