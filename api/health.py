from flask import Blueprint, jsonify


health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check
    ---
    tags:
      - Health
    responses:
      200:
        description: Service is healthy
    """
    return jsonify({"status": "ok"})
