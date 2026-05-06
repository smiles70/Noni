"""NLU - intent proposals only. System never acts without confirmation."""
def interpret_text(command: str) -> dict:
    cmd = command.lower()
    if "add" in cmd:
        return {"intent": "ADD_REQUEST", "confidence": 0.9}
    if "delete" in cmd:
        return {"intent": "REMOVE_REQUEST", "confidence": 0.9}
    return {"intent": "UNKNOWN", "confidence": 0.5}
