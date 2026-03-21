from db.models import Order, Product, Role, User, db
from services.category_service import create_category, normalize_category_name


DEFAULT_ROLES = ["Guest", "User", "Admin", "SuperAdmin"]
DEFAULT_USERS = [
    {
        "username": "superadmin",
        "email": "superadmin@giftcraft.com",
        "phone": "13800000001",
        "password": "superadmin123",
        "role": "SuperAdmin",
    },
    {
        "username": "admin",
        "email": "admin@giftcraft.com",
        "phone": "13800000002",
        "password": "admin123",
        "role": "Admin",
    },
    {
        "username": "content_admin",
        "email": "content_admin@giftcraft.com",
        "phone": "13800000003",
        "password": "content123",
        "role": "Admin",
    },
    {
        "username": "guest",
        "email": "guest@giftcraft.com",
        "phone": "13800000004",
        "password": "guest123",
        "role": "Guest",
    },
]
DEFAULT_PRODUCTS = [
    {
        "name": "Custom Engraved Crystal Award",
        "description": "Premium crystal award with custom engraving. Elegant and timeless.",
        "price": 89.99,
        "stock": 4,
        "image_url": "https://images.unsplash.com/photo-1549461717-d2c676941db9?auto=format&fit=crop&q=80&w=400",
        "category": "Awards",
        "customization_json": {"type": "Engraving", "fields": ["Name", "Company", "Message"]},
        "owner_username": "admin",
    },
    {
        "name": "Personalized Leather Notebook",
        "description": "High-quality leather-bound notebook with gold-leaf initials.",
        "price": 45.0,
        "stock": 12,
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&q=80&w=400",
        "category": "Stationery",
        "customization_json": {"type": "Embossing", "fields": ["Initials"]},
        "owner_username": "admin",
    },
    {
        "name": "Branded Executive Gift Box",
        "description": "Curated premium gift set with logo card and premium packaging.",
        "price": 129.0,
        "stock": 8,
        "image_url": "https://images.unsplash.com/photo-1513885535751-8b9238bd345a?auto=format&fit=crop&q=80&w=400",
        "category": "Corporate Gifts",
        "customization_json": {"type": "Branding", "fields": ["Logo", "Greeting Card"]},
        "owner_username": "content_admin",
    },
]
DEFAULT_CATEGORIES = [
    {"name": "Awards", "sort_order": 1},
    {"name": "Stationery", "sort_order": 2},
    {"name": "Corporate Gifts", "sort_order": 3},
    {"name": "Accessories", "sort_order": 4},
    {"name": "Other", "sort_order": 5},
]


def _upsert_role(name):
    role = Role.query.filter_by(name=name).first()
    if not role:
        role = Role(name=name)
        db.session.add(role)
        db.session.flush()
    return role


def _upsert_user(entry):
    user = User.query.filter_by(username=entry["username"]).first()
    role = _upsert_role(entry["role"])

    if not user:
        user = User(
            username=entry["username"],
            email=entry["email"],
            phone=entry.get("phone"),
            role_id=role.id,
        )
        user.set_password(entry["password"])
        db.session.add(user)
        return user

    changed = False
    if user.email != entry["email"]:
        user.email = entry["email"]
        changed = True
    if user.phone != entry.get("phone"):
        user.phone = entry.get("phone")
        changed = True
    if user.role_id != role.id:
        user.role_id = role.id
        changed = True

    if changed:
        db.session.add(user)
    return user


def _upsert_product(entry):
    product = Product.query.filter_by(name=entry["name"]).first()
    owner = User.query.filter_by(username=entry.get("owner_username")).first()
    if not product:
        product = Product(**{k: v for k, v in entry.items() if k != "owner_username"})
        product.owner_id = owner.id if owner else None
        db.session.add(product)
        return product

    product.description = entry["description"]
    product.price = entry["price"]
    product.stock = entry["stock"]
    product.image_url = entry["image_url"]
    product.category = entry["category"]
    product.customization_json = entry["customization_json"]
    product.owner_id = owner.id if owner else product.owner_id
    db.session.add(product)
    return product


def _seed_categories():
    seeded = {}
    for item in DEFAULT_CATEGORIES:
        category = create_category(item["name"], sort_order=item.get("sort_order", 0), active=True)
        if category:
            seeded[normalize_category_name(category.name)] = category

    for product in DEFAULT_PRODUCTS:
        category_name = normalize_category_name(product.get("category"))
        if category_name and category_name not in seeded:
            category = create_category(category_name, sort_order=99, active=True)
            if category:
                seeded[category.name] = category


def seed_mock_data(app):
    with app.app_context():
        db.create_all()

        if User.query.first():
            return {
                "roles": Role.query.count(),
                "users": User.query.count(),
                "products": Product.query.count(),
            }

        for role_name in DEFAULT_ROLES:
            _upsert_role(role_name)
        db.session.commit()

        for user in DEFAULT_USERS:
            _upsert_user(user)
        db.session.commit()

        _seed_categories()

        for product in DEFAULT_PRODUCTS:
            _upsert_product(product)
        db.session.commit()

        return {
            "roles": len(DEFAULT_ROLES),
            "users": len(DEFAULT_USERS),
            "products": len(DEFAULT_PRODUCTS),
        }


def seed_demo_order(app):
    with app.app_context():
        if Order.query.first():
            return False
        db.session.add(
            Order(
                customer_name="Demo Buyer",
                items_json=[{"product": "Custom Engraved Crystal Award", "qty": 1}],
                status="Processing",
                total_price=89.99,
            )
        )
        db.session.commit()
        return True
