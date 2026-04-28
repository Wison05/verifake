# pyright: reportMissingImports=false

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import pytest


pytest.importorskip("fastapi")

from fastapi import FastAPI
from fastapi.testclient import TestClient


video = importlib.import_module("services.backend.routers.video")
exceptions = importlib.import_module("services.ai.pipelines.video_stage1.exceptions")


app_under_test = FastAPI()
app_under_test.include_router(video.router, prefix="/api/v1")
client = TestClient(app_under_test)


def test_video_stage1_preprocess_returns_400_for_missing_file() -> None:
    response = client.post(
        "/api/v1/video-stage1/preprocess",
        json={"file_path": "missing-file.mp4"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "파일이 존재하지 않습니다."


def test_video_stage1_preprocess_returns_summary_payload(
    tmp_path: Path,
    monkeypatch,
) -> None:
    input_path = tmp_path / "sample.mov"
    input_path.write_bytes(b"data")

    def fake_run_video_stage1_preprocess_job(
        input_file: Path,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        assert input_file == input_path
        return {
            "job_id": job_id or "job_test_003",
            "status": "success",
        }

    monkeypatch.setattr(video, "run_video_stage1_preprocess_job", fake_run_video_stage1_preprocess_job)

    response = client.post(
        "/api/v1/video-stage1/preprocess",
        json={"file_path": str(input_path), "job_id": "job_test_003"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "job_id": "job_test_003",
        "status": "success",
        "preprocessing_json": "storage/jobs/job_test_003/metadata/preprocessing.json",
    }


def test_video_stage1_preprocess_returns_500_for_missing_ai_runtime(
    tmp_path: Path,
    monkeypatch,
) -> None:
    input_path = tmp_path / "sample.mov"
    input_path.write_bytes(b"data")

    def fake_run_video_stage1_preprocess_job(
        input_file: Path,
        job_id: str | None = None,
    ) -> dict[str, Any]:
        raise exceptions.Stage1UnavailableError("missing ai runtime")

    monkeypatch.setattr(video, "run_video_stage1_preprocess_job", fake_run_video_stage1_preprocess_job)

    response = client.post(
        "/api/v1/video-stage1/preprocess",
        json={"file_path": str(input_path), "job_id": "job_test_004"},
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "missing ai runtime",
    }
