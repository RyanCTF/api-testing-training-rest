"""Simulated third-party partner API that main-app trusts (see
sections/unsafe_consumption.py in main-app). Deliberately has no auth on
set_avatar_url - simulates an attacker who is a legitimately registered partner
user updating their own profile, which they're fully entitled to do. The bug this
lab teaches lives entirely in main-app's blind trust, not here.
"""
from flask import Flask, jsonify, request

app = Flask(__name__)

USERS = {
    "p-1": {"display_name": "Partner User One", "avatar_url": "https://cdn.partner.example/avatars/default.png"},
}


@app.get("/partner/users/<user_id>")
def get_user(user_id):
    user = USERS.get(user_id)
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": user_id, **user}), 200


@app.post("/partner/users/<user_id>/avatar_url")
def set_avatar_url(user_id):
    data = request.get_json(silent=True) or {}
    avatar_url = data.get("avatar_url")
    if not avatar_url:
        return jsonify({"error": "avatar_url is required"}), 400
    user = USERS.setdefault(user_id, {"display_name": f"Partner User {user_id}"})
    user["avatar_url"] = avatar_url
    return jsonify({"id": user_id, **user}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
