"""/api/unsafe-consumption/1 - OWASP API10:2023. main-app calls a "trusted" partner
API to resolve a user's avatar_url, then fetches that URL server-side with none of
the validation a directly user-supplied URL would get - because the value came
from an integration partner instead of straight from the request body, it never
occurred to anyone it needed the same scrutiny. A partner-registered attacker can
set their own avatar_url to point anywhere, including services that are only
reachable from inside the docker network, not from the public internet.
"""
import os
import re

import requests
from flask import Blueprint, jsonify, request

bp = Blueprint("unsafe_consumption", __name__)

PARTNER_API_BASE = os.environ.get("PARTNER_API_BASE", "http://partner-api:5000")

FLAG_RE = re.compile(r"FLAG\{[^}]*\}")


@bp.post("/api/unsafe-consumption/1/sync-avatar")
def sync_avatar():
    data = request.get_json(silent=True) or {}
    partner_user_id = data.get("partner_user_id")
    if not partner_user_id:
        return jsonify({"error": "partner_user_id is required"}), 400

    try:
        partner_resp = requests.get(f"{PARTNER_API_BASE}/partner/users/{partner_user_id}", timeout=3)
    except requests.RequestException as e:
        return jsonify({"error": f"partner lookup failed: {e}"}), 502
    if partner_resp.status_code != 200:
        return jsonify({"error": "partner user not found"}), 404

    partner_data = partner_resp.json()
    avatar_url = partner_data.get("avatar_url")

    # BUG (OWASP API10 - Unsafe Consumption of APIs): avatar_url came from the
    # partner integration, not directly from this request, so it never gets the
    # scheme/host validation a user-supplied URL would - no allowlist, no block
    # on internal address ranges, nothing.
    try:
        avatar_resp = requests.get(avatar_url, timeout=3)
        preview = avatar_resp.text[:500]
        result = {
            "partner_user_id": partner_user_id,
            "display_name": partner_data.get("display_name"),
            "avatar_url": avatar_url,
            "fetched_status": avatar_resp.status_code,
            "fetched_content_type": avatar_resp.headers.get("Content-Type", ""),
            "avatar_preview": preview,
        }
        match = FLAG_RE.search(preview)
        if match:
            result["flag"] = match.group(0)
        return jsonify(result), 200
    except requests.RequestException as e:
        return jsonify({"partner_user_id": partner_user_id, "avatar_url": avatar_url, "fetch_error": str(e)}), 200
