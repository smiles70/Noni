"""Tests for the env-var feature flag system."""

import os

import pytest
from fastapi.testclient import TestClient

from backend.core.feature_flags import FeatureFlags


def test_feature_flags_enable_only_truthy_values() -> None:
    env = {
        "FEATURE_NEW_PAYWALL": "true",
        "FEATURE_B2B_ONBOARDING": "1",
        "_FEATURE_IGNORED": "true",
        "FEATURE_DISABLED_FLAG": "false",
        "FEATURE_EMPTY_FLAG": "",
    }
    flags = FeatureFlags(env)
    assert flags.is_enabled("new_paywall") is True
    assert flags.is_enabled("b2b_onboarding") is True
    assert flags.is_enabled("disabled_flag") is False
    assert flags.is_enabled("empty_flag") is False
    assert flags.is_enabled("unknown_flag") is False
    assert "_ignored" not in flags._flags
    assert sorted(flags.all_enabled()) == ["b2b_onboarding", "new_paywall"]


def test_feature_flags_case_insensitive() -> None:
    env = {"FEATURE_CANARY": "TRUE", "FEATURE_DARKLAUNCH": "Yes"}
    flags = FeatureFlags(env)
    assert flags.is_enabled("canary") is True
    assert flags.is_enabled("darklaunch") is True


def test_feature_flags_endpoint(client: TestClient) -> None:
    """The middleware must expose enabled flags on the public endpoint."""
    os.environ["FEATURE_TEST_ALPHA"] = "1"
    try:
        response = client.get("/api/v1/features")
        assert response.status_code == 200
        data = response.json()
        assert data["enabled"] == ["test_alpha"]
    finally:
        os.environ.pop("FEATURE_TEST_ALPHA", None)
