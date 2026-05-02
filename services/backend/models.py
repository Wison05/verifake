from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from services.backend.database import Base
import uuid

class VideoMetadata(Base):
    __tablename__ = "video_metadata"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(36), unique=True, index=True)
    
    origin_url = Column(Text, nullable=True)
    download_dir = Column(Text, nullable=True)     # 1. 원본 다운로드 경로
    storage_path = Column(Text, nullable=True)     # 2. 분리된 영상 경로
    audio_path = Column(Text, nullable=True)       # 3. 분리된 음성 경로

    user_id = Column(String(50), index=True)
    fcm_token = Column(String(255), nullable=True)
    phash_value = Column(String(64), nullable=True)
    status = Column(String(20), default="PENDING")
    created_at = Column(DateTime, server_default=func.now())