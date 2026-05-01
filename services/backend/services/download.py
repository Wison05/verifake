import asyncio
import re
import instaloader
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from services.backend.services.processor import separate_streams, TMP_DIR
from services.backend import models
from videohash import VideoHash
from services.backend import database

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


async def run_download(task_id: str, url: str):
    # [변경] 외부에서 db를 받지 않고, 함수 내부에서 세션을 새로 생성합니다.
    # 이렇게 해야 백그라운드에서 세션이 끊기지 않고 끝까지 유지됩니다.
    db = database.SessionLocal() 
    
    try:
        task = db.query(models.VideoMetadata).filter(models.VideoMetadata.task_id == task_id).first()
        if not task:
            print(f"Task {task_id} not found in database")
            return

        if not task.user_id: # 이미 존재하지 않는 경우에만 생성
            task.user_id = str(uuid.uuid4())
            print(f"Generated new user_id: {task.user_id} for task: {task_id}")
            

        dest_dir = TMP_DIR / task_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. 상태 업데이트 및 저장
        task.status = "PROCESSING"
        task.download_dir = str(dest_dir)
        db.commit()

        # 2. 인스타그램 다운로드 실행
        print(f"Starting download for task {task_id}...")
        await asyncio.to_thread(_download_instagram, url, dest_dir)

        video_files = list(dest_dir.glob("**/*.mp4"))
        if not video_files:
            raise FileNotFoundError("다운로드된 영상 파일을 찾을 수 없습니다.")

        # 3. 영상과 음성 분리 실행
        video_path, audio_path = separate_streams(video_files[0], task_id)
        
        # 4. pHash 분석
        v_hash = await asyncio.to_thread(lambda: VideoHash(path=video_path).hash_hex)
        
        # 5. 결과 기록
        task.storage_path = str(video_path)
        task.audio_path = str(audio_path)
        task.phash_value = v_hash
        task.status = "COMPLETED"

    except Exception as e:
        # 에러 발생 시 처리
        db.rollback() # 에러 시 롤백 추가
        task = db.query(models.VideoMetadata).filter(models.VideoMetadata.task_id == task_id).first()
        if task:
            task.status = "FAILED"
        print(f"Task {task_id} failed: {str(e)}")
        
    finally:
        db.commit()
        db.close()