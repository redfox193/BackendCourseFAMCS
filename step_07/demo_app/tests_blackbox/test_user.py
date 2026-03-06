from __future__ import annotations

import pytest


@pytest.fixture
def insert_users(pgsql):
    """Предзаполняем БД данными перед тестом."""
    cursor = pgsql["user_db"].cursor()
    cursor.execute('TRUNCATE TABLE "user" RESTART IDENTITY')
    cursor.execute(
        'INSERT INTO "user" (username, name) VALUES (%s, %s), (%s, %s)',
        ("john", "John Doe", "kate", "Kate Brown"),
    )


async def test_list_users_from_seed(service_client, insert_users):
    response = await service_client.get("/user")
    assert response.status_code == 200
    data = response.json()
    assert [user["username"] for user in data] == ["john", "kate"]


async def test_create_user_persists_in_db(service_client, pgsql):
    response = await service_client.post(
        "/user",
        json={"username": "alice", "name": "Alice Smith"},
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["username"] == "alice"
    assert payload["name"] == "Alice Smith"


async def test_update_and_delete_user(service_client, insert_users):
    update_resp = await service_client.put(
        "/user/1",
        json={"name": "John Updated"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "John Updated"

    delete_resp = await service_client.delete("/user/1")
    assert delete_resp.status_code == 204

    get_resp = await service_client.get("/user/1")
    assert get_resp.status_code == 404
