"""
FinPay API — Flask application entry point.
"""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request, abort
import auth
import payments
import db
from config import APP_VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


# ─── Health ──────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": APP_VERSION})


# ─── Balance ─────────────────────────────────────────────────────────────────

@app.route("/api/balance", methods=["GET"])
def get_balance():
    user_id = auth.require_auth()
    balance = payments.get_balance(user_id)
    if balance is None:
        abort(404, description="Account not found")
    return jsonify({"user_id": user_id, "balance": balance})


# ─── Transfer ────────────────────────────────────────────────────────────────

@app.route("/api/transfer", methods=["POST"])
def transfer():
    # Parse request body
    body = request.get_json(force=True, silent=True) or {}
    recipient_id = body.get("recipient_id", "")
    amount = body.get("amount", 0)

    if not recipient_id:
        abort(400, description="recipient_id is required")
    if not isinstance(amount, (int, float)) or amount <= 0:
        abort(400, description="amount must be a positive number")

    # Identify caller from token
    user_id = auth.require_auth()

    result = payments.transfer_funds(user_id, recipient_id, float(amount))

    if not result["ok"]:
        abort(400, description=result["error"])

    return jsonify(result), 201


# ─── Transaction History ─────────────────────────────────────────────────────

@app.route("/api/transactions", methods=["GET"])
def transactions():
    user_id = auth.require_auth()
    page = int(request.args.get("page", 1))
    result = payments.get_transaction_history(user_id, page=page)
    return jsonify(result)


# ─── User Dashboard ──────────────────────────────────────────────────────────

@app.route("/api/dashboard", methods=["GET"])
def dashboard():
    """Return a combined summary for the authenticated user's dashboard."""
    current_user = auth.require_auth()

    balance = payments.get_balance(current_user)
    if balance is None:
        abort(404, description="Account not found")

    # Fetch recent transactions (first page)
    history = payments.get_transaction_history(current_user, page=1)
    recent_txs = history.get("transactions", [])

    # Summarise sent vs received
    total_sent = sum(
        tx["amount"] for tx in recent_txs if tx["from"] == current_user
    )
    total_received = sum(
        tx["amount"] for tx in recent_txs if tx["to"] == current_user
    )

    return jsonify({
        "user_id": current_user,
        "balance": balance,
        "recent_transactions": recent_txs,
        "summary": {
            "total_sent": round(total_sent, 2),
            "total_received": round(total_received, 2),
        },
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
