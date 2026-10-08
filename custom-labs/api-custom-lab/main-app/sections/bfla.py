"""/api/bfla/1 - OWASP API5:2023, Broken Function Level Authorization. The
admin-only refund endpoint checks that a caller's token is VALID, never that
the token's owner's ROLE is actually admin - a standard user's own genuine
token reaches an operation only admins should be able to call.
"""
from flask import Blueprint, jsonify, request

bp = Blueprint("bfla", __name__)

BASE = "/api/bfla/1"

USERS = {
    "alice": {"user_id": "u1", "role": "standard"},
    "admin1": {"user_id": "u9", "role": "admin"},
}

TOKENS = {}  # token -> {"user_id":..., "role":...}, populated by /login

ORDERS = {
    "ord-2001": {"amount": 499.50, "refunded": False},
}


def _caller():
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
    TOKENS[token] = user
    return jsonify({"token": token, "user_id": user["user_id"], "role": user["role"]}), 200


@bp.post(f"{BASE}/admin/refund")
def admin_refund():
    caller = _caller()
    if not caller:
        return jsonify({"error": "invalid or missing token"}), 401

    data = request.get_json(silent=True) or {}
    order_id = data.get("order_id")
    order = ORDERS.get(order_id)
    if not order:
        return jsonify({"error": "order not found"}), 404

    # BUG: only checks that SOME valid token was presented - never that its
    # role is actually "admin", despite this being an admin-only operation.
    order["refunded"] = True
    result = {"order_id": order_id, "refunded": True, "amount": order["amount"]}
    if caller["role"] != "admin":
        result["flag"] = "FLAG{bfla-1-solved}"
    return jsonify(result), 200
