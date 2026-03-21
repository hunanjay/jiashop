from flask import Blueprint, jsonify, request

from api.dependencies import get_current_user, require_permission
from services.order_service import create_order as service_create_order
from services.order_service import add_order_note as service_add_order_note
from services.order_service import delete_order as service_delete_order
from services.order_service import get_order as service_get_order
from services.order_service import list_orders as service_list_orders
from services.order_service import list_order_timeline as service_list_order_timeline
from services.order_service import list_orders_for_owner as service_list_orders_for_owner
from services.order_service import update_order_status as service_update_order_status


orders_bp = Blueprint("orders", __name__, url_prefix="/api")


def _serialize_order(order):
    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "items": order.items_json,
        "status": order.status,
        "total_price": order.total_price,
        "customer_id": order.customer_id,
        "customer_phone": order.customer_phone,
        "shipping_address": order.shipping_address,
        "custom_logo_url": order.custom_logo_url,
        "design_file_url": order.design_file_url,
        "remarks": order.remarks,
        "owner_id": order.owner_id,
        "created_at": order.created_at.isoformat() if order.created_at else None,
    }


def _serialize_timeline_item(item):
    return {
        "id": item.id,
        "user_id": item.user_id,
        "action": item.action,
        "resource_id": item.resource_id,
        "timestamp": item.timestamp.isoformat() if item.timestamp else None,
    }


def _build_order_payload(data, *, require_customer_name=False, status_default="Pending"):
    customer_name = (data.get("customer_name") or "").strip()
    items = data.get("items", [])

    if require_customer_name and not customer_name:
        return None, (jsonify({"error": "customer_name is required"}), 400)
    if not require_customer_name and not customer_name:
        customer_name = "Anonymous"

    if not isinstance(items, list):
        return None, (jsonify({"error": "items must be a list"}), 400)

    try:
        total_price = float(data.get("total_price", 0) or 0)
    except (TypeError, ValueError):
        return None, (jsonify({"error": "total_price must be a number"}), 400)

    return {
        "customer_name": customer_name,
        "items_json": items,
        "total_price": total_price,
        "status": (data.get("status") or status_default).strip() or status_default,
        "customer_id": (data.get("customer_id") or "").strip() or None,
        "customer_phone": (data.get("customer_phone") or "").strip() or None,
        "shipping_address": (data.get("shipping_address") or "").strip() or None,
        "custom_logo_url": (data.get("custom_logo_url") or "").strip() or None,
        "design_file_url": (data.get("design_file_url") or "").strip() or None,
        "remarks": (data.get("remarks") or "").strip() or None,
    }, None


@orders_bp.route("/orders", methods=["POST"])
@require_permission("/api/orders", "POST")
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
    payload, error_response = _build_order_payload(data)
    if error_response:
        return error_response

    order = service_create_order(
        {
            **payload,
            "owner_id": get_current_user().id if get_current_user() else None,
        }
    )
    return jsonify(_serialize_order(order)), 201


@orders_bp.route("/orders/<order_id>", methods=["GET"])
@require_permission("/api/orders/:order_id", "GET")
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
    current_user = get_current_user()
    if current_user and current_user.role and current_user.role.name and current_user.role.name.lower() == "user" and order.owner_id != current_user.id:
        return jsonify({"error": "Can only view your own order"}), 403
    return jsonify(_serialize_order(order))


@orders_bp.route("/admin/orders", methods=["GET"])
@require_permission("/api/admin/orders", "GET")
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
    current_user = get_current_user()
    if current_user and current_user.role and current_user.role.name and current_user.role.name.lower() == "user":
        orders = service_list_orders_for_owner(current_user.id)
    else:
        orders = service_list_orders()
    return jsonify([_serialize_order(order) for order in orders])


@orders_bp.route("/workspace/orders", methods=["GET"])
@require_permission("/api/workspace/orders", "GET")
def list_workspace_orders():
    """
    Workspace order list
    ---
    tags:
      - Orders
    security:
      - bearerAuth: []
    responses:
      200:
        description: Own order list for workspace users
      403:
        description: Forbidden
    """
    current_user = get_current_user()
    if not current_user:
        return jsonify([])
    if current_user.role and current_user.role.name and current_user.role.name.lower() == "user":
        orders = service_list_orders_for_owner(current_user.id)
    else:
        orders = service_list_orders()
    return jsonify([_serialize_order(order) for order in orders])


@orders_bp.route("/workspace/orders", methods=["POST"])
@require_permission("/api/workspace/orders", "POST")
def create_workspace_order():
    """
    Create workspace order
    ---
    tags:
      - Orders
    security:
      - bearerAuth: []
    consumes:
      - application/json
    responses:
      201:
        description: Order created
      400:
        description: Invalid payload
      403:
        description: Forbidden
    """
    data = request.get_json(silent=True) or {}
    payload, error_response = _build_order_payload(data, require_customer_name=True)
    if error_response:
        return error_response

    current_user = get_current_user()
    order = service_create_order(
        {
            **payload,
            "owner_id": current_user.id if current_user else None,
        }
    )
    return jsonify(_serialize_order(order)), 201


@orders_bp.route("/admin/orders", methods=["POST"])
@require_permission("/api/admin/orders", "POST")
def create_admin_order():
    """
    Create admin order
    ---
    tags:
      - Orders
    security:
      - bearerAuth: []
    consumes:
      - application/json
    responses:
      201:
        description: Order created
      400:
        description: Invalid payload
      403:
        description: Forbidden
    """
    data = request.get_json(silent=True) or {}
    payload, error_response = _build_order_payload(data, require_customer_name=True)
    if error_response:
        return error_response

    order = service_create_order(
        {
            **payload,
            "owner_id": get_current_user().id if get_current_user() else None,
        }
    )
    return jsonify(_serialize_order(order)), 201


@orders_bp.route("/admin/orders/<order_id>/status", methods=["PUT"])
@require_permission("/api/admin/orders/:order_id/status", "PUT")
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

    current_user = get_current_user()
    if current_user and current_user.role and current_user.role.name and current_user.role.name.lower() == "user" and order.owner_id != current_user.id:
        return jsonify({"error": "Can only modify your own order"}), 403

    new_status = (data.get("status") or "").strip()
    if not new_status:
        return jsonify({"error": "status is required"}), 400

    user = get_current_user()
    order = service_update_order_status(order, new_status, user.id if user else None)
    return jsonify(_serialize_order(order))


@orders_bp.route("/admin/orders/<order_id>/note", methods=["POST"])
@require_permission("/api/admin/orders/:order_id/note", "POST")
def add_order_note(order_id):
    data = request.get_json(silent=True) or {}
    note = (data.get("note") or "").strip()
    if not note:
        return jsonify({"error": "note is required"}), 400

    order = service_get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    current_user = get_current_user()
    order = service_add_order_note(order, note, current_user.id if current_user else None)
    return jsonify(_serialize_order(order))


@orders_bp.route("/admin/orders/<order_id>/timeline", methods=["GET"])
@require_permission("/api/admin/orders/:order_id/timeline", "GET")
def get_order_timeline(order_id):
    order = service_get_order(order_id)
    if not order:
      return jsonify({"error": "Order not found"}), 404
    timeline = service_list_order_timeline(order_id)
    return jsonify([_serialize_timeline_item(item) for item in timeline])


@orders_bp.route("/admin/orders/<order_id>", methods=["DELETE"])
@require_permission("/api/admin/orders/:order_id", "DELETE")
def delete_admin_order(order_id):
    """
    Delete order
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
        description: Order deleted
      404:
        description: Order not found
      403:
        description: Forbidden
    """
    order = service_get_order(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    current_user = get_current_user()
    if current_user and current_user.role and current_user.role.name and current_user.role.name.lower() == "user" and order.owner_id != current_user.id:
        return jsonify({"error": "Can only delete your own order"}), 403

    service_delete_order(order)
    return jsonify({"message": "Order deleted", "id": order_id})
