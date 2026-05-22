from __future__ import annotations

import asyncio
import re
import uuid
from pathlib import Path

import instaloader
from sqlalchemy.orm import Session
from videohash import VideoHash

from services.backend import database, models
from services.backend.services.processor import separate_streams, TMP_DIR


def _extract_shortcode(url: str) -> str:
    """인스타그램 URL에서 shortcode 추출
    
    Args:
        url: 인스타그램 URL
        
    Returns:
        shortcode (post ID)
        
    Raises:
        ValueError: shortcode를 추출할 수 없을 때
    """
    match = re.search(r"/(?:p|reel)/([A-Za-z0-9_-]+)", url)
    if not match:
        raise ValueError("인스타그램 shortcode를 추출할 수 없습니다.")
    return match.group(1)


def _download_instagram(url: str, dest_dir: Path) -> None:
    """인스타그램 영상 다운로드
    
    Args:
        url: 인스타그램 URL
        dest_dir: 다운로드 저장 경로
        
    Raises:
        ValueError: shortcode 추출 실패 시
        instaloader.InstaloaderException: 다운로드 실패 시
    """
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


def _ensure_user_id(task: models.VideoMetadata) -> None:
    """사용자 ID 생성 (없을 경우)
    
    Args:
        task: 비디오 메타데이터 모델
    """
    if not task.user_id:
        task.user_id = str(uuid.uuid4())
        print(f"Generated new user_id: {task.user_id} for task: {task.task_id}")


def _verify_downloaded_files(dest_dir: Path) -> Path:
    """다운로드된 영상 파일 검증
    
    Args:
        dest_dir: 다운로드 디렉토리
        
    Returns:
        첫 번째 mp4 파일 경로
        
    Raises:
        FileNotFoundError: mp4 파일이 없을 때
    """
    video_files = list(dest_dir.glob("**/*.mp4"))
    if not video_files:
        raise FileNotFoundError("다운로드된 영상 파일을 찾을 수 없습니다.")
    return video_files[0]


async def _process_video_file(
    task_id: str,
    video_file: Path,
) -> tuple[str, str, str]:
    """영상 파일 처리 (스트림 분리, pHash 계산)
    
    Args:
        task_id: 작업 ID
        video_file: 영상 파일 경로
        
    Returns:
        (video_path, audio_path, phash_value) 튜플
    """
    # 영상과 음성 분리
    video_path, audio_path = separate_streams(video_file, task_id)
    
    # pHash 계산
    phash_value = await asyncio.to_thread(
        lambda: VideoHash(path=video_path).hash_hex
    )
    
    return video_path, audio_path, phash_value


def _update_task_success(
    task: models.VideoMetadata,
    video_path: str,
    audio_path: str,
    phash_value: str,
) -> None:
    """작업 완료 시 DB 업데이트
    
    Args:
        task: 비디오 메타데이터 모델
        video_path: 저장된 영상 경로
        audio_path: 저장된 음성 경로
        phash_value: pHash 값
    """
    task.storage_path = video_path
    task.audio_path = audio_path
    task.phash_value = phash_value
    task.status = "COMPLETED"


def _update_task_failure(task: models.VideoMetadata, error: str) -> None:
    """작업 실패 시 DB 업데이트
    
    Args:
        task: 비디오 메타데이터 모델
        error: 에러 메시지
    """
    task.status = "FAILED"
    print(f"Task {task.task_id} failed: {error}")


async def run_download(task_id: str, url: str) -> None:
    """인스타그램 영상 다운로드 및 처리
    
    Args:
        task_id: 작업 ID
        url: 인스타그램 URL
    """
    db = database.SessionLocal()
    
    try:
        # 1. DB에서 작업 조회
        task = db.query(models.VideoMetadata).filter(
            models.VideoMetadata.task_id == task_id
        ).first()
        
        if not task:
            print(f"Task {task_id} not found in database")
            return

        # 2. 사용자 ID 확보
        _ensure_user_id(task)

        # 3. 다운로드 디렉토리 준비
        dest_dir = TMP_DIR / task_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # 4. 상태 업데이트: PROCESSING
        task.status = "PROCESSING"
        task.download_dir = str(dest_dir)
        db.commit()

        # 5. 인스타그램 다운로드
        print(f"Starting download for task {task_id}...")
        await asyncio.to_thread(_download_instagram, url, dest_dir)

        # 6. 다운로드된 파일 검증
        video_file = _verify_downloaded_files(dest_dir)

        # 7. 영상 처리 (스트림 분리, pHash 계산)
        video_path, audio_path, phash_value = await _process_video_file(
            task_id,
            video_file,
        )

        # 8. 작업 완료
        _update_task_success(task, video_path, audio_path, phash_value)
        db.commit()

    except Exception as exc:
        # 에러 처리
        db.rollback()
        task = db.query(models.VideoMetadata).filter(
            models.VideoMetadata.task_id == task_id
        ).first()
        if task:
            _update_task_failure(task, str(exc))
            db.commit()
    
    finally:
        db.close()