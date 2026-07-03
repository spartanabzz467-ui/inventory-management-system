import pytest

from app import create_app, db
from app.config import TestConfig
from app.models import Item


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_item(app):
    with app.app_context():
        item = Item(name="Sugar 1kg", barcode="1234567890123",
                    category="Groceries", quantity=10, price=150.0)
        db.session.add(item)
        db.session.commit()
        return item.id
