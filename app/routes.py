from flask import Blueprint, jsonify, request

from app import db
from app.models import Item
from app.external_api import fetch_product_by_barcode, fetch_products_by_name

items_bp = Blueprint("items", __name__)


# ---------------------------------------------------------------------
# CRUD routes
# ---------------------------------------------------------------------

@items_bp.route("/items", methods=["GET"])
def get_items():
    """List all items. Supports optional ?category= filter."""
    query = Item.query
    category = request.args.get("category")
    if category:
        query = query.filter(Item.category.ilike(f"%{category}%"))
    items = query.order_by(Item.id).all()
    return jsonify([item.to_dict() for item in items]), 200


@items_bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    return jsonify(item.to_dict()), 200


@items_bp.route("/items", methods=["POST"])
def create_item():
    data = request.get_json(silent=True) or {}

    if not data.get("name"):
        return jsonify({"error": "'name' is required"}), 400

    if data.get("barcode") and Item.query.filter_by(barcode=data["barcode"]).first():
        return jsonify({"error": "An item with this barcode already exists"}), 409

    item = Item(
        name=data["name"],
        barcode=data.get("barcode"),
        category=data.get("category"),
        description=data.get("description"),
        quantity=data.get("quantity", 0),
        price=data.get("price", 0.0),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@items_bp.route("/items/<int:item_id>", methods=["PATCH", "PUT"])
def update_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": f"Item {item_id} not found"}), 404

    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"error": "No update data provided"}), 400

    new_barcode = data.get("barcode")
    if new_barcode and new_barcode != item.barcode:
        existing = Item.query.filter_by(barcode=new_barcode).first()
        if existing:
            return jsonify({"error": "An item with this barcode already exists"}), 409

    item.update_from_dict(data)
    db.session.commit()
    return jsonify(item.to_dict()), 200


@items_bp.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": f"Item {item_id} not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Item {item_id} deleted"}), 200


# ---------------------------------------------------------------------
# Helper routes
# ---------------------------------------------------------------------

@items_bp.route("/items/search", methods=["GET"])
def search_items():
    """Search local inventory by name (?name=)."""
    name = request.args.get("name", "")
    if not name:
        return jsonify({"error": "'name' query parameter is required"}), 400
    items = Item.query.filter(Item.name.ilike(f"%{name}%")).all()
    return jsonify([item.to_dict() for item in items]), 200


@items_bp.route("/items/low-stock", methods=["GET"])
def low_stock_items():
    """Return items at or below a quantity threshold (default 5)."""
    threshold = request.args.get("threshold", 5, type=int)
    items = Item.query.filter(Item.quantity <= threshold).all()
    return jsonify([item.to_dict() for item in items]), 200


# ---------------------------------------------------------------------
# External API integration routes (OpenFoodFacts)
# ---------------------------------------------------------------------

@items_bp.route("/external/product/<barcode>", methods=["GET"])
def external_lookup_by_barcode(barcode):
    """Look up a product on OpenFoodFacts without saving it."""
    product = fetch_product_by_barcode(barcode)
    if not product:
        return jsonify({"error": f"No product found for barcode {barcode}"}), 404
    return jsonify(product), 200


@items_bp.route("/external/search", methods=["GET"])
def external_search_by_name():
    """Search OpenFoodFacts by product name without saving results."""
    name = request.args.get("name", "")
    if not name:
        return jsonify({"error": "'name' query parameter is required"}), 400
    products = fetch_products_by_name(name)
    return jsonify(products), 200


@items_bp.route("/items/from-external/<barcode>", methods=["POST"])
def import_item_from_external(barcode):
    """Fetch a product from OpenFoodFacts by barcode and save it into
    the local inventory database. Extra JSON body fields (quantity,
    price) can be supplied to fill in what the external API doesn't
    provide."""
    if Item.query.filter_by(barcode=barcode).first():
        return jsonify({"error": "An item with this barcode already exists"}), 409

    product = fetch_product_by_barcode(barcode)
    if not product:
        return jsonify({"error": f"No product found for barcode {barcode}"}), 404

    overrides = request.get_json(silent=True) or {}

    item = Item(
        name=product["name"],
        barcode=product["barcode"],
        category=product.get("category"),
        description=product.get("description"),
        quantity=overrides.get("quantity", 0),
        price=overrides.get("price", 0.0),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201
