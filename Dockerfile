FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
COPY services/backend /app/services/backend

EXPOSE 8000
CMD ["uvicorn", "services.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
