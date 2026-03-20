from flask import Blueprint, jsonify, request

from api.dependencies import RoleChecker, get_current_user
from services.order_service import create_order as service_create_order
from services.order_service import get_order as service_get_order
from services.order_service import list_orders as service_list_orders
from services.order_service import update_order_status as service_update_order_status


orders_bp = Blueprint("orders", __name__, url_prefix="/api")


def _serialize_order(order):
    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "items": order.items_json,
        "status": order.status,
        "total_price": order.total_price,
        "created_at": order.created_at.isoformat() if order.created_at else None,
    }


@orders_bp.route("/orders", methods=["POST"])
def create_order():
    """
    Create order
    ---
    tags:
      - Orders
    consumes:
      - application/json
    responses:
      201:
        description: Order created
      400:
        description: Invalid payload
    """
    data = request.get_json(silent=True) or {}
    items = data.get("items", [])

    if not isinstance(items, list):
        return jsonify({"error": "items must be a list"}), 400

    try:
        total_price = float(data.get("total_price", 0) or 0)
    except (TypeError, ValueError):
        return jsonify({"error": "total_price must be a number"}), 400

    order = service_create_order(
        {
            "customer_name": data.get("customer_name", "Anonymous"),
            "items_json": items,
            "total_price": total_price,
            "status": "Pending",
        }
    )
    return jsonify(_serialize_order(order)), 201


@orders_bp.route("/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    """
    Get order detail
    ---
    tags:
      - Orders
    parameters:
      - in: path
        name: order_id
        required: true
        type: string
    responses:
      200:
        description: Order found
      404:
        description: Order not found
    """
    order = service_get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(_serialize_order(order))


@orders_bp.route("/admin/orders", methods=["GET"])
@RoleChecker("Admin", "SuperAdmin")
def list_orders():
    """
    Admin order list
    ---
    tags:
      - Orders
    security:
      - bearerAuth: []
    responses:
      200:
        description: Order list
      403:
        description: Forbidden
    """
    orders = service_list_orders()
    return jsonify([_serialize_order(order) for order in orders])


@orders_bp.route("/admin/orders/<order_id>/status", methods=["PUT"])
@RoleChecker("Admin", "SuperAdmin")
def update_order_status(order_id):
    """
    Update order status
    ---
    tags:
      - Orders
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: order_id
        required: true
        type: string
    responses:
      200:
        description: Order updated
      400:
        description: Invalid payload
      404:
        description: Order not found
    """
    data = request.get_json(silent=True) or {}
    order = service_get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    new_status = (data.get("status") or "").strip()
    if not new_status:
        return jsonify({"error": "status is required"}), 400

    user = get_current_user()
    order = service_update_order_status(order, new_status, user.id if user else None)
    return jsonify(_serialize_order(order))
