from db.models import AuditLog, Role, User, db


def list_roles():
    return Role.query.order_by(Role.id.asc()).all()


def get_role_by_name(name):
    return Role.query.filter_by(name=name).first()


def update_user_role(user: User, role: Role, actor_id=None):
    user.role_id = role.id
    db.session.add(user)

    if actor_id:
        db.session.add(
            AuditLog(
                user_id=actor_id,
                action=f"Role updated to {role.name}",
                resource_id=user.id,
            )
        )

    db.session.commit()
    return user
