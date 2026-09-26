from fastapi.testclient import TestClient
from main import app, tasks

client = TestClient(app)


def reset_tasks():
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Learn FastAPI", "done": False},
        {"id": 2, "title": "Build CRUD API", "done": False},
        {"id": 3, "title": "Test with Swagger", "done": False},
    ])


def setup_function():
    reset_tasks()


def test_root_and_health():
    assert client.get("/").status_code == 200
    assert client.get("/health").json() == {"status": "ok"}


def test_read_tasks_and_404():
    assert client.get("/tasks").status_code == 200
    assert client.get("/tasks/1").json()["title"] == "Learn FastAPI"
    response = client.get("/tasks/99")
    assert response.status_code == 404
    assert response.json() == {"error": "Task 99 not found"}


def test_create_validation_and_success():
    response = client.post("/tasks", json={"title": "Buy milk"})
    assert response.status_code == 201
    assert response.json() == {"id": 4, "title": "Buy milk", "done": False}

    invalid = client.post("/tasks", json={})
    assert invalid.status_code == 400

    empty = client.post("/tasks", json={"title": "   "})
    assert empty.status_code == 400


def test_update_and_delete():
    response = client.put("/tasks/1", json={"title": "Learn FastAPI deeply"})
    assert response.status_code == 200
    assert response.json()["title"] == "Learn FastAPI deeply"

    response = client.put("/tasks/1", json={"done": True})
    assert response.status_code == 200
    assert response.json()["done"] is True

    empty = client.put("/tasks/1", json={})
    assert empty.status_code == 400

    missing = client.put("/tasks/99", json={"done": True})
    assert missing.status_code == 404

    deleted = client.delete("/tasks/1")
    assert deleted.status_code == 204
    assert client.get("/tasks/1").status_code == 404

    delete_missing = client.delete("/tasks/99")
    assert delete_missing.status_code == 404
