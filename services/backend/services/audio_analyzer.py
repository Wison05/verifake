from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

from services.backend.tasks import get_audio_job, update_audio_job


AUDIO_STAGE1_TIMEOUT_SEC = 30 * 60
RESULT_FILENAME = "audio_stage1_result.json"
LOG_LIMIT_CHARS = 16000
DEFAULT_AI_DEVICE = "cpu"


def _truncate_log(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        text = value.decode("utf-8", errors="replace")
    else:
        text = value
    return text[-LOG_LIMIT_CHARS:]


def get_audio_python() -> Path:
    raw_path = os.getenv("VERIFAKE_AI_PYTHON")
    if not raw_path:
        raise RuntimeError("VERIFAKE_AI_PYTHON 환경변수가 설정되지 않았습니다.")

    python_path = Path(raw_path).expanduser().resolve()
    if not python_path.exists():
        raise RuntimeError(f"VERIFAKE_AI_PYTHON 경로가 존재하지 않습니다: {python_path}")
    if not python_path.is_file():
        raise RuntimeError(f"VERIFAKE_AI_PYTHON 경로가 실행 파일이 아닙니다: {python_path}")
    if not os.access(python_path, os.X_OK):
        raise RuntimeError(f"VERIFAKE_AI_PYTHON 실행 권한이 없습니다: {python_path}")

    return python_path


def validate_audio_python() -> Path:
    return get_audio_python()


def get_audio_device() -> str:
    return os.getenv("VERIFAKE_AI_DEVICE", DEFAULT_AI_DEVICE).strip() or DEFAULT_AI_DEVICE


def build_audio_stage1_command(
    *,
    python_executable: Path,
    input_path: Path,
    output_dir: Path,
    job_id: str,
    device: str,
) -> list[str]:
    command = [
        str(python_executable),
        "-m",
        "services.ai.audio_pipeline.audio_stage1",
        "--input",
        str(input_path),
        "--output-dir",
        str(output_dir),
        "--request-id",
        job_id,
        "--json-output",
        str(output_dir / RESULT_FILENAME),
    ]
    if device:
        command.extend(["--device", device])
    return command


def run_audio_job(job_id: str, input_path: Path) -> None:
    started_at = datetime.now().isoformat()
    try:
        python_executable = get_audio_python()
        device = get_audio_device()
        output_dir = Path("storage/jobs") / job_id / "audio"
        output_dir.mkdir(parents=True, exist_ok=True)
        result_path = output_dir / RESULT_FILENAME

        update_audio_job(
            job_id,
            status="ANALYZING",
            stage="audio_stage1",
            audio_path=str(input_path.resolve()),
            artifacts_dir=str(output_dir),
            result_path=str(result_path),
            started_at=started_at,
        )

        command = build_audio_stage1_command(
            python_executable=python_executable,
            input_path=input_path.resolve(),
            output_dir=output_dir,
            job_id=job_id,
            device=device,
        )

        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=AUDIO_STAGE1_TIMEOUT_SEC,
            cwd=Path(__file__).resolve().parents[3],
        )

        stdout = _truncate_log(completed.stdout)
        stderr = _truncate_log(completed.stderr)

        if completed.returncode != 0:
            update_audio_job(
                job_id,
                status="FAILED",
                stage="audio_stage1",
                stdout=stdout,
                stderr=stderr,
                returncode=completed.returncode,
                error=stderr or f"audio_stage1 subprocess failed with return code {completed.returncode}",
                finished_at=datetime.now().isoformat(),
            )
            return

        if not result_path.exists():
            update_audio_job(
                job_id,
                status="FAILED",
                stage="audio_stage1",
                stdout=stdout,
                stderr=stderr,
                returncode=completed.returncode,
                error=f"audio_stage1 결과 파일이 생성되지 않았습니다: {result_path}",
                finished_at=datetime.now().isoformat(),
            )
            return

        try:
            result_payload = json.loads(result_path.read_text(encoding="utf-8"))
        except Exception:
            update_audio_job(
                job_id,
                status="FAILED",
                stage="audio_stage1",
                stdout=stdout,
                stderr=stderr,
                returncode=completed.returncode,
                error=f"audio_stage1 결과 파일을 읽을 수 없습니다: {result_path}",
                finished_at=datetime.now().isoformat(),
            )
            return

        update_audio_job(
            job_id,
            status="SUCCEEDED",
            stage="audio_stage1",
            stdout=stdout,
            stderr=stderr,
            returncode=completed.returncode,
            result=result_payload,
            finished_at=datetime.now().isoformat(),
        )
    except subprocess.TimeoutExpired as exc:
        update_audio_job(
            job_id,
            status="TIMED_OUT",
            stage="audio_stage1",
            stdout=_truncate_log(exc.stdout),
            stderr=_truncate_log(exc.stderr),
            error=f"audio_stage1 subprocess timeout after {AUDIO_STAGE1_TIMEOUT_SEC} seconds",
            finished_at=datetime.now().isoformat(),
        )
    except Exception as exc:
        existing_job = get_audio_job(job_id) or {}
        update_audio_job(
            job_id,
            status="FAILED",
            stage=existing_job.get("stage", "audio_stage1"),
            error=str(exc),
            finished_at=datetime.now().isoformat(),
        )
