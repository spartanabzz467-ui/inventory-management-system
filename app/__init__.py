from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    """Application factory. Lets us build the app with different configs
    (normal run vs. testing) without duplicating setup code."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from app.routes import items_bp
    app.register_blueprint(items_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return jsonify({
            "message": "Inventory Management System API",
            "endpoints": {
                "items": "/api/items",
                "single_item": "/api/items/<id>",
                "search": "/api/items/search?name=<name>",
                "low_stock": "/api/items/low-stock?threshold=<n>",
                "external_lookup": "/api/external/product/<barcode>",
                "external_search": "/api/external/search?name=<name>",
                "import_from_external": "/api/items/from-external/<barcode>",
            }
        })

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    with app.app_context():
        db.create_all()

    return app
