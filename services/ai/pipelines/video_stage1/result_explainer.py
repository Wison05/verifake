from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from services.ai.common.json_io import read_json, write_json
from services.ai.pipelines.video_stage1.exceptions import (
    Stage1ExplanationError,
    Stage1UnavailableError,
)

ENV_FILE_PATH = Path(__file__).resolve().parents[4] / ".env"
PROMPTS_DIR = Path(__file__).with_name("prompts")
SUMMARY_PROMPT_PATH = PROMPTS_DIR / "result_summary_prompt.txt"
DETAIL_PROMPT_PATH = PROMPTS_DIR / "result_detail_prompt.txt"
GEMINI_MODEL = "gemini-2.5-flash-lite"


def _load_prompt_template(path: Path) -> str:
    if not path.exists():
        raise Stage1ExplanationError(f"Prompt file not found: {path}")

    template = path.read_text(encoding="utf-8").strip()
    if "{{RESULT_JSON}}" not in template:
        raise Stage1ExplanationError(
            f"Prompt template must include {{RESULT_JSON}} placeholder: {path}"
        )
    return template


def _build_prompt(template: str, result_payload: dict[str, Any]) -> str:
    result_json = json.dumps(result_payload, ensure_ascii=False, indent=2)
    return template.replace("{{RESULT_JSON}}", result_json)


def _validate_result_payload(payload: dict[str, Any]) -> None:
    job_id = payload.get("job_id")
    status = payload.get("status")
    detection = payload.get("detection")

    if not isinstance(job_id, str) or not job_id:
        raise ValueError("result.json must include a non-empty string job_id.")
    if not isinstance(status, str) or not status:
        raise ValueError("result.json must include a non-empty string status.")
    if not isinstance(detection, dict):
        raise ValueError("result.json must include a detection object.")

    video_score = detection.get("video_score")
    if not isinstance(video_score, dict):
        raise ValueError("result.json must include detection.video_score.")

    for required_key in ("final_fake_score", "max_fake_score"):
        if required_key not in video_score:
            raise ValueError(
                f"result.json must include detection.video_score.{required_key}."
            )


def _load_dotenv_file() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise Stage1UnavailableError(
            "Stage1 result explanation requires python-dotenv for .env auto-loading. Install services/backend/requirements.txt before calling this pipeline."
        ) from exc

    load_dotenv(dotenv_path=ENV_FILE_PATH, override=False)


def _load_api_key() -> str:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key

    _load_dotenv_file()
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Stage1UnavailableError(
            "Gemini API key is missing. Set GOOGLE_API_KEY or GEMINI_API_KEY before calling the Stage1 result explainer."
        )
    return api_key


def _create_genai_client(api_key: str):
    try:
        from google import genai
    except ImportError as exc:
        raise Stage1UnavailableError(
            "Stage1 result explanation requires the google-genai package. Install services/backend/requirements.txt before calling this pipeline."
        ) from exc

    return genai.Client(api_key=api_key)


def _generate_text(client: Any, prompt: str) -> str:
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    text = getattr(response, "text", "")
    if not isinstance(text, str) or not text.strip():
        raise Stage1ExplanationError("Gemini response did not contain plain text output.")
    return text.strip()


def run_video_stage1_result_explainer(result_json_path: str) -> dict[str, Any]:
    result_path = Path(result_json_path)
    if not result_path.exists():
        raise FileNotFoundError(f"result.json file not found: {result_path}")
    if not result_path.is_file():
        raise ValueError(f"result.json path must point to a file: {result_path}")

    payload_obj = read_json(result_path)
    if not isinstance(payload_obj, dict):
        raise ValueError("result.json must contain a JSON object.")
    payload: dict[str, Any] = dict(payload_obj)
    _validate_result_payload(payload)

    prompt_source: dict[str, Any] = {
        str(key): value for key, value in payload.items() if key != "llm_explanations"
    }
    summary_prompt = _build_prompt(_load_prompt_template(SUMMARY_PROMPT_PATH), prompt_source)
    detail_prompt = _build_prompt(_load_prompt_template(DETAIL_PROMPT_PATH), prompt_source)

    api_key = _load_api_key()
    client = _create_genai_client(api_key)
    summary_text = _generate_text(client, summary_prompt)
    detail_text = _generate_text(client, detail_prompt)

    payload["llm_explanations"] = {
        "model": GEMINI_MODEL,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "summary_text": summary_text,
        "detail_text": detail_text,
    }

    write_json(result_path, payload)
    return payload
