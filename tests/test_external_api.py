from unittest.mock import patch, Mock

from app.external_api import fetch_product_by_barcode, fetch_products_by_name


FAKE_OFF_PRODUCT_RESPONSE = {
    "status": 1,
    "product": {
        "product_name": "Peanut Butter",
        "code": "737628064502",
        "categories": "Spreads, Sweet spreads, Peanut butter",
        "generic_name": "Creamy peanut butter",
        "brands": "Acme",
        "image_url": "https://example.com/image.jpg",
    },
}

FAKE_OFF_NOT_FOUND_RESPONSE = {"status": 0}

FAKE_OFF_SEARCH_RESPONSE = {
    "products": [
        {"product_name": "Peanut Butter Smooth", "code": "1", "brands": "Acme"},
        {"product_name": "Peanut Butter Crunchy", "code": "2", "brands": "Acme"},
    ]
}


def _mock_response(json_data, status_ok=True):
    mock_resp = Mock()
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status = Mock() if status_ok else Mock(side_effect=Exception("HTTP error"))
    return mock_resp


def test_fetch_product_by_barcode_success(app):
    with app.app_context():
        with patch("app.external_api.requests.get", return_value=_mock_response(FAKE_OFF_PRODUCT_RESPONSE)):
            product = fetch_product_by_barcode("737628064502")

    assert product is not None
    assert product["name"] == "Peanut Butter"
    assert product["barcode"] == "737628064502"
    assert product["category"] == "Spreads"


def test_fetch_product_by_barcode_not_found(app):
    with app.app_context():
        with patch("app.external_api.requests.get", return_value=_mock_response(FAKE_OFF_NOT_FOUND_RESPONSE)):
            product = fetch_product_by_barcode("000000000000")

    assert product is None


def test_fetch_product_by_barcode_handles_request_exception(app):
    import requests
    with app.app_context():
        with patch("app.external_api.requests.get", side_effect=requests.RequestException("network down")):
            product = fetch_product_by_barcode("123")

    assert product is None


def test_fetch_products_by_name_success(app):
    with app.app_context():
        with patch("app.external_api.requests.get", return_value=_mock_response(FAKE_OFF_SEARCH_RESPONSE)):
            products = fetch_products_by_name("peanut butter")

    assert len(products) == 2
    assert products[0]["name"] == "Peanut Butter Smooth"


def test_fetch_products_by_name_empty_results(app):
    with app.app_context():
        with patch("app.external_api.requests.get", return_value=_mock_response({"products": []})):
            products = fetch_products_by_name("nonexistent product xyz")

    assert products == []
