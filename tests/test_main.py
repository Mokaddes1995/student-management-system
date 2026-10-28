import logging
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():

    response = client.get("/")

    assert response.status_code == 200

    assert response.json()["status"] == "running"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "database": "connected",
    }


def test_health_endpoint_database_unavailable(client):
    with patch(
        "app.main.engine.connect",
        side_effect=Exception("Database connection failed"),
    ):
        response = client.get("/health")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert response.json() == {
        "detail": "Database unavailable",
    }


def test_request_logging(client, caplog):
    with caplog.at_level(logging.INFO, logger="app.main"):
        response = client.get("/health")

    assert response.status_code == 200

    records = [
        record
        for record in caplog.records
        if record.name == "app.main" and getattr(record, "event", None) == "request_completed"
    ]

    assert records, "Request completion log was not recorded"

    record = records[-1]

    assert record.getMessage() == "Request completed"
    assert record.method == "GET"
    assert record.path == "/health"
    assert record.status_code == 200
    assert isinstance(record.duration_ms, (int, float))
    assert record.request_id


def test_request_id_header(client):
    response = client.get("/health")

    request_id = response.headers.get("X-Request-ID")

    assert response.status_code == 200
    assert request_id is not None
    assert len(request_id) == 36


def test_app_debug_matches_settings():
    from app.core.config import settings
    from app.main import app

    assert app.debug is settings.debug
