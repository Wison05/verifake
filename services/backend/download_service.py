from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from uuid import uuid4
from datetime import datetime
from pathlib import Path
import asyncio
import re
import instaloader

router = APIRouter()

TMP_DIR = Path("storage/tmp")
TMP_DIR.mkdir(parents=True, exist_ok=True)

tasks_db = {}


def _extract_shortcode(url: str) -> str:
    match = re.search(r'/(?:p|reel)/([A-Za-z0-9_-]+)', url)
    if not match:
        raise ValueError("인스타그램 shortcode를 추출할 수 없습니다.")
    return match.group(1)


def _download_instagram(url: str, dest_dir: Path):
    shortcode = _extract_shortcode(url)
    loader = instaloader.Instaloader(
        dirname_pattern=str(dest_dir),
        download_pictures=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern="",
    )
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    loader.download_post(post, target=shortcode)


async def _run_download(task_id: str, url: str):
    dest_dir = TMP_DIR / task_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    tasks_db[task_id]["status"] = "PROCESSING"
    try:
        await asyncio.to_thread(_download_instagram, url, dest_dir)
        tasks_db[task_id]["status"] = "DONE"
        tasks_db[task_id]["download_dir"] = str(dest_dir)
    except Exception as e:
        tasks_db[task_id]["status"] = "FAILED"
        tasks_db[task_id]["error"] = str(e)


@router.post("/share", summary="영상 업로드 및 수집", tags=["Upload"])
async def upload_video(
    background_tasks: BackgroundTasks,
    title: str = Form(..., description="영상 제목"),
    link: str = Form(None, description="인스타그램 영상 링크"),
    videoFile: UploadFile = File(None, description="직접 업로드할 영상 파일"),
):
    if not link and not videoFile:
        raise HTTPException(status_code=400, detail="링크 또는 파일 중 하나를 제공해야 합니다.")

    task_id = str(uuid4())

    if link:
        if "instagram.com" not in link:
            raise HTTPException(status_code=400, detail="유효한 인스타그램 링크가 아닙니다.")
        tasks_db[task_id] = {"status": "PENDING", "verdict": None, "title": title}
        background_tasks.add_task(_run_download, task_id, link)

    elif videoFile:
        dest_dir = TMP_DIR / task_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / videoFile.filename
        content = await videoFile.read()
        dest_path.write_bytes(content)
        tasks_db[task_id] = {
            "status": "DONE",
            "verdict": None,
            "title": title,
            "download_dir": str(dest_dir),
        }

    return {
        "task_id": task_id,
        "timestamp": datetime.now().isoformat(),
        "message": "수집 요청이 완료되었습니다.",
    }


@router.get("/status/{task_id}", summary="분석 상태 조회", tags=["Status"])
async def get_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="해당 task_id를 찾을 수 없습니다.")

    task = tasks_db[task_id]
    return {
        "task_id": task_id,
        "status": task["status"],
        "verdict": task["verdict"],
        "download_dir": task.get("download_dir"),
        "error": task.get("error"),
        "timestamp": datetime.now().isoformat(),
    }
