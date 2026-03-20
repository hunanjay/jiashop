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
