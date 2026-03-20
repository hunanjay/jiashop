from flask_jwt_extended import create_access_token, create_refresh_token

from db.models import User


def authenticate_user(username: str, password: str):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None


def build_user_claims(user: User):
    role_name = user.role.name if user.role else "Guest"
    return {
        "username": user.username,
        "role": role_name,
        "email": user.email,
    }


def issue_token_pair(user: User):
    claims = build_user_claims(user)
    access_token = create_access_token(identity=user.id, additional_claims=claims)
    refresh_token = create_refresh_token(identity=user.id, additional_claims=claims)
    return access_token, refresh_token
