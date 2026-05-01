from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.backend import database, crud

router = APIRouter()

@router.get("/user/{user_id}/fcm-token", summary="유저의 최신 FCM 토큰 조회")
async def read_user_fcm_token(user_id: str, db: Session = Depends(database.get_db)):
    token = crud.get_latest_fcm_token_by_user(db, user_id)
    
    if not token:
        raise HTTPException(status_code=404, detail="해당 유저의 FCM 토큰을 찾을 수 없습니다.")
    
    return {"user_id": user_id, "fcm_token": token}