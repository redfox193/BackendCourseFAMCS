"""Тесты, использующие фикстуры из conftest.py. Импорт не требуется."""


def test_shared_config(shared_config):
    assert shared_config["env"] == "test"
    assert shared_config["debug"] is True


def test_sample_user(sample_user):
    assert sample_user["id"] == 1
    assert sample_user["name"] == "Alice"
    assert sample_user["email"] == "alice@example.com"


def test_user_and_config(sample_user, shared_config):
    # можно комбинировать несколько фикстур
    assert sample_user["name"] == "Alice"
    assert shared_config["env"] == "test"
