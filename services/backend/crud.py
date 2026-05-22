from __future__ import annotations
from sqlalchemy.orm import Session
from services.backend import models
from services.backend.services.fcm_service import send_push_notification  # [+ 추가]

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

def update_user_fcm_token(db: Session, user_id: str, fcm_token: str) -> bool:     # [+ 추가]
    """특정 유저의 가장 최근 태스크 기록에 FCM 토큰을 갱신하거나 등록합니다."""               # [+ 추가]
    # 가장 최근에 생성된 해당 유저의 레코드를 가져옴                                # [+ 추가]
    last_task = (                                                                # [+ 추가]
        db.query(models.VideoMetadata)                                           # [+ 추가]
        .filter(models.VideoMetadata.user_id == user_id)                         # [+ 추가]
        .order_by(models.VideoMetadata.created_at.desc())                        # [+ 추가]
        .first()                                                                 # [+ 추가]
    )                                                                            # [+ 추가]
    if last_task:                                                                # [+ 추가]
        last_task.fcm_token = fcm_token                                          # [+ 추가]
        db.commit()                                                              # [+ 추가]
        return True                                                              # [+ 추가]
    return False                                                                 # [+ 추가]

# 🟥 분석 완료 시 푸시 알림 발송 로직 연동 및 수정
def update_task_analysis(
    db: Session, 
    task_id: str, 
    verdict: str, 
    deepfake_score: float, 
    status: str = "DONE"
) -> models.VideoMetadata | None:
    """분석 완료 시 판정 결과 및 스코어를 저장하고, 해당 유저에게 푸시 알림을 발송합니다."""
    task = get_task_by_id(db, task_id)
    if task:
        task.verdict = verdict
        task.deepfake_score = deepfake_score
        task.status = status
        db.commit()
        db.refresh(task)

        # 🟥 [실제 연동 부분] 해당 task에 등록된 fcm_token이 있다면 알림 발송 시작  # [+ 추가]
        if task.fcm_token:                                                       # [+ 추가]
            title = "영상 분석 완료 🔍"                                           # [+ 추가]
            body = f"요청하신 영상의 분석이 완료되었습니다. 판정: {verdict}"           # [+ 추가]
            data = {                                                             # [+ 추가]
                "task_id": task.task_id,                                         # [+ 추가]
                "verdict": verdict,                                              # [+ 추가]
                "deepfake_score": str(deepfake_score)                            # [+ 추가]
            }                                                                    # [+ 추가]
            # FCM 푸시 서비스 호출                                                # [+ 추가]
            send_push_notification(                                              # [+ 추가]
                fcm_token=task.fcm_token,                                        # [+ 추가]
                title=title,                                                     # [+ bandwidth 추가]
                body=body,                                                       # [+ 추가]
                data=data                                                        # [+ 추가]
            )                                                                    # [+ 추가]
            
    return task