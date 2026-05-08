from __future__ import annotations

import json
from pathlib import Path

from services.ai.evaluation.metrics import compute_auc_roc, compute_metrics, write_metrics


def prediction(
    sample_id: str,
    label: int,
    score: float,
    category: str = "A",
    sample_type: str = "FakeVideo-FakeAudio",
) -> dict[str, object]:
    return {
        "sample_id": sample_id,
        "dataset_name": "FakeAVCeleb",
        "category": category,
        "type": sample_type,
        "modality": "video",
        "label": label,
        "fake_score": score,
    }


def test_compute_auc_roc_handles_ties() -> None:
    auc, reason = compute_auc_roc(
        labels=[0, 0, 0, 0, 1, 1],
        scores=[0.1, 0.2, 0.8, 0.8, 0.8, 0.9],
    )

    assert auc == 0.875
    assert reason is None


def test_compute_auc_roc_returns_null_reason_for_one_class() -> None:
    auc, reason = compute_auc_roc(labels=[1, 1], scores=[0.8, 0.9])

    assert auc is None
    assert reason == "auc_roc requires both positive and negative labels"


def test_compute_metrics_counts_accuracy_and_one_class_auc_reason() -> None:
    metrics = compute_metrics([prediction("a", 1, 0.7), prediction("b", 1, 0.2)])

    assert metrics["total_count"] == 2
    assert metrics["correct_count"] == 1
    assert metrics["accuracy"] == 0.5
    assert metrics["auc_roc"] is None
    assert metrics["auc_roc_reason"] == "auc_roc requires both positive and negative labels"


def test_write_metrics_saves_dataset_metrics_and_errors(tmp_path: Path) -> None:
    paths = write_metrics(
        run_dir=tmp_path,
        predictions_by_modality={
            "video": [
                prediction("tp", 1, 0.9),
                prediction("fp", 0, 0.8),
                prediction("fn", 1, 0.1),
                prediction("tn", 0, 0.2),
            ]
        },
    )

    metrics = json.loads(paths["FakeVideo-FakeAudio"].read_text(encoding="utf-8"))
    false_positive = (tmp_path / "errors" / "FakeVideo-FakeAudio_false_positive.jsonl").read_text(encoding="utf-8")
    false_negative = (tmp_path / "errors" / "FakeVideo-FakeAudio_false_negative.jsonl").read_text(encoding="utf-8")

    assert paths["FakeVideo-FakeAudio"].name == "FakeVideo-FakeAudio_metrics.json"
    assert metrics["dataset_name"] == "FakeVideo-FakeAudio"
    assert set(metrics["results"]) == {"video", "audio", "fusion"}
    assert metrics["results"]["video"]["accuracy"] == 0.5
    assert "auc_roc_reason" not in metrics["results"]["video"]
    assert metrics["results"]["audio"]["auc_roc"] is None
    assert metrics["results"]["audio"]["auc_roc_reason"] == "no predictions"
    assert '"sample_id": "fp"' in false_positive
    assert '"sample_id": "fn"' in false_negative


def test_write_metrics_creates_one_file_per_type_when_category_differs(tmp_path: Path) -> None:
    paths = write_metrics(
        run_dir=tmp_path,
        predictions_by_modality={
            "video": [
                prediction("fake-a", 1, 0.9, category="A", sample_type="FakeVideo-FakeAudio"),
                prediction("real-a", 0, 0.1, category="D", sample_type="RealVideo-RealAudio"),
            ],
            "audio": [prediction("fake-a", 1, 0.8, category="A", sample_type="FakeVideo-FakeAudio")],
            "fusion": [prediction("fake-a", 1, 0.85, category="A", sample_type="FakeVideo-FakeAudio")],
        },
    )

    assert {"FakeVideo-FakeAudio", "RealVideo-RealAudio"}.issubset(paths)
    fake_metrics = json.loads(paths["FakeVideo-FakeAudio"].read_text(encoding="utf-8"))
    real_metrics = json.loads(paths["RealVideo-RealAudio"].read_text(encoding="utf-8"))

    assert fake_metrics["dataset_name"] == "FakeVideo-FakeAudio"
    assert real_metrics["dataset_name"] == "RealVideo-RealAudio"
    assert fake_metrics["results"]["video"]["total_count"] == 1
    assert real_metrics["results"]["video"]["total_count"] == 1


def test_write_metrics_emits_expected_types_with_zero_counts(tmp_path: Path) -> None:
    paths = write_metrics(
        run_dir=tmp_path,
        predictions_by_modality={
            "video": [prediction("fake-a", 1, 0.9, category="A", sample_type="FakeVideo-FakeAudio")],
        },
        expected_dataset_names=["FakeVideo-FakeAudio", "FakeVideo-RealAudio"],
    )

    missing_metrics = json.loads(paths["FakeVideo-RealAudio"].read_text(encoding="utf-8"))
    assert missing_metrics["dataset_name"] == "FakeVideo-RealAudio"
    assert missing_metrics["results"]["video"] == {
        "total_count": 0,
        "correct_count": 0,
        "accuracy": None,
        "auc_roc": None,
        "auc_roc_reason": "no predictions",
    }
    assert missing_metrics["results"]["audio"]["total_count"] == 0
    assert missing_metrics["results"]["fusion"]["total_count"] == 0
