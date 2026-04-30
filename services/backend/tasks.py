from __future__ import annotations

from datetime import datetime
from typing import Any


upload_tasks_db: dict[str, dict[str, Any]] = {}
audio_jobs_db: dict[str, dict[str, Any]] = {}


def _timestamp() -> str:
    return datetime.now().isoformat()


def create_upload_task(task_id: str) -> dict[str, Any]:
    task = {
        "task_id": task_id,
        "status": "PENDING",
        "verdict": None,
        "timestamp": _timestamp(),
    }
    upload_tasks_db[task_id] = task
    return task


def get_upload_task(task_id: str) -> dict[str, Any] | None:
    return upload_tasks_db.get(task_id)


def create_audio_job(task_id: str, file_path: str, artifacts_dir: str) -> dict[str, Any]:
    job = {
        "task_id": task_id,
        "status": "PENDING",
        "stage": "queued",
        "file_path": file_path,
        "audio_path": None,
        "video_path": None,
        "artifacts_dir": artifacts_dir,
        "result_path": None,
        "result": None,
        "error": None,
        "stdout": "",
        "stderr": "",
        "returncode": None,
        "created_at": _timestamp(),
        "started_at": None,
        "finished_at": None,
    }
    audio_jobs_db[task_id] = job
    return job


def get_audio_job(task_id: str) -> dict[str, Any] | None:
    return audio_jobs_db.get(task_id)


def update_audio_job(task_id: str, **fields: Any) -> dict[str, Any]:
    job = audio_jobs_db[task_id]
    job.update(fields)
    return job
