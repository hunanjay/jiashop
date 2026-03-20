from db.models import Order, Product, Role, User, db


DEFAULT_ROLES = ["Guest", "User", "Admin", "SuperAdmin"]
DEFAULT_USERS = [
    {
        "username": "superadmin",
        "email": "superadmin@giftcraft.com",
        "password": "superadmin123",
        "role": "SuperAdmin",
    },
    {
        "username": "admin",
        "email": "admin@giftcraft.com",
        "password": "admin123",
        "role": "Admin",
    },
    {
        "username": "content_admin",
        "email": "content_admin@giftcraft.com",
        "password": "content123",
        "role": "Admin",
    },
    {
        "username": "guest",
        "email": "guest@giftcraft.com",
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
    },
    {
        "name": "Personalized Leather Notebook",
        "description": "High-quality leather-bound notebook with gold-leaf initials.",
        "price": 45.0,
        "stock": 12,
        "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&q=80&w=400",
        "category": "Stationery",
        "customization_json": {"type": "Embossing", "fields": ["Initials"]},
    },
    {
        "name": "Branded Executive Gift Box",
        "description": "Curated premium gift set with logo card and premium packaging.",
        "price": 129.0,
        "stock": 8,
        "image_url": "https://images.unsplash.com/photo-1513885535751-8b9238bd345a?auto=format&fit=crop&q=80&w=400",
        "category": "Corporate Gifts",
        "customization_json": {"type": "Branding", "fields": ["Logo", "Greeting Card"]},
    },
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
            role_id=role.id,
        )
        user.set_password(entry["password"])
        db.session.add(user)
        return user

    changed = False
    if user.email != entry["email"]:
        user.email = entry["email"]
        changed = True
    if user.role_id != role.id:
        user.role_id = role.id
        changed = True

    if changed:
        db.session.add(user)
    return user


def _upsert_product(entry):
    product = Product.query.filter_by(name=entry["name"]).first()
    if not product:
        product = Product(**entry)
        db.session.add(product)
        return product

    product.description = entry["description"]
    product.price = entry["price"]
    product.stock = entry["stock"]
    product.image_url = entry["image_url"]
    product.category = entry["category"]
    product.customization_json = entry["customization_json"]
    db.session.add(product)
    return product


def seed_mock_data(app):
    with app.app_context():
        db.create_all()

        for role_name in DEFAULT_ROLES:
            _upsert_role(role_name)
        db.session.commit()

        for user in DEFAULT_USERS:
            _upsert_user(user)
        db.session.commit()

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
