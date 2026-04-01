from datetime import datetime
import uuid

from werkzeug.security import check_password_hash, generate_password_hash

from db.extensions import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    users = db.relationship("User", backref="role", lazy=True)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(30), unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    session_id = db.Column(db.String(36), unique=True)
    access_token = db.Column(db.Text)
    access_token_expires_at = db.Column(db.DateTime)
    refresh_token = db.Column(db.Text)
    refresh_token_expires_at = db.Column(db.DateTime)
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"))
    action = db.Column(db.String(255), nullable=False)
    resource_id = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=10)
    status = db.Column(db.String(20), default="active", nullable=False)
    image_url = db.Column(db.Text)
    images_json = db.Column(db.JSON)
    category = db.Column(db.String(50))
    customization_json = db.Column(db.JSON)
    owner_id = db.Column(db.String(36), db.ForeignKey("users.id"))
    sales_count = db.Column(db.Integer, nullable=False, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ProductCategory(db.Model):
    __tablename__ = "product_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    active = db.Column(db.Boolean, default=True, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_name = db.Column(db.String(120), nullable=False)
    purchaser = db.Column(db.String(80))
    phone = db.Column(db.String(30))
    shipping_address = db.Column(db.String(255))
    owner_id = db.Column(db.String(36), db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())[:8])
    customer_name = db.Column(db.String(100), nullable=False)
    items_json = db.Column(db.JSON, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    total_price = db.Column(db.Float, nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey("customers.id"))
    customer_phone = db.Column(db.String(30))
    shipping_address = db.Column(db.String(255))
    custom_logo_url = db.Column(db.Text)
    design_file_url = db.Column(db.Text)
    effect_images_json = db.Column(db.JSON)
    remarks = db.Column(db.Text)
    owner_id = db.Column(db.String(36), db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)
    cart_token = db.Column(db.String(64), nullable=False, index=True)
    product_id = db.Column(db.String(36), db.ForeignKey("products.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
