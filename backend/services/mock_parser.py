"""Shared mock-token parser.

Sprint '2nd Safe Yellow' P13: extracts common parsing logic from
auth_verifier._verify_mock and MockAuthProvider.verify_credential
to eliminate duplication while preserving each caller's error contract.
"""

from __future__ import annotations

import uuid
from typing import Optional

MOCK_NAMESPACE = uuid.UUID("00000000-0000-0000-0000-000000000001")
MOCK_PREFIX = "mock:"


def parse_mock_token(token: str) -> Optional[str]:
    """Extract email from a mock credential.

    Returns the validated email string, or None if the token is not a
    well-formed mock credential.
    """
    if not isinstance(token, str) or not token.startswith(MOCK_PREFIX):
        return None
    email = token[len(MOCK_PREFIX) :].strip().lower()
    if not email or "@" not in email:
        return None
    return email
