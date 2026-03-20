from flask import Blueprint, jsonify, request

from api.dependencies import require_permission
from db.models import User
from services.admin_service import get_role_by_name, list_roles, update_user_role
from api.dependencies import get_current_user


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
@require_permission("/api/admin/users", "GET")
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


@admin_bp.route("/roles", methods=["GET"])
@require_permission("/api/admin/roles", "GET")
def get_roles():
    """
    List roles
    ---
    tags:
      - Admin
    security:
      - bearerAuth: []
    responses:
      200:
        description: Role list
      403:
        description: Forbidden
    """
    roles = list_roles()
    return jsonify([{"id": role.id, "name": role.name} for role in roles])


@admin_bp.route("/users/<user_id>/role", methods=["PATCH"])
@require_permission("/api/admin/users/:user_id/role", "PATCH")
def change_user_role(user_id):
    """
    Update user role
    ---
    tags:
      - Admin
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: user_id
        required: true
        type: string
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - role
          properties:
            role:
              type: string
    responses:
      200:
        description: Role updated
      400:
        description: Invalid role
      404:
        description: User not found
      403:
        description: Forbidden
    """
    data = request.get_json(silent=True) or {}
    role_name = (data.get("role") or "").strip()

    if not role_name:
        return jsonify({"error": "role is required"}), 400

    role = get_role_by_name(role_name)
    if not role:
        return jsonify({"error": "Role not found", "role": role_name}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    actor = get_current_user()
    updated_user = update_user_role(user, role, actor.id if actor else None)
    return jsonify(_serialize_user(updated_user))
