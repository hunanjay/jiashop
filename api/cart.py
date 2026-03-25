from flask import Blueprint, jsonify, request

from db.extensions import db
from db.models import CartItem, Product


cart_bp = Blueprint("cart", __name__, url_prefix="/api")


def _read_token():
    token = (request.headers.get("X-Cart-Token") or request.args.get("token") or "").strip()
    if not token:
        payload = request.get_json(silent=True) or {}
        token = (payload.get("token") or "").strip()
    return token


def _serialize_cart(token: str):
    rows = CartItem.query.filter_by(cart_token=token).all()
    return {
        "token": token,
        "items": [{"product_id": row.product_id, "quantity": row.quantity} for row in rows],
    }


@cart_bp.route("/cart", methods=["GET"])
def get_cart():
    token = _read_token()
    if not token:
        return jsonify({"error": "Missing cart token"}), 400
    return jsonify(_serialize_cart(token))


@cart_bp.route("/cart/items", methods=["POST"])
def add_cart_item():
    token = _read_token()
    if not token:
        return jsonify({"error": "Missing cart token"}), 400

    payload = request.get_json(silent=True) or {}
    product_id = (payload.get("product_id") or "").strip()
    try:
        quantity_delta = int(payload.get("quantity", 1) or 1)
    except (TypeError, ValueError):
        return jsonify({"error": "quantity must be an integer"}), 400

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400
    if quantity_delta == 0:
        return jsonify(_serialize_cart(token))

    product = Product.query.filter(Product.id == product_id, Product.status != "deleted").first()
    if not product:
        return jsonify({"error": "Product not found"}), 404

    row = CartItem.query.filter_by(cart_token=token, product_id=product_id).first()
    if row:
        row.quantity = max(0, int(row.quantity or 0) + quantity_delta)
        if row.quantity <= 0:
            db.session.delete(row)
    elif quantity_delta > 0:
        db.session.add(CartItem(cart_token=token, product_id=product_id, quantity=quantity_delta))

    db.session.commit()
    return jsonify(_serialize_cart(token))


@cart_bp.route("/cart/items/<product_id>", methods=["PUT"])
def set_cart_item_quantity(product_id):
    token = _read_token()
    if not token:
        return jsonify({"error": "Missing cart token"}), 400

    payload = request.get_json(silent=True) or {}
    try:
        quantity = int(payload.get("quantity", 0) or 0)
    except (TypeError, ValueError):
        return jsonify({"error": "quantity must be an integer"}), 400

    row = CartItem.query.filter_by(cart_token=token, product_id=product_id).first()
    if quantity <= 0:
        if row:
            db.session.delete(row)
            db.session.commit()
        return jsonify(_serialize_cart(token))

    product = Product.query.filter(Product.id == product_id, Product.status != "deleted").first()
    if not product:
        return jsonify({"error": "Product not found"}), 404

    if row:
        row.quantity = quantity
    else:
        db.session.add(CartItem(cart_token=token, product_id=product_id, quantity=quantity))
    db.session.commit()
    return jsonify(_serialize_cart(token))


@cart_bp.route("/cart", methods=["DELETE"])
def clear_cart():
    token = _read_token()
    if not token:
        return jsonify({"error": "Missing cart token"}), 400
    CartItem.query.filter_by(cart_token=token).delete()
    db.session.commit()
    return jsonify(_serialize_cart(token))
