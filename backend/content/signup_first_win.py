################################################################################
# SIGN-UP -> FIRST SAFE WIN CONTENT - NONI
# GERAGOGY-GROUNDED, LOW-PRESSURE, OLDER-ADULT SAFE
#
# PURPOSE:
# - Support Golden Landing Flow Steps 4-6
# - Transition from exploration to first real value
# - Provide a calm, protected first interaction
#
# DESIGN INTENT (REFERENCE):
# - No urgency or coercion (Czaja et al.)
# - Full reversibility and control (Formosa, Carr)
# - Mental model first, action second (Norman)
# - Confidence through success, not instruction (Fisk)
#
# CONTENT ONLY - NO UI OR BEHAVIORAL LOGIC
# Per ADR 0006: landing-page content is stored separately from the
# Golden Flow step model. This module is pure data; the API layer
# converts it to a typed Pydantic response.
################################################################################

SIGNUP_FIRST_WIN_CONTENT = {
    "step_4_invitation": {
        "title": "You can try this without commitment",
        "body": (
            "If you’d like, you can take a small look at how learning with Noni works.\n\n"
            "You are not signing up for anything yet. Nothing will be sent, saved, "
            "or shared unless you later choose to continue."
        ),
        "options": [
            "Continue to a brief example",
            "Not right now",
        ],
        "note": "Both choices are perfectly fine. You remain in control.",
    },
    "step_5_guided_interaction": {
        "title": "Here is what working with Claude feels like",
        "body": (
            "Claude is an AI that responds to questions and ideas in conversation.\n\n"
            "Below is a simple example. You do not need to type anything yet. "
            "Just notice how the response is shown and explained."
        ),
        "guidance": (
            "Nothing happens automatically. This is only an example, "
            "and you are free to stop at any time."
        ),
    },
    "step_6_first_safe_win": {
        "title": "That’s the whole idea",
        "body": (
            "Using Noni means taking things one small step at a time.\n\n"
            "You see suggestions clearly. You decide what matters. "
            "There is no rush, and nothing is permanent."
        ),
        "reflection": (
            "If this felt manageable, that’s a good sign. "
            "Learning with Noni is meant to feel this way."
        ),
    },
    "optional_next_steps": {
        "title": "What would you like to do next?",
        "options": [
            "Keep exploring at my own pace",
            "Pause and come back later",
        ],
        "note": (
            "You don’t have to decide right now. "
            "You can take a break or return whenever you like."
        ),
    },
}
