import importlib
import sqlite3

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_path = tmp_path / "tasks.db"
    monkeypatch.setenv("TASKS_DB_PATH", str(db_path))

    import main
    importlib.reload(main)

    main.DB_PATH = db_path
    main.init_database()

    with main.get_connection() as connection:
        connection.execute("DELETE FROM tasks")

        # Reset AUTOINCREMENT so the test database starts at ID 1.
        connection.execute("DELETE FROM sqlite_sequence WHERE name = 'tasks'")

        connection.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Learn FastAPI", 0),
                ("Build CRUD API", 0),
                ("Test with Swagger", 0),
            ],
        )

    return TestClient(main.app), main


def test_root_and_health(client):
    api, _ = client

    assert api.get("/").status_code == 200
    assert api.get("/health").json() == {"status": "ok"}


def test_database_schema_and_seed(client):
    api, main = client

    response = api.get("/tasks")

    assert response.status_code == 200

    assert response.json() == [
        {"id": 1, "title": "Learn FastAPI", "done": False},
        {"id": 2, "title": "Build CRUD API", "done": False},
        {"id": 3, "title": "Test with Swagger", "done": False},
    ]

    with sqlite3.connect(main.DB_PATH) as connection:
        columns = connection.execute("PRAGMA table_info(tasks)").fetchall()
        names = [column[1] for column in columns]

        assert names == ["id", "title", "done"]

        assert (
            connection.execute(
                "SELECT COUNT(*) FROM tasks"
            ).fetchone()[0]
            == 3
        )


def test_read_task_and_404(client):
    api, _ = client

    assert api.get("/tasks/1").json() == {
        "id": 1,
        "title": "Learn FastAPI",
        "done": False,
    }

    response = api.get("/tasks/99")

    assert response.status_code == 404
    assert response.json() == {"error": "Task 99 not found"}


def test_create_validation_and_persistence(client):
    api, main = client

    response = api.post(
        "/tasks",
        json={"title": "Buy milk"},
    )

    assert response.status_code == 201

    assert response.json() == {
        "id": 4,
        "title": "Buy milk",
        "done": False,
    }

    invalid = api.post("/tasks", json={})
    assert invalid.status_code == 400

    empty = api.post(
        "/tasks",
        json={"title": " "},
    )
    assert empty.status_code == 400

    with sqlite3.connect(main.DB_PATH) as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (4,),
        ).fetchone()

        assert row == (4, "Buy milk", 0)


def test_update_and_delete(client):
    api, _ = client

    response = api.put(
        "/tasks/1",
        json={"title": "Learn FastAPI deeply"},
    )

    assert response.status_code == 200

    assert response.json() == {
        "id": 1,
        "title": "Learn FastAPI deeply",
        "done": False,
    }

    response = api.put(
        "/tasks/1",
        json={"done": True},
    )

    assert response.status_code == 200
    assert response.json()["done"] is True

    empty = api.put(
        "/tasks/1",
        json={},
    )

    assert empty.status_code == 400

    missing = api.put(
        "/tasks/99",
        json={"done": True},
    )

    assert missing.status_code == 404

    deleted = api.delete("/tasks/1")

    assert deleted.status_code == 204
    assert api.get("/tasks/1").status_code == 404

    delete_missing = api.delete("/tasks/99")

    assert delete_missing.status_code == 404


def test_persistence_survives_module_reload(client):
    api, main = client

    created = api.post(
        "/tasks",
        json={"title": "Persistent task"},
    )

    assert created.status_code == 201

    created_id = created.json()["id"]

    # Reload the application while keeping the same database file.
    importlib.reload(main)

    # Point the reloaded module back to the same temporary database.
    main.DB_PATH = main.DB_PATH

    with main.get_connection() as connection:
        row = connection.execute(
            "SELECT id, title, done FROM tasks WHERE id = ?",
            (created_id,),
        ).fetchone()

    assert row is not None
    assert row[1] == "Persistent task"