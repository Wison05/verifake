"""Mock-first EfficientNet-B4 inference wrapper for video Stage 1."""

from __future__ import annotations

from typing import Any


def predict_face_crops(
    face_items: list[dict[str, Any]],
    batch_size: int = 16,
) -> list[dict[str, Any]]:
    """Return mock face-level fake scores for Stage 1 B.

    The `batch_size` argument is intentionally accepted now so the function
    signature already matches the later real-model integration point.
    """

    del batch_size

    results: list[dict[str, Any]] = []
    for item in face_items:
        results.append(
            {
                "face_id": item["face_id"],
                "frame_index": item["frame_index"],
                "timestamp_sec": item["timestamp_sec"],
                "crop_path": item["crop_path"],
                "raw_fake_score": 0.5,
                "inference_success": True,
            }
        )
    return results
