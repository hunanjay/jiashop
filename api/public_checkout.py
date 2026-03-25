from flask import Blueprint, jsonify, request

from db.extensions import db
from db.models import Customer, User
from services.order_service import create_order as service_create_order


public_checkout_bp = Blueprint("public_checkout", __name__, url_prefix="/api/public")


def _serialize_user(user: User):
    return {
        "id": user.id,
        "username": user.username,
    }


def _resolve_owner_id(owner_username: str, owner_id: str | None = None):
    username = (owner_username or "").strip()
    if not username:
        return None

    user = User.query.filter(User.username == username).first()
    if user:
        return user.id

    if owner_id:
        candidate = User.query.get(owner_id.strip())
        if candidate and candidate.username == username:
            return candidate.id

    return None


def _parse_order_payload(data):
    customer_name = (data.get("customer_name") or "").strip()
    if not customer_name:
        return None, (jsonify({"error": "customer_name is required"}), 400)

    items = data.get("items", [])
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
        "status": (data.get("status") or "Pending").strip() or "Pending",
        "owner_username": (data.get("owner_username") or "").strip(),
        "owner_id": (data.get("owner_id") or "").strip() or None,
        "customer_id": (data.get("customer_id") or "").strip() or None,
        "customer_phone": (data.get("customer_phone") or "").strip() or None,
        "shipping_address": (data.get("shipping_address") or "").strip() or None,
        "remarks": (data.get("remarks") or "").strip() or None,
    }, None


@public_checkout_bp.route("/users/search", methods=["GET"])
def search_users():
    query = (request.args.get("q") or "").strip()
    if not query:
        return jsonify([])

    users = (
        User.query.filter(User.username.ilike(f"%{query}%"))
        .order_by(User.username.asc())
        .limit(10)
        .all()
    )
    return jsonify([_serialize_user(user) for user in users])


@public_checkout_bp.route("/customers", methods=["POST"])
def create_public_customer():
    data = request.get_json(silent=True) or {}
    company_name = (data.get("company_name") or "").strip()
    if not company_name:
        return jsonify({"error": "company_name is required"}), 400

    owner_id = _resolve_owner_id(data.get("owner_username") or "", data.get("owner_id"))
    if not owner_id:
        return jsonify({"error": "owner_username is required and must match an existing user"}), 400

    customer = Customer(
        company_name=company_name,
        purchaser=(data.get("purchaser") or "").strip() or None,
        phone=(data.get("phone") or "").strip() or None,
        shipping_address=(data.get("shipping_address") or "").strip() or None,
        owner_id=owner_id,
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify(
        {
            "id": customer.id,
            "company_name": customer.company_name,
            "purchaser": customer.purchaser,
            "phone": customer.phone,
            "shipping_address": customer.shipping_address,
            "owner_id": customer.owner_id,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
            "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
        }
    ), 201


@public_checkout_bp.route("/orders", methods=["POST"])
def create_public_order():
    data = request.get_json(silent=True) or {}
    payload, error_response = _parse_order_payload(data)
    if error_response:
        return error_response

    owner_id = _resolve_owner_id(payload.get("owner_username") or "", payload.get("owner_id"))
    if not owner_id:
        return jsonify({"error": "owner_username is required and must match an existing user"}), 400

    payload = {key: value for key, value in payload.items() if key != "owner_username"}
    order = service_create_order({**payload, "owner_id": owner_id})
    return jsonify(
        {
            "id": order.id,
            "customer_name": order.customer_name,
            "items": order.items_json,
            "status": order.status,
            "total_price": order.total_price,
            "customer_id": order.customer_id,
            "customer_phone": order.customer_phone,
            "shipping_address": order.shipping_address,
            "remarks": order.remarks,
            "owner_id": order.owner_id,
            "created_at": order.created_at.isoformat() if order.created_at else None,
        }
    ), 201
