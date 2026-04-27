from __future__ import annotations

from services.ai.inference.video_stage1.deepfakebench_efficientnet_b4 import (
    predict_face_crops,
)


def test_predict_face_crops_returns_empty_list_for_empty_input() -> None:
    assert predict_face_crops([]) == []


def test_predict_face_crops_returns_mock_scores_with_original_metadata() -> None:
    face_items = [
        {
            "face_id": "face_000001_00",
            "frame_index": 1,
            "timestamp_sec": 0.333,
            "crop_path": "storage/jobs/mock_job_001/faces/frame_000001_face_00.jpg",
        }
    ]

    result = predict_face_crops(face_items)

    assert result == [
        {
            "face_id": "face_000001_00",
            "frame_index": 1,
            "timestamp_sec": 0.333,
            "crop_path": "storage/jobs/mock_job_001/faces/frame_000001_face_00.jpg",
            "raw_fake_score": 0.5,
            "inference_success": True,
        }
    ]
