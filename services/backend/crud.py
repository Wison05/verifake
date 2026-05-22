from __future__ import annotations

from sqlalchemy.orm import Session

from services.backend import models


def get_latest_fcm_token_by_user(db: Session, user_id: str) -> str | None:
    """특정 유저의 가장 최신 FCM 토큰을 반환합니다."""
    row = (
        db.query(models.VideoMetadata.fcm_token)
        .filter(
            models.VideoMetadata.user_id == user_id,
            models.VideoMetadata.fcm_token.isnot(None),
        )
        .order_by(models.VideoMetadata.created_at.desc())
        .first()
    )
    return row[0] if row else None


def get_task_by_id(db: Session, task_id: str) -> models.VideoMetadata | None:
    return (
        db.query(models.VideoMetadata)
        .filter(models.VideoMetadata.task_id == task_id)
        .first()
    )

def update_task_analysis(
    db: Session, 
    task_id: str, 
    verdict: str, 
    deepfake_score: float, 
    status: str = "DONE"
) -> models.VideoMetadata | None:
    """분석 완료 시 판정 결과 및 스코어를 저장합니다."""
    task = get_task_by_id(db, task_id)
    if task:
        task.verdict = verdict
        task.deepfake_score = deepfake_score
        task.status = status
        db.commit()
        db.refresh(task)
    return task
