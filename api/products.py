from flask import Blueprint, jsonify, request

from api.dependencies import RoleChecker
from services.product_service import create_product as service_create_product
from services.product_service import delete_product as service_delete_product
from services.product_service import get_product as service_get_product
from services.product_service import list_products as service_list_products
from services.product_service import update_product as service_update_product


products_bp = Blueprint("products", __name__, url_prefix="/api")


def _serialize_product(product):
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "stock": product.stock,
        "image_url": product.image_url,
        "category": product.category,
        "customization": product.customization_json,
        "created_at": product.created_at.isoformat() if product.created_at else None,
    }


def _parse_price(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_stock(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _extract_product_payload():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    price = _parse_price(data.get("price"))
    stock = _parse_stock(data.get("stock", 10))

    if not name:
        return None, (jsonify({"error": "Product name is required"}), 400)
    if price is None:
        return None, (jsonify({"error": "Product price must be a number"}), 400)
    if stock is None or stock < 0:
        return None, (jsonify({"error": "Product stock must be a non-negative integer"}), 400)

    return {
        "name": name,
        "description": data.get("description"),
        "price": price,
        "stock": stock,
        "image_url": data.get("image_url"),
        "category": data.get("category"),
        "customization_json": data.get("customization") or {},
    }, None


@products_bp.route("/products", methods=["GET"])
def list_products():
    """
    List products
    ---
    tags:
      - Products
    responses:
      200:
        description: Product list
    """
    products = service_list_products()
    return jsonify([_serialize_product(product) for product in products])


@products_bp.route("/admin/products", methods=["GET"])
@RoleChecker("Admin", "SuperAdmin")
def admin_list_products():
    """
    Admin product list
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
    responses:
      200:
        description: Product list
      403:
        description: Forbidden
    """
    products = service_list_products()
    return jsonify([_serialize_product(product) for product in products])


@products_bp.route("/products/<product_id>", methods=["GET"])
def get_product(product_id):
    """
    Get product detail
    ---
    tags:
      - Products
    parameters:
      - in: path
        name: product_id
        required: true
        type: string
    responses:
      200:
        description: Product found
      404:
        description: Product not found
    """
    product = service_get_product(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(_serialize_product(product))


@products_bp.route("/products", methods=["POST"])
@RoleChecker("Admin", "SuperAdmin")
def create_product():
    """
    Create product
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
    consumes:
      - application/json
    responses:
      201:
        description: Product created
      400:
        description: Invalid payload
      403:
        description: Forbidden
    """
    payload, error_response = _extract_product_payload()
    if error_response:
        return error_response

    product = service_create_product(payload)
    return jsonify(_serialize_product(product)), 201


@products_bp.route("/products/<product_id>", methods=["PUT"])
@RoleChecker("Admin", "SuperAdmin")
def update_product(product_id):
    """
    Update product
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: product_id
        required: true
        type: string
    responses:
      200:
        description: Product updated
      404:
        description: Product not found
    """
    product = service_get_product(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json(silent=True) or {}
    payload = {}

    if "name" in data:
        payload["name"] = (data.get("name") or "").strip() or product.name
    if "description" in data:
        payload["description"] = data.get("description")
    if "price" in data and data.get("price") is not None:
        price = _parse_price(data.get("price"))
        if price is None:
            return jsonify({"error": "Product price must be a number"}), 400
        payload["price"] = price
    if "stock" in data and data.get("stock") is not None:
        stock = _parse_stock(data.get("stock"))
        if stock is None or stock < 0:
            return jsonify({"error": "Product stock must be a non-negative integer"}), 400
        payload["stock"] = stock
    if "image_url" in data:
        payload["image_url"] = data.get("image_url")
    if "category" in data:
        payload["category"] = data.get("category")
    if "customization" in data:
        payload["customization_json"] = data.get("customization") or {}

    product = service_update_product(product, payload)
    return jsonify(_serialize_product(product))


@products_bp.route("/products/<product_id>", methods=["DELETE"])
@RoleChecker("Admin", "SuperAdmin")
def delete_product(product_id):
    """
    Delete product
    ---
    tags:
      - Products
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: product_id
        required: true
        type: string
    responses:
      200:
        description: Product deleted
      404:
        description: Product not found
    """
    product = service_get_product(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    service_delete_product(product)
    return jsonify({"message": "Product deleted", "id": product_id})
