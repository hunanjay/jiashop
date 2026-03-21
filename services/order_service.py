from db.models import AuditLog, Order, db


def list_orders():
    return Order.query.order_by(Order.created_at.desc()).all()


def get_order(order_id):
    return Order.query.get(order_id)


def create_order(payload):
    order = Order(**payload)
    db.session.add(order)
    db.session.commit()
    return order


def list_orders_for_owner(owner_id):
    return Order.query.filter_by(owner_id=owner_id).order_by(Order.created_at.desc()).all()


def delete_order(order):
    db.session.delete(order)
    db.session.commit()
    return True


def update_order_status(order, new_status, user_id=None):
    if user_id:
        db.session.add(
            AuditLog(
                user_id=user_id,
                action=f"Status updated to {new_status}",
                resource_id=order.id,
            )
        )
    order.status = new_status
    db.session.commit()
    return order


def add_order_note(order, note, user_id=None):
    if user_id:
        db.session.add(
            AuditLog(
                user_id=user_id,
                action=f"Note added: {note[:180]}",
                resource_id=order.id,
            )
        )
    order.remarks = note
    db.session.commit()
    return order


def list_order_timeline(order_id):
    return AuditLog.query.filter_by(resource_id=order_id).order_by(AuditLog.timestamp.desc()).all()
