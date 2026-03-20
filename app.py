import os

from flasgger import Swagger
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from api import register_blueprints
from config import DevelopmentConfig
from db.extensions import db
from services.seed_service import seed_mock_data


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


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    CORS(app)
    db.init_app(app)
    jwt = JWTManager(app)
    register_jwt_callbacks(jwt)
    register_blueprints(app)
    Swagger(app, template=SWAGGER_TEMPLATE, config=SWAGGER_CONFIG)

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
        seed_mock_data(app)
    app.run(debug=True, port=int(os.environ.get("PORT", 5050)), host="0.0.0.0")
