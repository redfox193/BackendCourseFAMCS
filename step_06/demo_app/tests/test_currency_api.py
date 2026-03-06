"""
Интеграционные тесты для эндпоинта /currency.
Внешний сервис курсов подменён на FakeCurrencyRatesClient (conftest).
"""
from fastapi.testclient import TestClient


def test_currency_single_symbol(client: TestClient):
    """GET /currency?symbols=BTC — один тикер."""
    response = client.get("/currency", params={"symbols": ["BTC"]})
    assert response.status_code == 200
    assert response.json() == {"BTC": 50000.0}


def test_currency_multiple_symbols(client: TestClient):
    """GET /currency?symbols=BTC&symbols=ETH&symbols=SOL — несколько тикеров."""
    response = client.get("/currency", params={"symbols": ["BTC", "ETH", "SOL"]})
    assert response.status_code == 200
    data = response.json()
    assert data["BTC"] == 50000.0
    assert data["ETH"] == 3000.0
    assert data["SOL"] == 100.0


def test_currency_unknown_symbol_returns_zero(client: TestClient):
    """Неизвестный тикер возвращает 0 (поведение FakeCurrencyRatesClient)."""
    response = client.get("/currency", params={"symbols": ["UNKNOWN"]})
    assert response.status_code == 200
    assert response.json() == {"UNKNOWN": 0.0}


def test_currency_empty_symbols(client: TestClient):
    """GET /currency без symbols или с пустым списком — пустой объект."""
    response = client.get("/currency", params={"symbols": []})
    assert response.status_code == 200
    assert response.json() == {}
