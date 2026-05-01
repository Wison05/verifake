from __future__ import annotations

import unittest


class BackendTasksStoreTests(unittest.TestCase):
    def test_create_upload_task_initializes_pending_verdict_shape(self) -> None:
        from services.backend.tasks import create_upload_task, get_upload_task, upload_tasks_db

        upload_tasks_db.clear()
        task = create_upload_task("upload-1")

        self.assertEqual(task["status"], "PENDING")
        self.assertIsNone(task["verdict"])
        self.assertIs(get_upload_task("upload-1"), task)

    def test_create_audio_job_initializes_expected_fields(self) -> None:
        from services.backend.tasks import audio_jobs_db, create_audio_job, get_audio_job

        audio_jobs_db.clear()
        job = create_audio_job("audio-1", "C:/input.wav", "storage/jobs/audio-1/audio")

        self.assertEqual(job["task_id"], "audio-1")
        self.assertEqual(job["status"], "PENDING")
        self.assertEqual(job["file_path"], "C:/input.wav")
        self.assertEqual(job["artifacts_dir"], "storage/jobs/audio-1/audio")
        self.assertIsNone(job["result"])
        self.assertIsNone(job["error"])
        self.assertEqual(job["stdout"], "")
        self.assertEqual(job["stderr"], "")
        self.assertIsNone(job["returncode"])
        self.assertIs(get_audio_job("audio-1"), job)

    def test_update_audio_job_mutates_only_target_record(self) -> None:
        from services.backend.tasks import audio_jobs_db, create_audio_job, update_audio_job

        audio_jobs_db.clear()
        create_audio_job("audio-1", "C:/one.wav", "storage/jobs/audio-1/audio")
        create_audio_job("audio-2", "C:/two.wav", "storage/jobs/audio-2/audio")

        updated = update_audio_job("audio-2", status="SUCCEEDED", error="")

        self.assertEqual(updated["status"], "SUCCEEDED")
        self.assertEqual(audio_jobs_db["audio-1"]["status"], "PENDING")


if __name__ == "__main__":
    unittest.main()
