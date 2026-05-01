from sqlalchemy.orm import Session
from services.backend import models

def get_latest_fcm_token_by_user(db: Session, user_id: str):
    """
    특정 유저의 가장 최신 FCM 토큰을 반환합니다.
    """
    result = db.query(models.VideoMetadata.fcm_token)\
        .filter(models.VideoMetadata.user_id == user_id)\
        .filter(models.VideoMetadata.fcm_token.isnot(None))\
        .order_by(models.VideoMetadata.created_at.desc())\
        .first()
    
    return result[0] if result else None