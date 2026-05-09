"""Sprint 13 contract: Sign-up -> First Safe Win content (Golden Flow Steps 4-6)."""

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.content.signup_first_win import SIGNUP_FIRST_WIN_CONTENT
from backend.models.signup_first_win import SignupFirstWinContent

client = TestClient(app)


def test_content_module_validates_against_schema():
    SignupFirstWinContent(**SIGNUP_FIRST_WIN_CONTENT)


def test_first_win_endpoint_returns_200_and_full_shape():
    res = client.get("/api/landing/first-win")
    assert res.status_code == 200
    body = res.json()
    for key in (
        "step_4_invitation",
        "step_5_guided_interaction",
        "step_6_first_safe_win",
        "optional_next_steps",
    ):
        assert key in body


def test_first_win_no_empty_strings_anywhere():
    res = client.get("/api/landing/first-win")
    body = res.json()

    def assert_non_empty(value, path: str) -> None:
        if isinstance(value, str):
            assert value.strip(), f"empty string at {path}"
        elif isinstance(value, list):
            assert value, f"empty list at {path}"
            for i, item in enumerate(value):
                assert_non_empty(item, f"{path}[{i}]")
        elif isinstance(value, dict):
            for k, v in value.items():
                assert_non_empty(v, f"{path}.{k}")

    assert_non_empty(body, "$")


def test_first_win_offers_reversible_choices():
    res = client.get("/api/landing/first-win")
    body = res.json()
    invite_options = body["step_4_invitation"]["options"]
    assert any(
        "not right now" in o.lower() or "later" in o.lower() for o in invite_options
    ), "invitation step must include a no-pressure exit option"
    next_options = body["optional_next_steps"]["options"]
    assert any(
        "pause" in o.lower() or "later" in o.lower() for o in next_options
    ), "optional next steps must include a pause / come-back-later option"


def test_first_win_contains_no_urgency_language():
    res = client.get("/api/landing/first-win")
    text = res.text.lower()
    forbidden = ["hurry", "urgent", "limited time", "act now", "expires", "only today"]
    for word in forbidden:
        assert word not in text, f"urgency phrase {word!r} found"
