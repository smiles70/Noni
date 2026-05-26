"""Runtime schema for Clerk Backend API user profile responses.

Validates the JSON shape returned by GET /v1/users/{user_id}
so that unexpected field drift from Clerk is caught at parse time
rather than surfacing as a downstream None/email-missing failure.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class _EmailAddress(BaseModel):
    id: str
    email_address: str
    verification: Optional[dict] = None


class ClerkUserProfile(BaseModel):
    """Clerk Backend API user object (minimal fields we depend on)."""

    id: str
    primary_email_address_id: Optional[str] = Field(default=None)
    email_addresses: list[_EmailAddress] = Field(default_factory=list)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)

    @property
    def primary_email(self) -> Optional[str]:
        """Return the email matching primary_email_address_id, or first verified fallback."""
        for entry in self.email_addresses:
            if entry.id == self.primary_email_address_id:
                return entry.email_address.strip().lower()
        for entry in self.email_addresses:
            return entry.email_address.strip().lower()
        return None

    @property
    def display_name(self) -> Optional[str]:
        """Join first + last name if both present."""
        parts = [p for p in (self.first_name, self.last_name) if p]
        return " ".join(parts) if parts else None
