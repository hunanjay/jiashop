from datetime import datetime, timedelta
import uuid

from flask_jwt_extended import create_access_token, create_refresh_token

from db.models import User


def authenticate_user(username: str, password: str):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None


def build_user_claims(user: User):
    role_name = (user.role.name if user.role else "Guest").lower()
    return {
        "username": user.username,
        "role": role_name,
        "email": user.email,
        "session_id": user.session_id,
    }


def issue_token_pair(user: User):
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()
    access_expires_at = now + timedelta(hours=1)
    refresh_expires_at = now + timedelta(days=30)
    user.session_id = session_id
    claims = build_user_claims(user)
    access_token = create_access_token(identity=user.id, additional_claims=claims, expires_delta=timedelta(hours=1))
    refresh_token = create_refresh_token(identity=user.id, additional_claims=claims, expires_delta=timedelta(days=30))
    user.access_token = access_token
    user.refresh_token = refresh_token
    user.access_token_expires_at = access_expires_at
    user.refresh_token_expires_at = refresh_expires_at
    user.last_login_at = now
    return access_token, refresh_token
