from fastapi.testclient import TestClient

def test_list_users_empty(client: TestClient):
    """GET /user — пустой список до создания пользователей."""
    response = client.get("/user")
    assert response.status_code == 200
    assert response.json() == []


def test_create_user(client: TestClient):
    """POST /user — создание пользователя."""
    response = client.post(
        "/user",
        json={"username": "alice", "name": "Alice Smith"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["name"] == "Alice Smith"
    assert "id" in data and isinstance(data["id"], int)


def test_get_user_after_create(client: TestClient):
    """GET /user/{id} — получение созданного пользователя."""
    create = client.post("/user", json={"username": "bob", "name": "Bob Brown"})
    assert create.status_code == 201
    user_id = create.json()["id"]

    response = client.get(f"/user/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"id": user_id, "username": "bob", "name": "Bob Brown"}


def test_get_user_not_found(client: TestClient):
    """GET /user/{id} — 404 для несуществующего id."""
    response = client.get("/user/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_list_users_after_creates(client: TestClient):
    """GET /user — список после создания нескольких пользователей."""
    client.post("/user", json={"username": "u1", "name": "User One"})
    client.post("/user", json={"username": "u2", "name": "User Two"})

    response = client.get("/user")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2
    usernames = {u["username"] for u in users}
    assert usernames == {"u1", "u2"}


def test_update_user(client: TestClient):
    """PUT /user/{id} — обновление пользователя."""
    create = client.post("/user", json={"username": "old", "name": "Old Name"})
    assert create.status_code == 201
    user_id = create.json()["id"]

    response = client.put(
        f"/user/{user_id}",
        json={"username": "new", "name": "New Name"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": user_id, "username": "new", "name": "New Name"}


def test_update_user_partial(client: TestClient):
    """PUT /user/{id} — частичное обновление (только name)."""
    create = client.post("/user", json={"username": "keep", "name": "Old"})
    user_id = create.json()["id"]

    response = client.put(f"/user/{user_id}", json={"name": "Updated"})
    assert response.status_code == 200
    assert response.json()["username"] == "keep"
    assert response.json()["name"] == "Updated"


def test_update_user_not_found(client: TestClient):
    """PUT /user/{id} — 404 для несуществующего id."""
    response = client.put("/user/99999", json={"name": "X"})
    assert response.status_code == 404


def test_delete_user(client: TestClient):
    """DELETE /user/{id} — удаление пользователя."""
    create = client.post("/user", json={"username": "del", "name": "To Delete"})
    user_id = create.json()["id"]

    response = client.delete(f"/user/{user_id}")
    assert response.status_code == 204

    get_response = client.get(f"/user/{user_id}")
    assert get_response.status_code == 404


def test_delete_user_not_found(client: TestClient):
    """DELETE /user/{id} — 404 для несуществующего id."""
    response = client.delete("/user/99999")
    assert response.status_code == 404


def test_create_user_validation_empty_username(client: TestClient):
    """POST /user — 422 при пустом username."""
    response = client.post("/user", json={"username": "", "name": "Some"})
    assert response.status_code == 422


def test_create_user_validation_missing_fields(client: TestClient):
    """POST /user — 422 при отсутствии полей."""
    response = client.post("/user", json={})
    assert response.status_code == 422
