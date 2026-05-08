from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from services.ai.evaluation.manifest import ManifestSample


@dataclass(frozen=True)
class PredictionPaths:
    video_jsonl: Path
    audio_jsonl: Path
    fusion_jsonl: Path
    combined_jsonl: Path
    combined_csv: Path
    failed_jsonl: Path

    def to_dict(self) -> dict[str, str]:
        return {key: str(value) for key, value in asdict(self).items()}


@dataclass(frozen=True)
class PredictionRecords:
    video: dict[str, Any] | None
    audio: dict[str, Any] | None
    fusion: dict[str, Any] | None
    combined: dict[str, Any]


def _nested_get(payload: Mapping[str, Any], keys: tuple[str, ...]) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    return current


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    return float(value)


def extract_video_fake_score(video_result: Mapping[str, Any] | None) -> float | None:
    if video_result is None:
        return None
    nested_score = _float_or_none(
        _nested_get(video_result, ("detection", "video_score", "final_fake_score"))
    )
    if nested_score is not None:
        return nested_score
    return _float_or_none(_nested_get(video_result, ("video_score", "final_fake_score")))


def extract_audio_fake_score(audio_result: Mapping[str, Any] | None) -> float | None:
    if audio_result is None:
        return None
    preferred = _float_or_none(audio_result.get("audio_fake_score"))
    if preferred is not None:
        return preferred
    return _float_or_none(audio_result.get("audio_fake_prob_like"))


def _base_record(sample: ManifestSample, modality: str, label: int, fake_score: float) -> dict[str, Any]:
    return {
        "sample_id": sample.sample_id,
        "dataset_name": sample.dataset_name,
        "category": sample.category,
        "type": sample.type,
        "label_name": sample.label_name,
        "split": sample.split,
        "filename": sample.filename,
        "video_path": sample.video_path,
        "audio_path": sample.audio_path,
        "modality": modality,
        "label": int(label),
        "fake_score": float(fake_score),
    }


def build_prediction_records(
    sample: ManifestSample,
    *,
    video_result: Mapping[str, Any] | None = None,
    audio_result: Mapping[str, Any] | None = None,
) -> PredictionRecords:
    video_score = extract_video_fake_score(video_result)
    audio_score = extract_audio_fake_score(audio_result)

    video = (
        _base_record(sample, "video", sample.labels["video_label"], video_score)
        if video_score is not None
        else None
    )
    audio = (
        _base_record(sample, "audio", sample.labels["audio_label"], audio_score)
        if audio_score is not None
        else None
    )
    fusion_score = None
    if video_score is not None and audio_score is not None:
        fusion_score = (video_score + audio_score) / 2.0
    fusion = (
        _base_record(sample, "fusion", sample.labels["fusion_label"], fusion_score)
        if fusion_score is not None
        else None
    )
    combined = {
        "sample_id": sample.sample_id,
        "dataset_name": sample.dataset_name,
        "category": sample.category,
        "type": sample.type,
        "label_name": sample.label_name,
        "split": sample.split,
        "filename": sample.filename,
        "video_path": sample.video_path,
        "audio_path": sample.audio_path,
        "video_label": sample.labels["video_label"],
        "audio_label": sample.labels["audio_label"],
        "fusion_label": sample.labels["fusion_label"],
        "video_fake_score": video_score,
        "audio_fake_score": audio_score,
        "fusion_fake_score": fusion_score,
    }
    return PredictionRecords(video=video, audio=audio, fusion=fusion, combined=combined)


def load_existing_sample_ids(paths: Iterable[str | Path]) -> set[str]:
    sample_ids: set[str] = set()
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as jsonl_file:
            for line in jsonl_file:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSONL row in {path}: {line.strip()}") from exc
                sample_id = row.get("sample_id")
                if sample_id:
                    sample_ids.add(str(sample_id))
    return sample_ids


class PredictionWriter:
    def __init__(self, run_dir: str | Path) -> None:
        root = Path(run_dir)
        root.mkdir(parents=True, exist_ok=True)
        self.paths = PredictionPaths(
            video_jsonl=root / "predictions_video.jsonl",
            audio_jsonl=root / "predictions_audio.jsonl",
            fusion_jsonl=root / "predictions_fusion.jsonl",
            combined_jsonl=root / "predictions_combined.jsonl",
            combined_csv=root / "predictions_combined.csv",
            failed_jsonl=root / "failed_cases.jsonl",
        )

    def processed_sample_ids(self) -> set[str]:
        return load_existing_sample_ids([self.paths.combined_jsonl])

    def write_records(self, records: PredictionRecords) -> None:
        if records.video is not None:
            self._append_jsonl(self.paths.video_jsonl, records.video)
        if records.audio is not None:
            self._append_jsonl(self.paths.audio_jsonl, records.audio)
        if records.fusion is not None:
            self._append_jsonl(self.paths.fusion_jsonl, records.fusion)
        self._append_jsonl(self.paths.combined_jsonl, records.combined)
        self._append_csv(records.combined)

    def write_failure(self, sample: ManifestSample, *, modality: str, error: str) -> None:
        self._append_jsonl(
            self.paths.failed_jsonl,
            {
                "sample_id": sample.sample_id,
                "dataset_name": sample.dataset_name,
                "category": sample.category,
                "modality": modality,
                "filename": sample.filename,
                "video_path": sample.video_path,
                "audio_path": sample.audio_path,
                "error": error,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    @staticmethod
    def _append_jsonl(path: Path, row: Mapping[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as jsonl_file:
            jsonl_file.write(json.dumps(dict(row), ensure_ascii=False) + "\n")

    def _append_csv(self, row: Mapping[str, Any]) -> None:
        self.paths.combined_csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(row.keys())
        should_write_header = not self.paths.combined_csv.exists() or self.paths.combined_csv.stat().st_size == 0
        with self.paths.combined_csv.open("a", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            if should_write_header:
                writer.writeheader()
            writer.writerow(dict(row))
