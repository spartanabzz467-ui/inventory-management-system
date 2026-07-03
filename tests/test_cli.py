from unittest.mock import patch, Mock

import cli


def _mock_response(json_data, status_code=200):
    mock_resp = Mock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    return mock_resp


def test_cmd_list_prints_items(capsys):
    args = Mock(category=None)
    with patch("cli._request", return_value=_mock_response([
        {"id": 1, "name": "Sugar", "barcode": "1", "category": "Groceries",
         "quantity": 10, "price": 150.0}
    ])):
        cli.cmd_list(args)
    captured = capsys.readouterr()
    assert "Sugar" in captured.out


def test_cmd_list_no_items(capsys):
    args = Mock(category=None)
    with patch("cli._request", return_value=_mock_response([])):
        cli.cmd_list(args)
    captured = capsys.readouterr()
    assert "No items found" in captured.out


def test_cmd_add_success(capsys):
    args = Mock(name="Rice", barcode="2", category="Groceries",
                 description=None, quantity=5, price=200.0)
    with patch("cli._request", return_value=_mock_response(
        {"id": 2, "name": "Rice", "barcode": "2", "category": "Groceries",
         "quantity": 5, "price": 200.0}, status_code=201
    )):
        cli.cmd_add(args)
    captured = capsys.readouterr()
    assert "Item created" in captured.out
    assert "Rice" in captured.out


def test_cmd_delete_success(capsys):
    args = Mock(id=1)
    with patch("cli._request", return_value=_mock_response({"message": "Item 1 deleted"})):
        cli.cmd_delete(args)
    captured = capsys.readouterr()
    assert "deleted" in captured.out


def test_cmd_get_not_found(capsys):
    args = Mock(id=999)
    with patch("cli._request", return_value=_mock_response({"error": "Item 999 not found"}, status_code=404)):
        cli.cmd_get(args)
    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_build_parser_list_command():
    parser = cli.build_parser()
    args = parser.parse_args(["list"])
    assert args.command == "list"
    assert args.func == cli.cmd_list


def test_build_parser_add_command_requires_name():
    parser = cli.build_parser()
    args = parser.parse_args(["add", "--name", "Salt", "--quantity", "3"])
    assert args.name == "Salt"
    assert args.quantity == 3
