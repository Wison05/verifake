from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


ONE_CLASS_AUC_REASON = "auc_roc requires both positive and negative labels"


def compute_auc_roc(labels: list[int], scores: list[float]) -> tuple[float | None, str | None]:
    positives = sum(1 for label in labels if label == 1)
    negatives = sum(1 for label in labels if label == 0)
    if positives == 0 or negatives == 0:
        return None, ONE_CLASS_AUC_REASON
    if len(labels) != len(scores):
        raise ValueError("labels and scores must have the same length")

    ranked = sorted(enumerate(scores), key=lambda item: item[1])
    ranks = [0.0] * len(scores)
    index = 0
    while index < len(ranked):
        tie_end = index + 1
        while tie_end < len(ranked) and ranked[tie_end][1] == ranked[index][1]:
            tie_end += 1
        average_rank = (index + 1 + tie_end) / 2.0
        for rank_index in range(index, tie_end):
            original_index = ranked[rank_index][0]
            ranks[original_index] = average_rank
        index = tie_end

    positive_rank_sum = sum(rank for rank, label in zip(ranks, labels) if label == 1)
    auc = (positive_rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)
    return float(auc), None


def compute_metrics(records: Iterable[dict[str, Any]], threshold: float = 0.5) -> dict[str, Any]:
    rows = list(records)
    labels = [int(row["label"]) for row in rows]
    scores = [float(row["fake_score"]) for row in rows]
    predicted = [1 if score >= threshold else 0 for score in scores]
    correct_count = sum(1 for expected, actual in zip(labels, predicted) if expected == actual)
    auc, auc_reason = compute_auc_roc(labels, scores) if rows else (None, "no predictions")
    total_count = len(rows)
    result: dict[str, Any] = {
        "total_count": total_count,
        "correct_count": correct_count,
        "accuracy": correct_count / total_count if total_count else None,
        "auc_roc": auc,
    }
    if auc_reason is not None:
        result["auc_roc_reason"] = auc_reason
    return result


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as jsonl_file:
        jsonl_file.write(json.dumps(row, ensure_ascii=False) + "\n")


def _error_rows(records: list[dict[str, Any]], threshold: float) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    false_positives: list[dict[str, Any]] = []
    false_negatives: list[dict[str, Any]] = []
    for row in records:
        predicted_label = 1 if float(row["fake_score"]) >= threshold else 0
        enriched = dict(row)
        enriched["predicted_label"] = predicted_label
        if int(row["label"]) == 0 and predicted_label == 1:
            false_positives.append(enriched)
        if int(row["label"]) == 1 and predicted_label == 0:
            false_negatives.append(enriched)
    return false_positives, false_negatives


def write_metrics(
    *,
    run_dir: str | Path,
    predictions_by_modality: dict[str, list[dict[str, Any]]],
    threshold: float = 0.5,
    expected_dataset_names: Iterable[str] | None = None,
) -> dict[str, Path]:
    root = Path(run_dir)
    metrics_dir = root / "metrics"
    errors_dir = root / "errors"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    errors_dir.mkdir(parents=True, exist_ok=True)

    grouped: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for modality, records in predictions_by_modality.items():
        for record in records:
            grouped[str(record.get("type") or record.get("category") or record["dataset_name"])][modality].append(record)

    if expected_dataset_names is not None:
        for dataset_name in expected_dataset_names:
            grouped[str(dataset_name)]

    output_paths: dict[str, Path] = {}
    for category_name, modality_records in grouped.items():
        payload: dict[str, Any] = {
            "dataset_name": category_name,
            "results": {},
        }
        false_positive_path = errors_dir / f"{category_name}_false_positive.jsonl"
        false_negative_path = errors_dir / f"{category_name}_false_negative.jsonl"
        false_positive_path.write_text("", encoding="utf-8")
        false_negative_path.write_text("", encoding="utf-8")

        for modality in ("video", "audio", "fusion"):
            records = modality_records.get(modality, [])
            payload["results"][modality] = compute_metrics(records, threshold=threshold)

            false_positives, false_negatives = _error_rows(records, threshold)
            for row in false_positives:
                _append_jsonl(false_positive_path, row)
            for row in false_negatives:
                _append_jsonl(false_negative_path, row)

        output_path = metrics_dir / f"{category_name}_metrics.json"
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        output_paths[category_name] = output_path
    return output_paths


def read_prediction_jsonl(path: str | Path) -> list[dict[str, Any]]:
    prediction_path = Path(path)
    if not prediction_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with prediction_path.open("r", encoding="utf-8") as jsonl_file:
        for line in jsonl_file:
            if line.strip():
                rows.append(json.loads(line))
    return rows
