import os

from flasgger import Swagger
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from sqlalchemy import inspect, text

from api import register_blueprints
from config import DevelopmentConfig
from db.extensions import db


SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "GiftCraft API",
        "description": "Gift customization backend API",
        "version": "1.0.0",
    },
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "bearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Use: Bearer <access_token>",
        }
    },
}

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec_1",
            "route": "/apispec_1.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}


def register_jwt_callbacks(jwt: JWTManager):
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        return jsonify({"error": "Missing access token", "detail": reason}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Invalid access token", "detail": reason}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token expired", "token_type": jwt_payload.get("type")}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "Token revoked"}), 401


def ensure_schema(app):
    """Best-effort schema sync for environments where migrations have not been applied yet."""
    with app.app_context():
        inspector = inspect(db.engine)
        dialect_name = db.engine.dialect.name

        def _ensure_text_column(table_name, column_name):
            if not inspector.has_table(table_name):
                return

            columns = {column["name"]: column for column in inspector.get_columns(table_name)}
            column = columns.get(column_name)
            if not column:
                return

            column_type = column.get("type")
            if getattr(column_type, "length", None) is None and column_type.__class__.__name__.lower() == "text":
                return
            if getattr(column_type, "length", None) is None and "TEXT" in str(column_type).upper():
                return

            if dialect_name == "sqlite":
                return

            db.session.execute(text(f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE TEXT"))
            db.session.commit()

        if inspector.has_table("users"):
            user_columns = {column["name"] for column in inspector.get_columns("users")}
            user_additions = {
                "phone": "VARCHAR(30)",
                "session_id": "VARCHAR(36)",
                "access_token": "TEXT",
                "access_token_expires_at": "TIMESTAMP",
                "refresh_token": "TEXT",
                "refresh_token_expires_at": "TIMESTAMP",
                "last_login_at": "TIMESTAMP",
            }
            for column_name, column_type in user_additions.items():
                if column_name not in user_columns:
                    db.session.execute(text(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"))
            if any(column not in user_columns for column in user_additions):
                db.session.commit()

        if inspector.has_table("customers"):
            customer_columns = {column["name"] for column in inspector.get_columns("customers")}
        else:
            customer_columns = set()
        if not inspector.has_table("customers"):
            db.session.execute(
                text(
                    """
                    CREATE TABLE customers (
                        id VARCHAR(36) PRIMARY KEY,
                        company_name VARCHAR(120) NOT NULL,
                        purchaser VARCHAR(80),
                        phone VARCHAR(30),
                        shipping_address VARCHAR(255),
                        owner_id VARCHAR(36),
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                    """
                )
            )
            db.session.commit()

        if inspector.has_table("orders"):
            order_columns = {column["name"] for column in inspector.get_columns("orders")}
            order_additions = {
                "customer_id": "VARCHAR(36)",
                "customer_phone": "VARCHAR(30)",
                "shipping_address": "VARCHAR(255)",
                "custom_logo_url": "VARCHAR(255)",
                "design_file_url": "VARCHAR(255)",
                "remarks": "TEXT",
            }
            for column_name, column_type in order_additions.items():
                if column_name not in order_columns:
                    db.session.execute(text(f"ALTER TABLE orders ADD COLUMN {column_name} {column_type}"))
            if any(column not in order_columns for column in order_additions):
                db.session.commit()

        if inspector.has_table("products"):
            product_columns = {column["name"] for column in inspector.get_columns("products")}
            product_additions = {
                "status": "VARCHAR(20)",
                "updated_at": "TIMESTAMP",
                "sales_count": "INTEGER",
            }
            for column_name, column_type in product_additions.items():
                if column_name not in product_columns:
                    default_clause = " DEFAULT 'active'" if column_name == "status" else (" DEFAULT 0" if column_name == "sales_count" else "")
                    db.session.execute(text(f"ALTER TABLE products ADD COLUMN {column_name} {column_type}{default_clause}"))
            if any(column not in product_columns for column in product_additions):
                db.session.commit()

        _ensure_text_column("products", "image_url")
        _ensure_text_column("orders", "custom_logo_url")
        _ensure_text_column("orders", "design_file_url")


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt = JWTManager(app)
    register_jwt_callbacks(jwt)
    register_blueprints(app)
    Swagger(app, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)
    ensure_schema(app)

    @app.route("/")
    def index():
        return jsonify(
            {
                "name": "GiftCraft API",
                "docs": "/apidocs/",
                "health": "/api/health",
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=int(os.environ.get("PORT", 5050)), host="0.0.0.0")
