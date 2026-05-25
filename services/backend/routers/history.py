# routers/history.py
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from services.backend import models
from services.backend.database import get_db

router = APIRouter()

# --- Response Schemas (응답 형태 정의) ---

class HistoryItemResponse(BaseModel):
    id: int
    task_id: str
    status: str
    verdict: Optional[str] = None
    deepfake_score: Optional[float] = None
    # 현재 모델에 title, thumbnail_path가 없다면 None으로 반환되거나 
    # 이후 DB 마이그레이션 시 추가가 필요합니다.
    title: Optional[str] = "분석 영상" 
    thumbnail_path: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # SQLAlchemy 객체를 자동으로 읽어오기 위한 설정

class HistoryListResponse(BaseModel):
    total: int
    items: List[HistoryItemResponse]
    limit: int
    offset: int

# --- API Endpoints ---

@router.get(
    "/history",
    summary="분석 기록 목록 조회",
    tags=["History"],
    response_model=HistoryListResponse
)
async def get_history_list(
    user_id: Optional[str] = Query(None, description="특정 유저의 기록만 필터링"),
    limit: int = Query(10, ge=1, le=100, description="페이지당 항목 수"),
    offset: int = Query(0, ge=0, description="건너뛸 항목 수"),
    db: Session = Depends(get_db)
):
    """
    전체 또는 특정 유저의 분석 기록 목록을 반환합니다.
    페이지네이션(limit, offset)을 지원하며 최신순으로 정렬됩니다.
    """
    query = db.query(models.VideoMetadata)
    
    # 1. [+ 추가] 유저 필터링 로직
    if user_id:
        query = query.filter(models.VideoMetadata.user_id == user_id)
    
    # 전체 개수 계산
    total = query.count()
    
    # 2. [+ 추가] 최신순 정렬 및 페이지네이션 처리
    tasks = (
        query.order_by(models.VideoMetadata.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return {
        "total": total,
        "items": tasks,
        "limit": limit,
        "offset": offset
    }