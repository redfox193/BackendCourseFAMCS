"""Общие фикстуры для всех тестов в step_03. Автоматически обнаруживаются pytest."""
import pytest


@pytest.fixture
def shared_config():
    """Фикстура, доступная всем тестам без импорта."""
    return {"env": "test", "debug": True}


@pytest.fixture
def sample_user():
    """Типичный пользователь для тестов."""
    return {"id": 1, "name": "Alice", "email": "alice@example.com"}
