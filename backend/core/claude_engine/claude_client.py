"""Claude - previewable, user-confirmable, undoable proposals. Mocked."""
def request_claude(prompt: str) -> dict:
    return {
        "proposed_text": f"Claude suggests: {prompt}",
        "requires_confirmation": True,
    }
