# pyright: reportMissingImports=false

from __future__ import annotations

from fastapi.testclient import TestClient

from services.backend.main import app


client = TestClient(app)


def test_main_exposes_only_media_collection_routes_not_ai_runtime_routes() -> None:
    route_paths = {
        path
        for route in app.routes
        if (path := getattr(route, "path", None)) is not None
    }

    assert "/api/v1/instagram" in route_paths
    assert "/api/v1/video" in route_paths
    assert "/api/v1/status/{task_id}" in route_paths

    assert "/api/v1/video-stage1/preprocess" not in route_paths
    assert "/api/v1/video-stage1/detect" not in route_paths
    assert "/api/v1/video-stage1/detect/jobs" not in route_paths
    assert "/api/v1/audio/jobs" not in route_paths
    assert "/api/v1/audio/jobs/{task_id}" not in route_paths
    assert "/api/v1/audio/jobs/{task_id}/result" not in route_paths
    assert "/media/video-stage1/preprocess" not in route_paths
    assert "/media/video-stage1/detect" not in route_paths
    assert "/media/instagram" not in route_paths
    assert "/media/video" not in route_paths
    assert "/media/status/{task_id}" not in route_paths


def test_ai_runtime_routes_are_not_exposed() -> None:
    assert client.post("/api/v1/video-stage1/preprocess").status_code == 404
    assert client.post("/api/v1/video-stage1/detect").status_code == 404
    assert client.post("/api/v1/video-stage1/detect/jobs").status_code == 404
    assert client.post("/api/v1/audio/jobs").status_code == 404
    assert client.post("/media/instagram").status_code == 404
    assert client.post("/media/video").status_code == 404
    assert client.get("/media/status/some-id").status_code == 404
