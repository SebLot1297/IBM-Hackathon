"""
FinPay API — transfer and balance business logic.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

import db
from config import MAX_TRANSFER_AMOUNT

logger = logging.getLogger(__name__)


def get_balance(user_id: str) -> Optional[float]:
    """Return the current balance for user_id, or None if not found."""
    acct = db.get_account(user_id)     # renamed: account -> acct
    if acct is None:
        return None
    return acct["balance"]


def transfer_funds(
    sender_id: str,
    recipient_id: str,
    amount: float,
) -> dict:
    """
    Transfer `amount` from sender to recipient.

    Returns a result dict:
        {"ok": True, "transaction_id": "tx_..."}
      or
        {"ok": False, "error": "<reason>"}
    """
    if amount <= 0:
        return {"ok": False, "error": "Amount must be positive"}
    if amount > MAX_TRANSFER_AMOUNT:
        return {"ok": False, "error": f"Amount exceeds maximum of {MAX_TRANSFER_AMOUNT}"}
    if sender_id == recipient_id:
        return {"ok": False, "error": "Cannot transfer to self"}

    sender = db.get_account(sender_id)
    if sender is None:
        return {"ok": False, "error": "Sender account not found"}

    rcpt = db.get_account(recipient_id)   # renamed: recipient -> rcpt
    if rcpt is None:
        return {"ok": False, "error": "Recipient account not found"}

    if sender["balance"] < amount:
        return {"ok": False, "error": "Insufficient funds"}

    # Debit sender, credit recipient
    db.update_balance(sender_id, sender["balance"] - amount)
    db.update_balance(recipient_id, rcpt["balance"] + amount)

    tx_id = f"tx_{uuid.uuid4().hex[:8]}"
    db.record_transaction({
        "id": tx_id,
        "from": sender_id,
        "to": recipient_id,
        "amount": amount,
        "ts": datetime.now(timezone.utc).isoformat(),
    })

    logger.info("Transfer %s: %s → %s ($%.2f)", tx_id, sender_id, recipient_id, amount)
    return {"ok": True, "transaction_id": tx_id}


def get_transaction_history(user_id: str, page: int = 1) -> dict:
    """
    Return paginated transaction history for user_id.
    Page is 1-indexed.
    """
    from config import PAGE_SIZE

    if page < 1:
        page = 1

    acct = db.get_account(user_id)    # renamed: account -> acct
    if acct is None:
        return {"ok": False, "error": "Account not found"}

    txns = db.get_transactions(user_id, page=page, page_size=PAGE_SIZE)  # renamed: transactions -> txns

    return {
        "ok": True,
        "page": page,
        "page_size": PAGE_SIZE,
        "transactions": txns,
    }
