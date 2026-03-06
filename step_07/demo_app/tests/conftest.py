"""
Фикстуры для интеграционных тестов.
Мокаем зависимости на уровне протокола: подменяем репозиторий и клиент валют
так, чтобы запросы не уходили в реальную БД и во внешний сервис.
"""
import pytest
import httpx
from fastapi.testclient import TestClient

from app.main import app
from app.deps import get_user_repository, get_currency_client
from tests.fakes import FakeUserRepository, FakeCurrencyRatesClient


@pytest.fixture
def user_repo():
    return FakeUserRepository()


@pytest.fixture
def currency_client():
    return FakeCurrencyRatesClient({"BTC": 50000.0, "ETH": 3000.0, "SOL": 100.0})


@pytest.fixture
def app_with_overrides(user_repo, currency_client):
    """Приложение с подменёнными зависимостями: фейковые БД и API."""
    app.dependency_overrides[get_user_repository] = lambda: user_repo
    app.dependency_overrides[get_currency_client] = lambda: currency_client
    yield app
    app.dependency_overrides.clear()


# -------- AsyncClient ---------

@pytest.fixture
async def async_client(app_with_overrides):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app_with_overrides),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest.fixture
async def simple_async_client():
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


# -------- TestClient ---------

@pytest.fixture
def client(app_with_overrides):
    return TestClient(app_with_overrides)