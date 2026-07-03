from app import db
from app.models import Item


def test_create_item(app):
    with app.app_context():
        item = Item(name="Milk 500ml", barcode="111", category="Dairy",
                     quantity=5, price=80.0)
        db.session.add(item)
        db.session.commit()

        assert item.id is not None
        assert item.name == "Milk 500ml"


def test_to_dict_contains_expected_fields(app, sample_item):
    with app.app_context():
        item = Item.query.get(sample_item)
        data = item.to_dict()
        assert data["name"] == "Sugar 1kg"
        assert data["quantity"] == 10
        assert "created_at" in data


def test_update_from_dict_partial_update(app, sample_item):
    with app.app_context():
        item = Item.query.get(sample_item)
        item.update_from_dict({"quantity": 3})
        db.session.commit()

        refreshed = Item.query.get(sample_item)
        assert refreshed.quantity == 3
        assert refreshed.name == "Sugar 1kg"  # untouched field stays the same
