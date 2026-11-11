from fastapi.testclient import TestClient

from backend import main


client = TestClient(main.app)


class FakeCursor:
    def __init__(self, rows, expected_user_id):
        self.rows = rows
        self.expected_user_id = expected_user_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def execute(self, query, params):
        assert params == (self.expected_user_id,)
        assert "owner_id = %s" in query
        assert "GROUP BY status" in query

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, rows, expected_user_id):
        self.rows = rows
        self.expected_user_id = expected_user_id

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def cursor(self):
        return FakeCursor(
            self.rows,
            self.expected_user_id,
        )


def mock_database(monkeypatch, rows, user_id=42):
    monkeypatch.setattr(
        main,
        "get_connection",
        lambda: FakeConnection(rows, user_id),
    )


def test_order_summary_requires_authentication():
    response = client.get("/orders/summary")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication required"
    }


def test_order_summary_returns_correct_counts(monkeypatch):
    rows = [
        ("Not Started", 3),
        ("Printing", 2),
        ("Shipped", 1),
    ]

    mock_database(monkeypatch, rows)

    main.app.dependency_overrides[
        main.get_current_user_id
    ] = lambda: 42

    try:
        response = client.get("/orders/summary")

        assert response.status_code == 200
        assert response.json() == {
            "status_counts": {
                "Not Started": 3,
                "Printing": 2,
                "Printed": 0,
                "Shipped": 1,
            }
        }
    finally:
        main.app.dependency_overrides.pop(
            main.get_current_user_id, None
        )


def test_order_summary_includes_all_statuses(monkeypatch):
    rows = [
        ("Not Started", 3),
        ("Shipped", 1),
    ]

    mock_database(monkeypatch, rows)

    main.app.dependency_overrides[
        main.get_current_user_id
    ] = lambda: 42

    try:
        response = client.get("/orders/summary")

        assert response.status_code == 200
        assert response.json() == {
            "status_counts": {
                "Not Started": 3,
                "Printing": 0,
                "Printed": 0,
                "Shipped": 1,
            }
        }
    finally:
        main.app.dependency_overrides.pop(
            main.get_current_user_id, None
        )


def test_order_summary_with_no_orders(monkeypatch):
    # Simulate a user with no orders
    mock_database(monkeypatch, rows=[])

    main.app.dependency_overrides[
        main.get_current_user_id
    ] = lambda: 42

    try:
        response = client.get("/orders/summary")

        assert response.status_code == 200
        assert response.json() == {
            "status_counts": {
                "Not Started": 0,
                "Printing": 0,
                "Printed": 0,
                "Shipped": 0,
            }
        }
    finally:
        main.app.dependency_overrides.pop(
            main.get_current_user_id, None
        )
