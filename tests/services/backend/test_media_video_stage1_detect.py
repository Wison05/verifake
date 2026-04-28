# pyright: reportMissingImports=false

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import HTTPException

from services.backend.routers import video


def test_video_stage1_detect_rejects_missing_preprocessing_json() -> None:
    with pytest.raises(HTTPException) as exc_info:
        video.detect_video_stage1(
            video.VideoStage1DetectRequest(
                preprocessing_json="/tmp/does-not-exist/preprocessing.json"
            )
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "preprocessing.json 파일이 존재하지 않습니다."


def test_video_stage1_detect_returns_result_paths(
    monkeypatch,
    tmp_path: Path,
) -> None:
    preprocessing_json = tmp_path / "storage" / "jobs" / "job_001" / "metadata" / "preprocessing.json"
    preprocessing_json.parent.mkdir(parents=True, exist_ok=True)
    preprocessing_json.write_text("{}", encoding="utf-8")

    def fake_run_video_stage1_detection(preprocessing_json_path: str) -> dict[str, str]:
        assert preprocessing_json_path == str(preprocessing_json)
        return {"job_id": "job_001"}

    monkeypatch.setattr(
        video,
        "run_video_stage1_detection",
        fake_run_video_stage1_detection,
    )

    response = video.detect_video_stage1(
        video.VideoStage1DetectRequest(
            preprocessing_json=str(preprocessing_json)
        )
    )

    assert response == {
        "job_id": "job_001",
        "status": "success",
        "detection_json": str(preprocessing_json.parent.parent / "output" / "detection.json"),
        "result_json": str(preprocessing_json.parent.parent / "output" / "result.json"),
    }
