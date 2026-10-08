"""/api/bola/1 - OWASP API1:2023, Broken Object Level Authorization. The
invoice-lookup endpoint checks that a caller's token is VALID, never that the
token's owner actually OWNS the invoice being requested - any authenticated
user's own genuine token reaches every other user's data just by changing the
ID in the URL.
"""
from flask import Blueprint, jsonify, request

bp = Blueprint("bola", __name__)

BASE = "/api/bola/1"

USERS = {
    "alice": {"user_id": "u1"},
    "bob": {"user_id": "u2"},
}

TOKENS = {}  # token -> user_id, populated by /login

INVOICES = {
    "ord-1001": {"owner_id": "u1", "amount": 249.99, "notes": "Alice's private invoice - card ending 4242"},
    "ord-1002": {"owner_id": "u2", "amount": 1875.00, "notes": "Bob's private invoice - card ending 9911"},
}


def _caller_id():
    auth = request.headers.get("Authorization", "")
    token = auth[len("Bearer ") :].strip() if auth.startswith("Bearer ") else auth.strip()
    return TOKENS.get(token)


@bp.post(f"{BASE}/login")
def login():
    # Authentication here is intentionally trivial (username only, no
    # password) - this lab is about authorization, not authentication.
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    user = USERS.get(username)
    if not user:
        return jsonify({"error": "unknown username"}), 404
    token = f"demo-{username}-{user['user_id']}"
    TOKENS[token] = user["user_id"]
    return jsonify({"token": token, "user_id": user["user_id"]}), 200


@bp.get(f"{BASE}/invoices/<invoice_id>")
def get_invoice(invoice_id):
    caller_id = _caller_id()
    if not caller_id:
        return jsonify({"error": "invalid or missing token"}), 401

    invoice = INVOICES.get(invoice_id)
    if not invoice:
        return jsonify({"error": "not found"}), 404

    # BUG: the token was validated above, but nothing checks it against
    # invoice['owner_id'] - any logged-in user can read anyone's invoice.
    result = {"invoice_id": invoice_id, **invoice}
    if invoice["owner_id"] != caller_id:
        result["flag"] = "FLAG{bola-1-solved}"
    return jsonify(result), 200
