import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'inventory.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENFOODFACTS_PRODUCT_URL = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    OPENFOODFACTS_SEARCH_URL = "https://world.openfoodfacts.org/cgi/search.pl"


class TestConfig(Config):
    """Configuration used by the automated test suite."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
