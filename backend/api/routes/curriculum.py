"""Curriculum API - all pages approved by ISCS before return."""
from fastapi import APIRouter
from backend.core.interface_control.state_estimator import InterfaceStateEstimator
from backend.core.interface_control.stability_metric import compute_stability
from backend.core.interface_control.state_selector import select_ui_state

router = APIRouter()
estimator = InterfaceStateEstimator()


@router.get("/what-is-ai")
def what_is_ai() -> dict:
    telemetry = [0.2, 0.2, 0.3]
    _, cov = estimator.update(telemetry)
    stability = compute_stability(cov)

    pages = [
        {"id": "ai-1", "title": "What Is Artificial Intelligence?",
         "content": [
             "Artificial Intelligence (AI) means computers helping people think or decide.",
             "AI does not think like a human. It follows patterns.",
             "You already use AI in maps, phones, and search.",
         ], "complexity": 1},
        {"id": "ai-2", "title": "Examples You Already Know",
         "content": ["GPS directions", "Email spam filters", "Voice assistants"],
         "complexity": 2},
    ]
    approved = select_ui_state(pages, stability)
    return {"ui_state": approved, "stability": stability}
