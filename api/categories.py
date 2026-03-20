from flask import Blueprint, jsonify, request

from api.dependencies import require_permission
from services.category_service import create_category, get_category_by_id, list_categories, update_category


categories_bp = Blueprint("categories", __name__, url_prefix="/api")


def _serialize_category(category):
    return {
        "id": category.id,
        "name": category.name,
        "active": category.active,
        "sort_order": category.sort_order,
        "created_at": category.created_at.isoformat() if category.created_at else None,
    }


def _parse_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


@categories_bp.route("/product-categories", methods=["GET"])
def list_public_categories():
    """
    List public product categories
    ---
    tags:
      - Categories
    responses:
      200:
        description: Active category list
    """
    categories = list_categories(include_inactive=False)
    return jsonify([_serialize_category(category) for category in categories])


@categories_bp.route("/admin/product-categories", methods=["GET"])
@require_permission("/api/admin/product-categories", "GET")
def list_admin_categories():
    """
    List all product categories
    ---
    tags:
      - Categories
    security:
      - bearerAuth: []
    responses:
      200:
        description: All category list
      403:
        description: Forbidden
    """
    categories = list_categories(include_inactive=True)
    return jsonify([_serialize_category(category) for category in categories])


@categories_bp.route("/admin/product-categories", methods=["POST"])
@require_permission("/api/admin/product-categories", "POST")
def create_admin_category():
    """
    Create product category
    ---
    tags:
      - Categories
    security:
      - bearerAuth: []
    consumes:
      - application/json
    responses:
      201:
        description: Category created
      400:
        description: Invalid payload
      403:
        description: Forbidden
    """
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    sort_order = data.get("sort_order", 0)
    active = _parse_bool(data.get("active", True), True)
    try:
        sort_order = int(sort_order)
    except (TypeError, ValueError):
        return jsonify({"error": "sort_order must be an integer"}), 400

    category = create_category(name, sort_order=sort_order, active=active)
    if not category:
        return jsonify({"error": "Failed to create category"}), 400
    return jsonify(_serialize_category(category)), 201


@categories_bp.route("/admin/product-categories/<int:category_id>", methods=["PATCH"])
@require_permission("/api/admin/product-categories/:category_id", "PATCH")
def update_admin_category(category_id):
    """
    Update product category
    ---
    tags:
      - Categories
    security:
      - bearerAuth: []
    parameters:
      - in: path
        name: category_id
        required: true
        type: integer
    responses:
      200:
        description: Category updated
      400:
        description: Invalid payload
      404:
        description: Category not found
      403:
        description: Forbidden
    """
    category = get_category_by_id(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json(silent=True) or {}
    payload = {}
    if "name" in data:
        payload["name"] = data.get("name")
    if "active" in data:
        payload["active"] = _parse_bool(data.get("active"))
    if "sort_order" in data and data.get("sort_order") is not None:
        try:
            payload["sort_order"] = int(data.get("sort_order"))
        except (TypeError, ValueError):
            return jsonify({"error": "sort_order must be an integer"}), 400

    try:
        updated = update_category(category, payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(_serialize_category(updated))
