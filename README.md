# Inventory Management System

A Flask REST API for a small retail company's admin portal. Employees can
add, view, update, and delete inventory items, and can pull real product
details (name, category, description) from the **OpenFoodFacts** API by
barcode or product name to speed up data entry.

## Features

- Full CRUD REST API for inventory items (Flask + SQLAlchemy + SQLite)
- External API integration with [OpenFoodFacts](https://world.openfoodfacts.org)
  - Look up a product by barcode
  - Search products by name
  - Import a looked-up product straight into the local inventory database
- Command-line interface (`cli.py`) that talks to the running API
- Automated test suite (pytest) covering models, routes, external API
  integration, and the CLI — 37 tests, all mocked where network calls
  would otherwise be required

## Project Structure

```
inventory-management-system/
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── config.py         # App + test configuration
│   ├── models.py         # Item model (SQLAlchemy)
│   ├── routes.py         # All API routes (CRUD + external API + helpers)
│   └── external_api.py   # OpenFoodFacts integration
├── tests/
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_routes.py
│   ├── test_external_api.py
│   ├── test_external_routes.py
│   └── test_cli.py
├── cli.py                # CLI client for the API
├── run.py                # Entry point (starts the Flask dev server)
├── requirements.txt
└── README.md
```

## Setup

```bash
# Clone the repo
git clone https://github.com/spartanabzz467-ui/inventory-management-system.git
cd inventory-management-system

# Create and activate a virtual environment
python3 -m venv venv
. venv/bin/activate        # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the API

```bash
python run.py
```

The API will be available at `http://127.0.0.1:5000`. The SQLite database
(`inventory.db`) is created automatically on first run.

## Running the CLI

Keep the API running in one terminal, then in another terminal:

```bash
python cli.py list
python cli.py add --name "Rice 2kg" --price 350 --quantity 20 --category Groceries
python cli.py get 1
python cli.py update 1 --quantity 15
python cli.py delete 1
python cli.py search --name rice
python cli.py low-stock --threshold 5
python cli.py external-lookup 737628064502
python cli.py external-search --name "peanut butter"
python cli.py import-external 737628064502 --price 450 --quantity 10
```

## Running the Tests

```bash
pytest -v
```

All 37 tests should pass. External API calls are mocked in the test suite
so the tests run offline and deterministically.

## API Reference

| Method | Endpoint                          | Description                                   |
|--------|------------------------------------|------------------------------------------------|
| GET    | `/api/items`                       | List all items (optional `?category=`)        |
| GET    | `/api/items/<id>`                  | Get a single item                              |
| POST   | `/api/items`                       | Create a new item                              |
| PATCH  | `/api/items/<id>`                  | Update an existing item                        |
| DELETE | `/api/items/<id>`                  | Delete an item                                 |
| GET    | `/api/items/search?name=`          | Search local items by name                     |
| GET    | `/api/items/low-stock?threshold=`  | List items at/below a quantity threshold       |
| GET    | `/api/external/product/<barcode>`  | Look up a product on OpenFoodFacts             |
| GET    | `/api/external/search?name=`       | Search OpenFoodFacts by product name           |
| POST   | `/api/items/from-external/<barcode>` | Fetch from OpenFoodFacts and save locally    |

### Example: create an item

```bash
curl -X POST http://127.0.0.1:5000/api/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Rice 2kg", "barcode": "111", "category": "Groceries", "quantity": 20, "price": 350}'
```

### Example: import a product from the external API

```bash
curl -X POST http://127.0.0.1:5000/api/items/from-external/737628064502 \
  -H "Content-Type: application/json" \
  -d '{"quantity": 10, "price": 450}'
```

## Design Notes

- **App factory pattern** (`app/create_app`) so the app can be built with
  different configs for normal running vs. testing (in-memory SQLite).
- **External API logic is isolated** in `app/external_api.py` so it can be
  unit tested with mocks instead of hitting the real network in CI.
- **CLI is a thin HTTP client**, not a separate code path into the
  database — it exercises the same REST API a browser-based admin UI
  would use.

## Git Workflow

This project was developed using feature branches merged via pull
requests on GitHub:

- `feature/crud-api` — Flask app factory, model, and CRUD routes
- `feature/external-api` — OpenFoodFacts integration and import route
- `feature/cli` — command-line client
- `feature/tests` — pytest suite for all of the above

Each feature branch was opened as a pull request into `main`, reviewed,
merged, and deleted after merge.

<- Deployed with GitHub 37 pytest tests: models, routes, external API (mocked), CLI -->
