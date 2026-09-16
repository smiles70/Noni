"""Site chrome copy — footer navigation and legal row.

Backend-served so footer labels/links stay consistent across the
landing mini-strip and the fat footer on marketing surfaces, and can
be updated without a frontend deploy. Plain language per the geragogy
contract; links point only to routes that exist.
"""

from typing import Any, Dict

SITE_FOOTER_CONTENT: Dict[str, Any] = {
    "tagline": "mynaani — AI learning for adults 55+",
    "nav_links": [
        {"label": "For learners", "href": "/"},
        {"label": "For caregivers", "href": "/caregiver"},
        {"label": "Be our partner", "href": "/partners"},
        {"label": "Gift", "href": "/gift"},
        {"label": "About us", "href": "/about"},
        {"label": "Help", "href": "/help"},
    ],
    "legal_links": [
        {"label": "Privacy", "href": "/privacy"},
        {"label": "Terms", "href": "/terms"},
    ],
    "social_links": [
        {
            "label": "Instagram",
            "href": "https://www.instagram.com/mynaani_learning",
        },
        {"label": "TikTok", "href": "https://www.tiktok.com/@mynaani_learning"},
        {"label": "YouTube", "href": "https://www.youtube.com/@mynaani"},
        {"label": "Facebook", "href": "https://www.facebook.com/mynaani"},
    ],
    # Minimal set for the fixed-viewport landing strip.
    "mini_links": [
        {"label": "Privacy", "href": "/privacy"},
        {"label": "Terms", "href": "/terms"},
        {"label": "Help", "href": "/help"},
    ],
    "brand_label": "mynaani",
}
