from flask import Blueprint, jsonify

from api.dependencies import RoleChecker
from db.models import User


admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


def _serialize_user(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.name if user.role else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@admin_bp.route("/users", methods=["GET"])
@RoleChecker("SuperAdmin")
def list_users():
    """
    List users
    ---
    tags:
      - Admin
    security:
      - bearerAuth: []
    responses:
      200:
        description: User list
      403:
        description: Forbidden
    """
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([_serialize_user(user) for user in users])
