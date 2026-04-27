from __future__ import annotations

import json
from pathlib import Path

from services.ai.pipelines.video_stage1.detect import run_video_stage1_detection


def test_run_video_stage1_detection_writes_detection_and_result_files(
    tmp_path: Path,
) -> None:
    fixture_path = Path("tests/fixtures/video_stage1/preprocessing.mock.json")
    preprocessing = json.loads(fixture_path.read_text(encoding="utf-8"))

    job_root = tmp_path / "storage" / "jobs" / "mock_job_001"
    (job_root / "input").mkdir(parents=True)
    (job_root / "frames").mkdir(parents=True)
    (job_root / "faces").mkdir(parents=True)
    (job_root / "metadata").mkdir(parents=True)

    normalized_video_path = job_root / "input" / "normalized.mp4"
    normalized_video_path.write_bytes(b"video")

    for frame in preprocessing["frames"]:
        frame_path = job_root / "frames" / Path(frame["frame_path"]).name
        frame_path.write_bytes(b"frame")
        frame["frame_path"] = str(frame_path)
        for face in frame["faces"]:
            crop_path = job_root / "faces" / Path(face["crop_path"]).name
            crop_path.write_bytes(b"face")
            face["crop_path"] = str(crop_path)

    preprocessing["input"]["normalized_video_path"] = str(normalized_video_path)

    preprocessing_json_path = job_root / "metadata" / "preprocessing.json"
    preprocessing_json_path.write_text(
        json.dumps(preprocessing, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    result = run_video_stage1_detection(str(preprocessing_json_path))

    detection_json_path = job_root / "output" / "detection.json"
    result_json_path = job_root / "output" / "result.json"
    log_path = job_root / "logs" / "detection.log"

    assert result["job_id"] == "mock_job_001"
    assert detection_json_path.exists()
    assert result_json_path.exists()
    assert log_path.exists()

    detection = json.loads(detection_json_path.read_text(encoding="utf-8"))
    final_result = json.loads(result_json_path.read_text(encoding="utf-8"))

    assert detection["status"] == "success"
    assert detection["inference_summary"] == {
        "analyzed_face_crop_count": 2,
        "analyzed_frame_count": 2,
        "skipped_frame_count": 1,
        "inference_status": "success",
    }
    assert len(detection["face_scores"]) == 2
    assert len(detection["frame_scores"]) == 2
    assert detection["segment_scores"] == []
    assert detection["top_segments"] == []
    assert detection["video_score"]["final_fake_score"] == 0.5

    assert final_result["status"] == "success"
    assert final_result["detection"]["top_segments"] == []
    assert final_result["detection"]["video_score"]["final_fake_score"] == 0.5
