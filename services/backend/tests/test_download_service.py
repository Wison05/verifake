from __future__ import annotations

import unittest


class DownloadServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        from services.backend.routers.instagram import tasks_db

        tasks_db.clear()

    async def test_receive_instagram_rejects_non_instagram_link(self) -> None:
        from fastapi import BackgroundTasks
        from fastapi import HTTPException

        from services.backend.routers.instagram import receive_instagram

        with self.assertRaises(HTTPException) as context:
            await receive_instagram(
                background_tasks=BackgroundTasks(),
                title="sample",
                link="https://example.com/video",
            )

        self.assertEqual(context.exception.status_code, 400)

    async def test_get_status_returns_existing_upload_shape(self) -> None:
        from services.backend.routers.instagram import get_status, tasks_db

        tasks_db["upload-1"] = {"status": "PENDING", "verdict": None, "title": "sample"}
        result = await get_status("upload-1")

        self.assertEqual(result["task_id"], "upload-1")
        self.assertEqual(result["status"], "PENDING")
        self.assertIn("timestamp", result)
        self.assertIn("verdict", result)

    async def test_get_status_raises_for_missing_upload_task(self) -> None:
        from fastapi import HTTPException

        from services.backend.routers.instagram import get_status

        with self.assertRaises(HTTPException) as context:
            await get_status("missing")

        self.assertEqual(context.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
