from datetime import datetime

from db.models import Product, db


def list_products():
    return Product.query.filter(Product.status != "deleted").order_by(Product.created_at.desc()).all()


def list_products_for_owner(owner_id):
    return Product.query.filter(Product.owner_id == owner_id, Product.status != "deleted").order_by(Product.created_at.desc()).all()


def get_product(product_id):
    product = Product.query.get(product_id)
    if product and product.status == "deleted":
        return None
    return product


def create_product(payload):
    product = Product(**payload)
    db.session.add(product)
    db.session.commit()
    return product


def create_owned_product(payload, owner_id):
    payload = {**payload, "owner_id": owner_id}
    return create_product(payload)


def update_product(product, payload):
    for field in ("name", "description", "price", "stock", "status", "image_url", "category", "customization_json", "sales_count"):
        if field in payload:
            setattr(product, field, payload[field])
    product.updated_at = datetime.utcnow()
    db.session.commit()
    return product


def delete_product(product):
    product.status = "deleted"
    product.updated_at = datetime.utcnow()
    db.session.commit()
