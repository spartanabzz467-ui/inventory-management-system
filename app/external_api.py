"""Integration with the OpenFoodFacts external API.

Kept in its own module (rather than mixed into routes.py) so it can be
unit tested in isolation by mocking `requests.get`.
"""
import requests
from flask import current_app

REQUEST_TIMEOUT = 8


def fetch_product_by_barcode(barcode):
    """Fetch a single product from OpenFoodFacts by barcode.

    Returns a normalized dict on success, or None if the product
    was not found / the request failed.
    """
    url = current_app.config["OPENFOODFACTS_PRODUCT_URL"].format(barcode=barcode)
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return None

    data = response.json()
    if data.get("status") != 1 or "product" not in data:
        return None

    return _normalize_product(data["product"], barcode=barcode)


def fetch_products_by_name(name, limit=10):
    """Search OpenFoodFacts for products matching a name. Returns a list
    of normalized product dicts (possibly empty)."""
    url = current_app.config["OPENFOODFACTS_SEARCH_URL"]
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit,
    }
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException:
        return []

    data = response.json()
    products = data.get("products", [])
    return [_normalize_product(p) for p in products[:limit]]


def _normalize_product(product, barcode=None):
    """Maps the (large, messy) OpenFoodFacts payload down to the fields
    our inventory system actually cares about."""
    return {
        "name": product.get("product_name") or "Unknown product",
        "barcode": barcode or product.get("code"),
        "category": (product.get("categories") or "").split(",")[0].strip() or None,
        "description": product.get("generic_name") or product.get("ingredients_text") or None,
        "brands": product.get("brands"),
        "image_url": product.get("image_url"),
    }

<- Deployed with GitHub OpenFoodFacts integration: lookup, search, import -->
