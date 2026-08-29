"""
FinPay API — thin in-memory database abstraction.
In production this would use SQLAlchemy + PostgreSQL.
"""

from typing import Optional


# Simulated in-memory store for demo purposes
_accounts: dict[str, dict] = {
    "user_001": {"id": "user_001", "name": "Alice Chen", "balance": 5000.00},
    "user_002": {"id": "user_002", "name": "Bob Marsh", "balance": 1200.50},
    "user_003": {"id": "user_003", "name": "Carol Diaz", "balance": 800.00},
    "user_004": {"id": "user_004", "name": "Dan Park", "balance": 9900.00},
    "user_005": {"id": "user_005", "name": "Eve Stone", "balance": 300.75},
}

_transactions: list[dict] = [
    {"id": "tx_001", "from": "user_001", "to": "user_002", "amount": 200.00, "ts": "2024-01-10T10:00:00Z"},
    {"id": "tx_002", "from": "user_003", "to": "user_001", "amount": 50.00, "ts": "2024-01-11T09:15:00Z"},
    {"id": "tx_003", "from": "user_002", "to": "user_004", "amount": 500.00, "ts": "2024-01-12T14:30:00Z"},
]


def get_account(user_id: str) -> Optional[dict]:
    """Return account dict for user_id, or None if not found."""
    return _accounts.get(user_id)


def update_balance(user_id: str, new_balance: float) -> bool:
    """Update account balance. Returns False if account not found."""
    if user_id not in _accounts:
        return False
    _accounts[user_id]["balance"] = round(new_balance, 2)
    return True


def record_transaction(tx: dict) -> None:
    """Append a transaction to the ledger."""
    _transactions.append(tx)


def get_transactions(user_id: str, page: int = 1, page_size: int = 20) -> list[dict]:
    """
    Return a paginated list of transactions involving user_id.
    Pages are 1-indexed.
    """
    user_txs = [
        tx for tx in _transactions
        if tx["from"] == user_id or tx["to"] == user_id
    ]
    # Calculate page slice
    start = page * page_size          # BUG: should be (page - 1) * page_size
    end = start + page_size
    return user_txs[start:end]
