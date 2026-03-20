from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from api.dependencies import RoleChecker, get_current_user
from db.models import User
from services.auth_service import authenticate_user, build_user_claims, issue_token_pair


auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _serialize_user(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role.name if user.role else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    User login
    ---
    tags:
      - Auth
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login succeeded
      401:
        description: Invalid credentials
      400:
        description: Missing credentials
    """
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = authenticate_user(username, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    access_token, refresh_token = issue_token_pair(user)
    claims = build_user_claims(user)
    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "role": claims["role"],
            "username": claims["username"],
            "email": claims["email"],
            "user": _serialize_user(user),
        }
    )


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token
    ---
    tags:
      - Auth
    security:
      - bearerAuth: []
    responses:
      200:
        description: New access token
      401:
        description: Invalid or expired refresh token
    """
    current_user = get_current_user()
    claims = get_jwt()
    additional_claims = {
        "username": claims.get("username", current_user.username if current_user else ""),
        "role": claims.get("role", current_user.role.name if current_user and current_user.role else "Guest"),
        "email": claims.get("email", current_user.email if current_user else ""),
    }
    from flask_jwt_extended import create_access_token

    access_token = create_access_token(identity=get_jwt_identity(), additional_claims=additional_claims)
    return jsonify({"access_token": access_token, "token_type": "Bearer", "expires_in": 3600})


@auth_bp.route("/me", methods=["GET"])
@RoleChecker("Guest", "User", "Admin", "SuperAdmin")
def me():
    """
    Current user profile
    ---
    tags:
      - Auth
    security:
      - bearerAuth: []
    responses:
      200:
        description: Current user
      401:
        description: Missing or invalid token
    """
    user = get_current_user()
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(_serialize_user(user))
