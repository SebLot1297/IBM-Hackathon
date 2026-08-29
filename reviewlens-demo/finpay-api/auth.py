"""
FinPay API — session/token validation helpers.

Tokens are simple Bearer strings in this demo.
Format: "fp_<user_id>_<secret>"
Example: "fp_user_001_dev-secret-change-in-production"
"""

import logging
from typing import Optional
from flask import request, abort
from config import SECRET_KEY

logger = logging.getLogger(__name__)


def _parse_token(token: str) -> tuple[str, str]:
    """Split a FinPay token into (user_id, secret) parts."""
    parts = token.split("_", 2)
    if len(parts) != 3 or parts[0] != "fp":
        return "", ""
    return parts[1], parts[2]


def get_token_from_request() -> str:
    """Extract Bearer token from Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return ""
    return auth_header[len("Bearer "):]


def validate_token(token: str) -> Optional[str]:
    """
    Validate a FinPay token.
    Returns the authenticated user_id on success, or None on failure.
    """
    if not token:
        return None
    user_id, secret = _parse_token(token)
    if not user_id:
        logger.warning("Malformed token: %s...", token[:8])
        return None
    if secret != SECRET_KEY:
        logger.warning("Invalid secret for user %s (token: %s...)", user_id, token[:8])
        return None
    logger.info("Authenticated user: %s", user_id)
    return user_id


def require_auth() -> str:
    """
    Enforce authentication on the current request.
    Returns the authenticated user_id.
    Aborts with 401 if the token is missing or invalid.
    """
    token = get_token_from_request()
    user_id = validate_token(token)
    if user_id is None:
        abort(401, description="Authentication required")
    return user_id
