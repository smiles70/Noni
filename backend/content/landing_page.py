"""Landing page copy (verbatim, locked for Sprint 5).

Design intent:
- Plain language (CDC, NIH)
- Anxiety reduction (Czaja et al.)
- Dignity and agency (Formosa, Carr)
- Trust and predictability (Norman, Fisk)
"""

from typing import Any, Dict

LANDING_PAGE_CONTENT: Dict[str, Any] = {
    "hero": {
        "headline": "A calm way to understand and use AI",
        "subheadline": (
            "Noni helps you learn what AI is, how Claude works, "
            "and how to use it confidently - without pressure or confusion."
        ),
    },
    "introduction": {
        "title": "Designed for learning at your own pace",
        "body": (
            "Many people feel unsure about new technology, especially AI. "
            "That is normal.\n\n"
            "Noni was created to make learning AI feel steady, respectful, "
            "and manageable. Nothing happens too fast, and nothing changes "
            "without clear guidance. You stay in control at every step."
        ),
    },
    "what_noni_does": {
        "title": "What Noni helps you do",
        "items": [
            "Understand what AI is and what it is not",
            "Learn how Claude can help with everyday thinking and tasks",
            "Use AI safely, without giving up your judgment",
            "Build confidence through simple, guided steps",
        ],
    },
    "how_it_feels": {
        "title": "What it feels like to use Noni",
        "items": [
            "Clear explanations in plain language",
            "No tests, grades, or time pressure",
            "Nothing is permanent - you can pause or stop at any time",
            "Support that respects your experience and decisions",
        ],
    },
    "trust_and_safety": {
        "title": "Your comfort and control come first",
        "body": (
            "Noni does not rush you and does not act on its own. "
            "AI suggestions are always shown for review, and you decide "
            "what to use or ignore.\n\n"
            "You never have to share personal information to learn, "
            "and you can step away at any time."
        ),
    },
    "call_to_action": {
        "primary": {
            "label": "Begin calmly",
            "note": "You can explore without commitment. Nothing will be sent or shared.",
        },
        "secondary": {
            "label": "Learn how it works",
            "note": "See what to expect before starting.",
        },
    },
    "closing": {
        "body": (
            "Learning something new should feel steady, not stressful.\n\n"
            "Noni is here to support you - at your pace, on your terms."
        ),
    },
}
