from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from db.models import User


def get_current_user():
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(user_id)


class RoleChecker:
    def __init__(self, *allowed_roles):
        self.allowed_roles = {role for role in allowed_roles if role}

    def __call__(self, fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            current_role = claims.get("role")

            if not current_role:
                user = get_current_user()
                current_role = user.role.name if user and user.role else None

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


def require_roles(*roles):
    return RoleChecker(*roles)
