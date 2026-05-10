from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, TypedDict

JobStatus = Literal["PENDING", "ANALYZING", "SUCCEEDED", "FAILED", "TIMED_OUT"]


class UploadTask(TypedDict):
    task_id: str
    status: JobStatus
    verdict: str | None
    timestamp: str


class AudioJob(TypedDict):
    task_id: str
    status: JobStatus
    stage: str
    file_path: str
    audio_path: str | None
    video_path: str | None
    artifacts_dir: str
    result_path: str | None
    result: Any
    error: str | None
    stdout: str
    stderr: str
    returncode: int | None
    created_at: str
    started_at: str | None
    finished_at: str | None


_upload_tasks: dict[str, UploadTask] = {}
_audio_jobs: dict[str, AudioJob] = {}


def _now() -> str:
    return datetime.now().isoformat()


def create_upload_task(task_id: str) -> UploadTask:
    task: UploadTask = {
        "task_id": task_id,
        "status": "PENDING",
        "verdict": None,
        "timestamp": _now(),
    }
    _upload_tasks[task_id] = task
    return task


def get_upload_task(task_id: str) -> UploadTask | None:
    return _upload_tasks.get(task_id)


def create_audio_job(task_id: str, file_path: str, artifacts_dir: str) -> AudioJob:
    job: AudioJob = {
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
        "created_at": _now(),
        "started_at": None,
        "finished_at": None,
    }
    _audio_jobs[task_id] = job
    return job


def get_audio_job(task_id: str) -> AudioJob | None:
    return _audio_jobs.get(task_id)


def update_audio_job(task_id: str, **fields: Any) -> AudioJob:
    job = _audio_jobs.get(task_id)
    if job is None:
        raise KeyError(f"audio job not found: {task_id}")
    job.update(fields)  # type: ignore[typeddict-item]
    return job


def clear_stores() -> None:
    """테스트 격리용"""
    _upload_tasks.clear()
    _audio_jobs.clear()
