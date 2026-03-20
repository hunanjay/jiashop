from db.models import Product, db


def list_products():
    return Product.query.order_by(Product.created_at.desc()).all()


def list_products_for_owner(owner_id):
    return Product.query.filter_by(owner_id=owner_id).order_by(Product.created_at.desc()).all()


def get_product(product_id):
    return Product.query.get(product_id)


def create_product(payload):
    product = Product(**payload)
    db.session.add(product)
    db.session.commit()
    return product


def create_owned_product(payload, owner_id):
    payload = {**payload, "owner_id": owner_id}
    return create_product(payload)


def update_product(product, payload):
    for field in ("name", "description", "price", "stock", "image_url", "category", "customization_json"):
        if field in payload:
            setattr(product, field, payload[field])
    db.session.commit()
    return product


def delete_product(product):
    db.session.delete(product)
    db.session.commit()
