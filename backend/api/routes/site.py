"""Site-chrome API — backend-served footer content.

Single endpoint: `/footer` returns the shared footer copy (nav row,
legal row, landing mini-strip) so every surface renders identical
labels. Pure read; no auth. See `.ai/intake/2026-09-16-p2-*`.
"""

from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.content.site_chrome import SITE_FOOTER_CONTENT
from backend.models.site_chrome import SiteFooterContent

router = APIRouter()


@router.get("/footer", response_model=SiteFooterContent)
def get_footer() -> JSONResponse:
    """Return the shared footer copy with the current copyright year."""
    payload = dict(SITE_FOOTER_CONTENT)
    payload["copyright"] = (
        f"© {datetime.now(timezone.utc).year} mynaani. All rights reserved."
    )
    content = SiteFooterContent.model_validate(payload)
    resp = JSONResponse(content=content.model_dump())
    resp.headers["Cache-Control"] = "public, max-age=300"
    return resp
