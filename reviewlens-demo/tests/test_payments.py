"""
Tests for payments.py — transfer and balance logic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'finpay-api'))

import pytest
import db
import payments


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_db():
    """Reset in-memory DB to a known state before each test."""
    db._accounts = {
        "user_001": {"id": "user_001", "name": "Alice Chen", "balance": 5000.00},
        "user_002": {"id": "user_002", "name": "Bob Marsh", "balance": 1200.50},
        "user_003": {"id": "user_003", "name": "Carol Diaz", "balance": 800.00},
    }
    db._transactions = []
    yield


# ─── get_balance ─────────────────────────────────────────────────────────────

def test_get_balance_existing_user():
    assert payments.get_balance("user_001") == 5000.00


def test_get_balance_unknown_user():
    assert payments.get_balance("user_999") is None


# ─── transfer_funds ──────────────────────────────────────────────────────────

def test_transfer_happy_path():
    result = payments.transfer_funds("user_001", "user_002", 100.00)
    assert result["ok"] is True
    assert "transaction_id" in result
    assert payments.get_balance("user_001") == 4900.00
    assert payments.get_balance("user_002") == 1300.50


def test_transfer_insufficient_funds():
    result = payments.transfer_funds("user_003", "user_001", 9999.00)
    assert result["ok"] is False
    assert "Insufficient" in result["error"]


def test_transfer_negative_amount():
    result = payments.transfer_funds("user_001", "user_002", -50.00)
    assert result["ok"] is False


def test_transfer_zero_amount():
    result = payments.transfer_funds("user_001", "user_002", 0)
    assert result["ok"] is False


def test_transfer_exceeds_maximum():
    result = payments.transfer_funds("user_001", "user_002", 99999.00)
    assert result["ok"] is False
    assert "maximum" in result["error"]


def test_transfer_to_self():
    result = payments.transfer_funds("user_001", "user_001", 100.00)
    assert result["ok"] is False
    assert "self" in result["error"]


def test_transfer_unknown_sender():
    result = payments.transfer_funds("user_999", "user_001", 100.00)
    assert result["ok"] is False


def test_transfer_unknown_recipient():
    result = payments.transfer_funds("user_001", "user_999", 100.00)
    assert result["ok"] is False


def test_transfer_records_transaction():
    payments.transfer_funds("user_001", "user_002", 50.00)
    assert len(db._transactions) == 1
    tx = db._transactions[0]
    assert tx["from"] == "user_001"
    assert tx["to"] == "user_002"
    assert tx["amount"] == 50.00


# ─── get_transaction_history ─────────────────────────────────────────────────

def test_transaction_history_empty():
    result = payments.get_transaction_history("user_001")
    assert result["ok"] is True
    assert result["transactions"] == []


def test_transaction_history_pagination():
    # Insert 25 transactions for user_001
    for i in range(25):
        db.record_transaction({
            "id": f"tx_{i:04d}",
            "from": "user_001",
            "to": "user_002",
            "amount": 1.00,
            "ts": "2024-01-01T00:00:00Z",
        })
    page1 = payments.get_transaction_history("user_001", page=1)
    page2 = payments.get_transaction_history("user_001", page=2)
    assert len(page1["transactions"]) == 20
    assert len(page2["transactions"]) == 5


def test_transaction_history_unknown_user():
    result = payments.get_transaction_history("user_999")
    assert result["ok"] is False
