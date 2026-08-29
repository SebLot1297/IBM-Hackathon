"""
Tests for auth.py — token validation helpers.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'taskflow-api'))

import pytest
from unittest.mock import patch
import auth


# ─── validate_token ──────────────────────────────────────────────────────────

def test_validate_token_valid():
    user_id = auth.validate_token("tf_user_001_dev-secret-change-in-production")
    assert user_id == "user_001"


def test_validate_token_wrong_secret():
    user_id = auth.validate_token("tf_user_001_wrong-secret")
    assert user_id is None


def test_validate_token_malformed():
    assert auth.validate_token("not-a-token") is None
    assert auth.validate_token("") is None
    assert auth.validate_token("tf_only_two") is None


def test_validate_token_empty():
    assert auth.validate_token("") is None


# ─── require_auth ────────────────────────────────────────────────────────────

def test_require_auth_valid_token(app_context):
    with patch("auth.get_token_from_request", return_value="tf_user_001_dev-secret-change-in-production"):
        user_id = auth.require_auth()
        assert user_id == "user_001"


def test_require_auth_missing_token(app_context):
    with patch("auth.get_token_from_request", return_value=""):
        with pytest.raises(Exception):  # Flask abort(401)
            auth.require_auth()


def test_require_auth_invalid_token(app_context):
    with patch("auth.get_token_from_request", return_value="tf_user_001_bad-secret"):
        with pytest.raises(Exception):
            auth.require_auth()


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def app_context():
    """Provide a minimal Flask app context for abort() to work."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'taskflow-api'))
    from flask import Flask
    app = Flask(__name__)
    with app.app_context():
        with app.test_request_context():
            yield
