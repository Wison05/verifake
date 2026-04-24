from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from uuid import uuid4
from datetime import datetime
import instaloader

router = APIRouter()

# 분석 상태 임시저장 딕셔너리 (DB로 교체 예정)
tasks_db = {}

#API 그룹화 요약
@router.post("/share", summary="영상 업로드 및 수집", tags=["Upload"])
async def upload_video(
    title: str = Form(..., description="영상 제목"),
    link: str = Form(None, description="인스타그램 영상 링크"),
    videoFile: UploadFile = File(None, description="직접 업로드할 영상 파일")
):
    task_id = str(uuid4())
    
    # instaloader 피드백 반영: 링크가 있을 경우 수집 프로세스 기록
    if link:
        if "instagram.com" not in link:
            raise HTTPException(status_code=400, detail="유효한 인스타그램 링크가 아닙니다.")
        # 실제 다운로드 로직은 별도 비동기 태스크로 분리 권장 (현재는 뼈대만 반영)
        print(f"[System] instaloader를 통해 {link} 수집 시작")

    tasks_db[task_id] = {"status": "PENDING", "verdict": None}

    return {
        "task_id": task_id,
        "timestamp": datetime.now().isoformat(),
        "message": "수집 요청이 완료되었습니다."
    }

@router.get("/status/{task_id}", summary="분석 상태 조회", tags=["Status"])
async def get_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="해당 task_id를 찾을 수 없습니다.")

    return {
        "task_id": task_id,
        "status": tasks_db[task_id]["status"],
        "verdict": tasks_db[task_id]["verdict"],
        "timestamp": datetime.now().isoformat()
    }
