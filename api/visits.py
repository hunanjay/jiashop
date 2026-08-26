from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request

from db.extensions import db
from db.models import Visit


visits_bp = Blueprint("visits", __name__, url_prefix="/api")

# ponytail: 同设备同页面 30 分钟内只记一次，去掉刷新噪音；要精确会话统计再建 session 表
DEDUPE_WINDOW = timedelta(minutes=30)


@visits_bp.route("/visits", methods=["POST"])
def track_visit():
    """
    Record a customer page visit (device based, no auth)
    ---
    tags:
      - Visits
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - device_id
          properties:
            device_id:
              type: string
            path:
              type: string
    responses:
      200:
        description: Visit recorded or deduped
      400:
        description: device_id missing
    """
    data = request.get_json(silent=True) or {}
    device_id = (data.get("device_id") or "").strip()[:64]
    if not device_id:
        return jsonify({"error": "device_id is required"}), 400

    path = ((data.get("path") or "/").strip() or "/")[:255]
    duplicate = Visit.query.filter(
        Visit.device_id == device_id,
        Visit.path == path,
        Visit.created_at >= datetime.utcnow() - DEDUPE_WINDOW,
    ).first()
    if duplicate:
        return jsonify({"recorded": False, "device_id": device_id})

    forwarded = request.headers.get("X-Forwarded-For") or request.remote_addr or ""
    visit = Visit(
        device_id=device_id,
        path=path,
        ip=forwarded.split(",")[0].strip()[:45],
        user_agent=(request.headers.get("User-Agent") or "")[:255],
    )
    db.session.add(visit)
    db.session.commit()
    return jsonify({"recorded": True, "device_id": device_id})
