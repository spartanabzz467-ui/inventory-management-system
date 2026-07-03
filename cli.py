"""
Command-line interface for the Inventory Management System.

This CLI is a thin client: every command makes an HTTP request to the
Flask REST API (so make sure `python run.py` is running first, by
default at http://127.0.0.1:5000).

Usage examples:
    python cli.py list
    python cli.py list --category Snacks
    python cli.py get 3
    python cli.py add --name "Rice 2kg" --price 350 --quantity 20 --category Groceries
    python cli.py update 3 --quantity 15
    python cli.py delete 3
    python cli.py search --name rice
    python cli.py low-stock --threshold 5
    python cli.py external-lookup 737628064502
    python cli.py external-search --name "peanut butter"
    python cli.py import-external 737628064502 --price 450 --quantity 10
"""
import argparse
import sys

import requests

BASE_URL = "http://127.0.0.1:5000/api"


def _print_item(item):
    print(f"[{item['id']}] {item['name']}  "
          f"barcode={item.get('barcode')}  "
          f"category={item.get('category')}  "
          f"qty={item['quantity']}  "
          f"price={item['price']}")


def _print_items(items):
    if not items:
        print("No items found.")
        return
    for item in items:
        _print_item(item)


def _request(method, path, **kwargs):
    try:
        response = requests.request(method, f"{BASE_URL}{path}", timeout=10, **kwargs)
    except requests.ConnectionError:
        print("Could not connect to the API. Is `python run.py` running?")
        sys.exit(1)
    return response


def cmd_list(args):
    params = {}
    if args.category:
        params["category"] = args.category
    response = _request("GET", "/items", params=params)
    _print_items(response.json())


def cmd_get(args):
    response = _request("GET", f"/items/{args.id}")
    if response.status_code == 200:
        _print_item(response.json())
    else:
        print(response.json().get("error", "Item not found"))


def cmd_add(args):
    payload = {
        "name": args.name,
        "barcode": args.barcode,
        "category": args.category,
        "description": args.description,
        "quantity": args.quantity,
        "price": args.price,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    response = _request("POST", "/items", json=payload)
    if response.status_code == 201:
        print("Item created:")
        _print_item(response.json())
    else:
        print("Error:", response.json().get("error"))


def cmd_update(args):
    payload = {}
    for field in ("name", "barcode", "category", "description", "quantity", "price"):
        value = getattr(args, field)
        if value is not None:
            payload[field] = value
    response = _request("PATCH", f"/items/{args.id}", json=payload)
    if response.status_code == 200:
        print("Item updated:")
        _print_item(response.json())
    else:
        print("Error:", response.json().get("error"))


def cmd_delete(args):
    response = _request("DELETE", f"/items/{args.id}")
    print(response.json().get("message") or response.json().get("error"))


def cmd_search(args):
    response = _request("GET", "/items/search", params={"name": args.name})
    _print_items(response.json())


def cmd_low_stock(args):
    response = _request("GET", "/items/low-stock", params={"threshold": args.threshold})
    _print_items(response.json())


def cmd_external_lookup(args):
    response = _request("GET", f"/external/product/{args.barcode}")
    if response.status_code == 200:
        product = response.json()
        print(f"{product['name']}  brand={product.get('brands')}  "
              f"category={product.get('category')}")
    else:
        print(response.json().get("error"))


def cmd_external_search(args):
    response = _request("GET", "/external/search", params={"name": args.name})
    products = response.json()
    if not products:
        print("No products found.")
    for p in products:
        print(f"{p['name']}  barcode={p.get('barcode')}  brand={p.get('brands')}")


def cmd_import_external(args):
    payload = {}
    if args.quantity is not None:
        payload["quantity"] = args.quantity
    if args.price is not None:
        payload["price"] = args.price
    response = _request("POST", f"/items/from-external/{args.barcode}", json=payload)
    if response.status_code == 201:
        print("Item imported from external API:")
        _print_item(response.json())
    else:
        print("Error:", response.json().get("error"))


def build_parser():
    parser = argparse.ArgumentParser(description="Inventory Management System CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List all items")
    p_list.add_argument("--category")
    p_list.set_defaults(func=cmd_list)

    p_get = sub.add_parser("get", help="Get a single item by id")
    p_get.add_argument("id", type=int)
    p_get.set_defaults(func=cmd_get)

    p_add = sub.add_parser("add", help="Add a new item")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--barcode")
    p_add.add_argument("--category")
    p_add.add_argument("--description")
    p_add.add_argument("--quantity", type=int, default=0)
    p_add.add_argument("--price", type=float, default=0.0)
    p_add.set_defaults(func=cmd_add)

    p_update = sub.add_parser("update", help="Update an existing item")
    p_update.add_argument("id", type=int)
    p_update.add_argument("--name")
    p_update.add_argument("--barcode")
    p_update.add_argument("--category")
    p_update.add_argument("--description")
    p_update.add_argument("--quantity", type=int)
    p_update.add_argument("--price", type=float)
    p_update.set_defaults(func=cmd_update)

    p_delete = sub.add_parser("delete", help="Delete an item")
    p_delete.add_argument("id", type=int)
    p_delete.set_defaults(func=cmd_delete)

    p_search = sub.add_parser("search", help="Search items by name")
    p_search.add_argument("--name", required=True)
    p_search.set_defaults(func=cmd_search)

    p_low = sub.add_parser("low-stock", help="List items at/below a quantity threshold")
    p_low.add_argument("--threshold", type=int, default=5)
    p_low.set_defaults(func=cmd_low_stock)

    p_ext_lookup = sub.add_parser("external-lookup", help="Look up a product by barcode via OpenFoodFacts")
    p_ext_lookup.add_argument("barcode")
    p_ext_lookup.set_defaults(func=cmd_external_lookup)

    p_ext_search = sub.add_parser("external-search", help="Search OpenFoodFacts by product name")
    p_ext_search.add_argument("--name", required=True)
    p_ext_search.set_defaults(func=cmd_external_search)

    p_import = sub.add_parser("import-external", help="Fetch a product from OpenFoodFacts and save it locally")
    p_import.add_argument("barcode")
    p_import.add_argument("--quantity", type=int)
    p_import.add_argument("--price", type=float)
    p_import.set_defaults(func=cmd_import_external)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

<- Deployed with GitHub CLI client for the REST API -->
