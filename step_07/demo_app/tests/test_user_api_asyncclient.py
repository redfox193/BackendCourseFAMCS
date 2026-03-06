"""
Те же сценарии, что в test_user_api.py, но через httpx.AsyncClient (без TestClient).
"""
import pytest
import httpx


async def test_health_async(async_client: httpx.AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_list_users_empty_async(async_client: httpx.AsyncClient):
    """GET /user — пустой список до создания пользователей."""
    response = await async_client.get("/user")
    assert response.status_code == 200
    assert response.json() == []


async def test_create_user_async(async_client: httpx.AsyncClient):
    """POST /user — создание пользователя."""
    response = await async_client.post(
        "/user",
        json={"username": "alice", "name": "Alice Smith"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alice"
    assert data["name"] == "Alice Smith"
    assert "id" in data and isinstance(data["id"], int)


async def test_get_user_after_create_async(async_client: httpx.AsyncClient):
    """GET /user/{id} — получение созданного пользователя."""
    create = await async_client.post("/user", json={"username": "bob", "name": "Bob Brown"})
    assert create.status_code == 201
    user_id = create.json()["id"]

    response = await async_client.get(f"/user/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"id": user_id, "username": "bob", "name": "Bob Brown"}


async def test_get_user_not_found_async(async_client: httpx.AsyncClient):
    """GET /user/{id} — 404 для несуществующего id."""
    response = await async_client.get("/user/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


async def test_list_users_after_creates_async(async_client: httpx.AsyncClient):
    """GET /user — список после создания нескольких пользователей."""
    await async_client.post("/user", json={"username": "u1", "name": "User One"})
    await async_client.post("/user", json={"username": "u2", "name": "User Two"})

    response = await async_client.get("/user")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2
    usernames = {u["username"] for u in users}
    assert usernames == {"u1", "u2"}


async def test_update_user_async(async_client: httpx.AsyncClient):
    """PUT /user/{id} — обновление пользователя."""
    create = await async_client.post("/user", json={"username": "old", "name": "Old Name"})
    assert create.status_code == 201
    user_id = create.json()["id"]

    response = await async_client.put(
        f"/user/{user_id}",
        json={"username": "new", "name": "New Name"},
    )
    assert response.status_code == 200
    assert response.json() == {"id": user_id, "username": "new", "name": "New Name"}


async def test_update_user_partial_async(async_client: httpx.AsyncClient):
    """PUT /user/{id} — частичное обновление (только name)."""
    create = await async_client.post("/user", json={"username": "keep", "name": "Old"})
    user_id = create.json()["id"]

    response = await async_client.put(f"/user/{user_id}", json={"name": "Updated"})
    assert response.status_code == 200
    assert response.json()["username"] == "keep"
    assert response.json()["name"] == "Updated"


async def test_update_user_not_found_async(async_client: httpx.AsyncClient):
    """PUT /user/{id} — 404 для несуществующего id."""
    response = await async_client.put("/user/99999", json={"name": "X"})
    assert response.status_code == 404


async def test_delete_user_async(async_client: httpx.AsyncClient):
    """DELETE /user/{id} — удаление пользователя."""
    create = await async_client.post("/user", json={"username": "del", "name": "To Delete"})
    user_id = create.json()["id"]

    response = await async_client.delete(f"/user/{user_id}")
    assert response.status_code == 204

    get_response = await async_client.get(f"/user/{user_id}")
    assert get_response.status_code == 404


async def test_delete_user_not_found_async(async_client: httpx.AsyncClient):
    """DELETE /user/{id} — 404 для несуществующего id."""
    response = await async_client.delete("/user/99999")
    assert response.status_code == 404


async def test_create_user_validation_empty_username_async(async_client: httpx.AsyncClient):
    """POST /user — 422 при пустом username."""
    response = await async_client.post("/user", json={"username": "", "name": "Some"})
    assert response.status_code == 422


async def test_create_user_validation_missing_fields_async(async_client: httpx.AsyncClient):
    """POST /user — 422 при отсутствии полей."""
    response = await async_client.post("/user", json={})
    assert response.status_code == 422
