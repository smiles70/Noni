"""Tests for /api/telemetry/export and /api/telemetry/export.csv."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


class TestTelemetryExport:
    def test_export_json_shape(self, client):
        r = client.get("/api/telemetry/export")
        assert r.status_code == 200
        body = r.json()
        assert "count" in body and "events" in body
        assert isinstance(body["events"], list)
        assert body["count"] == len(body["events"])

    def test_export_csv_returns_csv_content_type(self, client):
        r = client.get("/api/telemetry/export.csv")
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]
        # Always at least a header row.
        text = r.text
        assert text.split("\n")[0].strip(), "CSV must have a header row"

    def test_csv_row_count_matches_json_count(self, client):
        json_count = client.get("/api/telemetry/export").json()["count"]
        csv_text = client.get("/api/telemetry/export.csv").text
        non_empty = [line for line in csv_text.splitlines() if line.strip()]
        # Header + N rows
        assert len(non_empty) == json_count + 1
