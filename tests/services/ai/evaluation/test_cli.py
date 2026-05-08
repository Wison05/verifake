from __future__ import annotations

import json
from pathlib import Path

from services.ai.evaluation import dataset_eval
from services.ai.evaluation.config import EvalConfig


def test_cli_main_loads_config_runs_evaluation_and_prints_json(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    config_path = tmp_path / "eval.ini"
    output_root = tmp_path / "out"
    captured: dict[str, object] = {}

    def fake_load_eval_config(config_path_arg: Path, output_root_override: Path | None = None) -> EvalConfig:
        captured["config_path"] = config_path_arg
        captured["override"] = output_root_override
        return EvalConfig(
            dataset_root=tmp_path / "dataset",
            metadata_csv=tmp_path / "dataset" / "meta_data.csv",
            output_root=output_root,
            video_enabled=True,
            audio_enabled=False,
        )

    run_dir = output_root / "existing-run"

    def fake_run_dataset_evaluation(
        config: EvalConfig,
        limit: int | None = None,
        run_dir: Path | None = None,
    ) -> dict[str, object]:
        captured["limit"] = limit
        captured["run_dir"] = run_dir
        assert run_dir is not None
        return {
            "run_dir": str(run_dir),
            "manifest_jsonl": str(run_dir / "manifest.jsonl"),
            "predictions": {"video_jsonl": str(output_root / "run" / "predictions_video.jsonl")},
            "metrics": {"FakeAVCeleb": str(output_root / "run" / "metrics" / "FakeAVCeleb_metrics.json")},
        }

    monkeypatch.setattr(dataset_eval, "load_eval_config", fake_load_eval_config)
    monkeypatch.setattr(dataset_eval, "run_dataset_evaluation", fake_run_dataset_evaluation)

    exit_code = dataset_eval.main(
        [
            "--config",
            str(config_path),
            "--output-root",
            str(output_root),
            "--limit",
            "7",
            "--run-dir",
            str(run_dir),
        ]
    )

    printed = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert captured == {"config_path": config_path, "override": output_root, "limit": 7, "run_dir": run_dir}
    assert printed["run_dir"].endswith("existing-run")
