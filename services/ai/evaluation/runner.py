from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from services.ai.evaluation.config import EvalConfig, REPO_ROOT
from services.ai.evaluation.manifest import ManifestSample, build_manifest, write_manifest_jsonl
from services.ai.evaluation.metrics import read_prediction_jsonl, write_metrics
from services.ai.evaluation.predictions import PredictionWriter, build_prediction_records


def _new_run_dir(output_root: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("run_%Y%m%d_%H%M%S")
    return output_root / f"{timestamp}_{uuid4().hex[:8]}"


def _run_video_pipeline(sample: ManifestSample, run_dir: Path) -> dict[str, Any]:
    from services.ai.pipelines.video_stage1.detect import run_video_stage1_detection
    from services.ai.pipelines.video_stage1.preprocess import run_video_stage1_preprocess

    storage_root = run_dir / "artifacts" / sample.sample_id / "video" / "jobs"
    run_video_stage1_preprocess(
        sample.video_path,
        job_id=sample.sample_id,
        storage_root=storage_root,
    )
    preprocessing_json_path = storage_root / sample.sample_id / "metadata" / "preprocessing.json"
    detection = run_video_stage1_detection(str(preprocessing_json_path))
    return detection


def _run_audio_pipeline(sample: ManifestSample, run_dir: Path) -> dict[str, Any]:
    from services.ai.audio_pipeline.audio_stage1 import run_audio_stage1

    output_dir = run_dir / "artifacts" / sample.sample_id / "audio"
    return run_audio_stage1(
        input_path=sample.audio_path,
        output_dir=output_dir,
        request_id=sample.sample_id,
    )


def _read_predictions(writer: PredictionWriter) -> dict[str, list[dict[str, Any]]]:
    required_fields = {"sample_id", "category", "label", "fake_score"}

    def complete_rows(path: Path) -> list[dict[str, Any]]:
        return [
            row
            for row in read_prediction_jsonl(path)
            if required_fields.issubset(row)
        ]

    return {
        "video": complete_rows(writer.paths.video_jsonl),
        "audio": complete_rows(writer.paths.audio_jsonl),
        "fusion": complete_rows(writer.paths.fusion_jsonl),
    }


def _resolve_run_dir(config: EvalConfig, run_dir: str | Path | None) -> Path:
    resolved = Path(run_dir).expanduser().resolve() if run_dir is not None else _new_run_dir(config.output_root)
    try:
        resolved.relative_to(REPO_ROOT)
    except ValueError:
        return resolved
    raise ValueError(f"Evaluation run_dir must be outside the repository: {REPO_ROOT}")


def run_dataset_evaluation(
    config: EvalConfig,
    limit: int | None = None,
    run_dir: str | Path | None = None,
) -> dict[str, Any]:
    resolved_run_dir = _resolve_run_dir(config, run_dir)
    resolved_run_dir.mkdir(parents=True, exist_ok=run_dir is not None)

    samples = build_manifest(dataset_root=config.dataset_root, metadata_csv=config.metadata_csv)
    if limit is not None:
        samples = samples[:limit]

    manifest_jsonl = write_manifest_jsonl(samples, resolved_run_dir / "manifest.jsonl")
    writer = PredictionWriter(resolved_run_dir)
    processed_sample_ids = writer.processed_sample_ids()

    for sample in samples:
        if sample.sample_id in processed_sample_ids:
            continue

        video_result: dict[str, Any] | None = None
        audio_result: dict[str, Any] | None = None
        if config.video_enabled:
            try:
                video_result = _run_video_pipeline(sample, resolved_run_dir)
            except Exception as exc:
                writer.write_failure(sample, modality="video", error=str(exc))
        if config.audio_enabled:
            try:
                audio_result = _run_audio_pipeline(sample, resolved_run_dir)
            except Exception as exc:
                writer.write_failure(sample, modality="audio", error=str(exc))

        records = build_prediction_records(
            sample,
            video_result=video_result,
            audio_result=audio_result,
        )
        if records.video is not None or records.audio is not None or records.fusion is not None:
            writer.write_records(records)

    expected_dataset_names = sorted({sample.type for sample in samples})
    metrics_paths = write_metrics(
        run_dir=resolved_run_dir,
        predictions_by_modality=_read_predictions(writer),
        expected_dataset_names=expected_dataset_names,
    )
    return {
        "run_dir": str(resolved_run_dir),
        "manifest_jsonl": str(manifest_jsonl),
        "predictions": writer.paths.to_dict(),
        "metrics": {dataset: str(path) for dataset, path in metrics_paths.items()},
    }
