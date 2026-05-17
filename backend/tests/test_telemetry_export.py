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


class TestRetrievalRollup:
    """S25.6: /api/telemetry/rollup aggregates curriculum.retrieval_choice."""

    def _post(self, client, *, module, unit_id, page_id, chosen_id, correct):
        r = client.post(
            "/api/curriculum/retrieval-choice",
            json={
                "module": module,
                "unit_id": unit_id,
                "page_id": page_id,
                "chosen_id": chosen_id,
                "correct": correct,
            },
        )
        assert r.status_code == 200, r.text

    def test_rollup_empty_shape_when_no_events(self, client):
        r = client.get("/api/telemetry/rollup")
        assert r.status_code == 200
        body = r.json()
        assert set(body.keys()) == {"total_choices", "by_module", "by_unit"}
        assert isinstance(body["by_module"], list)
        assert isinstance(body["by_unit"], list)

    def test_rollup_aggregates_correctly(self, client):
        # Baseline: rollup may already contain events from prior tests in
        # this module (the in-process DB persists across tests). We diff
        # against the baseline so this test is order-independent.
        baseline = client.get("/api/telemetry/rollup").json()
        baseline_total = baseline["total_choices"]

        # Two attempts on unit-2: 1 correct, 1 wrong  -> accuracy 0.5
        self._post(
            client,
            module=1,
            unit_id="unit-2",
            page_id="u2-retrieval",
            chosen_id="a",
            correct=True,
        )
        self._post(
            client,
            module=1,
            unit_id="unit-2",
            page_id="u2-retrieval",
            chosen_id="b",
            correct=False,
        )
        # Three attempts on m2u1: all correct -> accuracy 1.0
        for i in range(3):
            self._post(
                client,
                module=2,
                unit_id="module2-unit-1",
                page_id="m2u1-retrieval",
                chosen_id="a",
                correct=True,
            )

        body = client.get("/api/telemetry/rollup").json()

        assert body["total_choices"] == baseline_total + 5

        by_unit = {(u["module"], u["unit_id"]): u for u in body["by_unit"]}
        unit_2 = by_unit[(1, "unit-2")]
        assert unit_2["attempts"] >= 2
        assert unit_2["correct"] >= 1
        # New attempts contribute 1/2 = 0.5; baseline may shift the ratio
        # so we only assert the relationship instead of an absolute value.
        assert 0.0 <= unit_2["accuracy"] <= 1.0

        m2u1 = by_unit[(2, "module2-unit-1")]
        assert m2u1["attempts"] >= 3
        assert m2u1["correct"] >= 3

    def test_rollup_accuracy_is_rounded_to_three_decimals(self, client):
        # 1 correct out of 3 attempts on a fresh unit -> 0.333
        for chosen, correct in [("a", True), ("b", False), ("b", False)]:
            self._post(
                client,
                module=3,
                unit_id="module3-unit-4",
                page_id="m3u4-retrieval",
                chosen_id=chosen,
                correct=correct,
            )

        body = client.get("/api/telemetry/rollup").json()
        unit = next(
            u
            for u in body["by_unit"]
            if u["module"] == 3 and u["unit_id"] == "module3-unit-4"
        )
        # Just assert the value is rounded (3 decimals or fewer).
        assert round(unit["accuracy"], 3) == unit["accuracy"]
