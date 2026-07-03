import json


# ---------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------

def test_create_item_success(client):
    response = client.post("/api/items", json={
        "name": "Cooking Oil 2L", "barcode": "999", "category": "Groceries",
        "quantity": 20, "price": 550.0
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Cooking Oil 2L"
    assert data["id"] is not None


def test_create_item_missing_name_fails(client):
    response = client.post("/api/items", json={"quantity": 5})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_item_duplicate_barcode_fails(client, sample_item):
    response = client.post("/api/items", json={
        "name": "Duplicate Sugar", "barcode": "1234567890123", "quantity": 1
    })
    assert response.status_code == 409


# ---------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------

def test_get_all_items(client, sample_item):
    response = client.get("/api/items")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["name"] == "Sugar 1kg"


def test_get_single_item(client, sample_item):
    response = client.get(f"/api/items/{sample_item}")
    assert response.status_code == 200
    assert response.get_json()["id"] == sample_item


def test_get_nonexistent_item_returns_404(client):
    response = client.get("/api/items/999")
    assert response.status_code == 404


def test_filter_items_by_category(client, sample_item):
    response = client.get("/api/items?category=Groceries")
    assert response.status_code == 200
    assert len(response.get_json()) == 1

    response = client.get("/api/items?category=Electronics")
    assert response.status_code == 200
    assert len(response.get_json()) == 0


# ---------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------

def test_patch_item_updates_fields(client, sample_item):
    response = client.patch(f"/api/items/{sample_item}", json={"quantity": 2})
    assert response.status_code == 200
    data = response.get_json()
    assert data["quantity"] == 2
    assert data["name"] == "Sugar 1kg"


def test_patch_nonexistent_item_returns_404(client):
    response = client.patch("/api/items/999", json={"quantity": 2})
    assert response.status_code == 404


def test_patch_with_no_body_returns_400(client, sample_item):
    response = client.patch(f"/api/items/{sample_item}", json={})
    assert response.status_code == 400


# ---------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------

def test_delete_item(client, sample_item):
    response = client.delete(f"/api/items/{sample_item}")
    assert response.status_code == 200

    follow_up = client.get(f"/api/items/{sample_item}")
    assert follow_up.status_code == 404


def test_delete_nonexistent_item_returns_404(client):
    response = client.delete("/api/items/999")
    assert response.status_code == 404


# ---------------------------------------------------------------------
# Helper routes
# ---------------------------------------------------------------------

def test_search_items_by_name(client, sample_item):
    response = client.get("/api/items/search?name=sugar")
    assert response.status_code == 200
    assert len(response.get_json()) == 1

    response = client.get("/api/items/search?name=nonexistent")
    assert response.status_code == 200
    assert len(response.get_json()) == 0


def test_search_requires_name_param(client):
    response = client.get("/api/items/search")
    assert response.status_code == 400


def test_low_stock_endpoint(client, sample_item):
    # sample_item has quantity=10, threshold default is 5 -> not low stock
    response = client.get("/api/items/low-stock")
    assert response.status_code == 200
    assert len(response.get_json()) == 0

    # raise threshold above 10 -> should now show up
    response = client.get("/api/items/low-stock?threshold=15")
    assert response.status_code == 200
    assert len(response.get_json()) == 1
