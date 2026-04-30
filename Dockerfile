# 1. 베이스 이미지 설정
FROM ubuntu:latest

# 2. 환경변수 설정 (파이썬 출력 및 AI 런타임용)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TF_USE_LEGACY_KERAS=1

# 3. 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    curl \
    vim \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 4. 작업 디렉토리 설정
WORKDIR /app

# 5. 의존성 파일 복사 및 설치 (AI 런타임 포함)
# 호스트의 requirements 파일들을 임시 복사하여 설치합니다.
COPY services/backend/requirements.txt /tmp/requirements.txt
COPY services/backend/requirements-ai-stage1.txt /tmp/requirements-ai-stage1.txt

# --break-system-packages 옵션을 사용하여 시스템 파이썬에 직접 설치
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt --break-system-packages && \
    pip install --no-cache-dir -r /tmp/requirements-ai-stage1.txt --break-system-packages

# 6. 소스 코드 복사 (Docker Compose에서 볼륨 마운트를 쓰더라도 빌드 시 복사해두는 것이 좋습니다)
COPY . .

# 7. 포트 개방
EXPOSE 8000

# 8. 실행 명령어 (Docker Compose의 command가 없을 때 기본값으로 사용됨)
CMD ["uvicorn", "services.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]