from __future__ import annotations

import argparse
import json
from pathlib import Path

from services.ai.evaluation.config import load_eval_config
from services.ai.evaluation.runner import run_dataset_evaluation


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run FakeAVCeleb dataset evaluation")
    parser.add_argument("--config", required=True, help="Evaluation INI config path")
    parser.add_argument("--output-root", default=None, help="Override output root")
    parser.add_argument("--limit", type=int, default=None, help="Optional sample limit")
    parser.add_argument("--run-dir", default=None, help="Existing external run directory for resume")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    config_path = Path(args.config)
    output_root = Path(args.output_root) if args.output_root else None
    run_dir = Path(args.run_dir) if args.run_dir else None
    config = load_eval_config(config_path, output_root_override=output_root)
    result = run_dataset_evaluation(config, limit=args.limit, run_dir=run_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
