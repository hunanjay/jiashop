from api.categories import categories_bp
from api.cart import cart_bp
from api.admin import admin_bp, workspace_bp
from api.auth import auth_bp
from api.health import health_bp
from api.orders import orders_bp
from api.public_checkout import public_checkout_bp
from api.products import products_bp
from api.upload import upload_bp


def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(public_checkout_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(workspace_bp)
    app.register_blueprint(upload_bp)
