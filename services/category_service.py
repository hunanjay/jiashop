from sqlalchemy import func

from db.models import ProductCategory, db


def normalize_category_name(name: str) -> str:
    return " ".join((name or "").strip().split())


def list_categories(include_inactive: bool = False):
    query = ProductCategory.query
    if not include_inactive:
        query = query.filter_by(active=True)
    return query.order_by(ProductCategory.sort_order.asc(), ProductCategory.name.asc()).all()


def get_category_by_name(name: str):
    normalized = normalize_category_name(name)
    if not normalized:
        return None
    return ProductCategory.query.filter(func.lower(ProductCategory.name) == normalized.lower()).first()


def get_category_by_id(category_id: int):
    return ProductCategory.query.get(category_id)


def create_category(name: str, sort_order: int = 0, active: bool = True):
    normalized = normalize_category_name(name)
    if not normalized:
        return None

    category = get_category_by_name(normalized)
    if category:
        category.active = active if active is not None else category.active
        if sort_order:
            category.sort_order = sort_order
        db.session.add(category)
        db.session.commit()
        return category

    if not sort_order:
        max_sort = db.session.query(func.max(ProductCategory.sort_order)).scalar() or 0
        sort_order = max_sort + 1

    category = ProductCategory(name=normalized, active=active, sort_order=sort_order)
    db.session.add(category)
    db.session.commit()
    return category


def update_category(category: ProductCategory, payload: dict):
    if "name" in payload:
        normalized = normalize_category_name(payload["name"])
        if normalized and normalized != category.name:
            existing = get_category_by_name(normalized)
            if existing and existing.id != category.id:
                raise ValueError("Category name already exists")
            category.name = normalized
    if "active" in payload:
        category.active = bool(payload["active"])
    if "sort_order" in payload and payload["sort_order"] is not None:
        category.sort_order = int(payload["sort_order"])

    db.session.add(category)
    db.session.commit()
    return category


def delete_category(category: ProductCategory):
    from db.models import Product
    # 将属于该分类的商品的分类字段置空（或设为 None）
    Product.query.filter_by(category=category.name).update({"category": None})
    db.session.delete(category)
    db.session.commit()



def ensure_category(name: str, allow_create: bool = False):
    normalized = normalize_category_name(name)
    if not normalized:
        return None

    category = get_category_by_name(normalized)
    if category:
        if not category.active and not allow_create:
            return None
        if allow_create and not category.active:
            category.active = True
            db.session.add(category)
            db.session.commit()
        return category

    if allow_create:
        return create_category(normalized, active=True)

    return None
