from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch


class ProcessorTests(unittest.TestCase):
    def test_separate_streams_runs_ffmpeg_with_timeout_and_capture(self) -> None:
        from services.backend.services.processor import AUDIO_DIR, VIDEO_DIR, MEDIA_SPLIT_TIMEOUT_SEC, separate_streams

        calls: list[tuple[list[str], dict[str, object]]] = []

        def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            calls.append((command, kwargs))
            return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

        with patch("services.backend.services.processor.subprocess.run", side_effect=fake_run):
            video_path, audio_path = separate_streams(Path("input.mp4"), "job-1")

        self.assertEqual(video_path, str(VIDEO_DIR / "job-1_video.mp4"))
        self.assertEqual(audio_path, str(AUDIO_DIR / "job-1_audio.wav"))
        self.assertEqual(len(calls), 2)
        for _, kwargs in calls:
            self.assertEqual(kwargs["check"], True)
            self.assertEqual(kwargs["capture_output"], True)
            self.assertEqual(kwargs["text"], True)
            self.assertEqual(kwargs["timeout"], MEDIA_SPLIT_TIMEOUT_SEC)


if __name__ == "__main__":
    unittest.main()
