from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from db.models import User
from services.authz_service import can


def get_current_user():
    try:
        user_id = get_jwt_identity()
    except RuntimeError:
        return None

    if not user_id:
        return None
    return User.query.get(user_id)


class RoleChecker:
    def __init__(self, *allowed_roles):
        self.allowed_roles = {role.lower() for role in allowed_roles if role}

    def __call__(self, fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            current_role = (claims.get("role") or "").lower()

            if not current_role:
                user = get_current_user()
                current_role = user.role.name.lower() if user and user.role and user.role.name else None

            user = get_current_user()
            session_id = claims.get("session_id")
            if user and user.session_id and session_id and user.session_id != session_id:
                return jsonify({"error": "Session expired or revoked"}), 401

            if self.allowed_roles and current_role not in self.allowed_roles:
                return (
                    jsonify(
                        {
                            "error": "Insufficient permissions",
                            "required_roles": sorted(self.allowed_roles),
                            "current_role": current_role,
                        }
                    ),
                    403,
                )

            return fn(*args, **kwargs)

        return wrapper


class CasbinChecker:
    def __init__(self, obj: str, act: str):
        self.obj = obj
        self.act = act

    def __call__(self, fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            current_role = (claims.get("role") or "").lower()
            if not current_role:
                user = get_current_user()
                current_role = user.role.name.lower() if user and user.role and user.role.name else None

            if not can(current_role, self.obj, self.act):
                return (
                    jsonify(
                        {
                            "error": "Insufficient permissions",
                            "required_object": self.obj,
                            "required_action": self.act,
                            "current_role": current_role,
                        }
                    ),
                    403,
                )

            return fn(*args, **kwargs)

        return wrapper


def require_roles(*roles):
    return RoleChecker(*roles)


def require_permission(obj: str, act: str):
    return CasbinChecker(obj, act)
