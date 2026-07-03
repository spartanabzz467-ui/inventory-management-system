from unittest.mock import patch


FAKE_PRODUCT = {
    "name": "Peanut Butter",
    "barcode": "737628064502",
    "category": "Spreads",
    "description": "Creamy peanut butter",
    "brands": "Acme",
    "image_url": "https://example.com/image.jpg",
}


def test_external_lookup_route_success(client):
    with patch("app.routes.fetch_product_by_barcode", return_value=FAKE_PRODUCT):
        response = client.get("/api/external/product/737628064502")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Peanut Butter"


def test_external_lookup_route_not_found(client):
    with patch("app.routes.fetch_product_by_barcode", return_value=None):
        response = client.get("/api/external/product/000000000000")
    assert response.status_code == 404


def test_external_search_route(client):
    with patch("app.routes.fetch_products_by_name", return_value=[FAKE_PRODUCT]):
        response = client.get("/api/external/search?name=peanut")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_external_search_requires_name(client):
    response = client.get("/api/external/search")
    assert response.status_code == 400


def test_import_item_from_external_creates_local_item(client):
    with patch("app.routes.fetch_product_by_barcode", return_value=FAKE_PRODUCT):
        response = client.post(
            "/api/items/from-external/737628064502",
            json={"quantity": 15, "price": 450.0},
        )
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Peanut Butter"
    assert data["quantity"] == 15
    assert data["price"] == 450.0

    # It should now also show up in the regular item list
    follow_up = client.get("/api/items")
    assert len(follow_up.get_json()) == 1


def test_import_item_from_external_not_found(client):
    with patch("app.routes.fetch_product_by_barcode", return_value=None):
        response = client.post("/api/items/from-external/000000000000", json={})
    assert response.status_code == 404


def test_import_item_from_external_duplicate_barcode(client, sample_item):
    # sample_item already has barcode 1234567890123
    with patch("app.routes.fetch_product_by_barcode", return_value=FAKE_PRODUCT):
        response = client.post("/api/items/from-external/1234567890123", json={})
    assert response.status_code == 409
