from api.admin import admin_bp
from api.auth import auth_bp
from api.health import health_bp
from api.orders import orders_bp
from api.products import products_bp


def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
