import httpx


async def test_currency_single_symbol_async(async_client: httpx.AsyncClient):
    """GET /currency?symbols=BTC — один тикер."""
    response = await async_client.get("/currency", params={"symbols": ["BTC"]})
    assert response.status_code == 200
    assert response.json() == {"BTC": 50000.0}


async def test_currency_multiple_symbols_async(async_client: httpx.AsyncClient):
    """GET /currency?symbols=BTC&symbols=ETH&symbols=SOL — несколько тикеров."""
    response = await async_client.get("/currency", params={"symbols": ["BTC", "ETH", "SOL"]})
    assert response.status_code == 200
    data = response.json()
    assert data["BTC"] == 50000.0
    assert data["ETH"] == 3000.0
    assert data["SOL"] == 100.0


async def test_currency_unknown_symbol_returns_zero_async(async_client: httpx.AsyncClient):
    """Неизвестный тикер возвращает 0 (поведение FakeCurrencyRatesClient)."""
    response = await async_client.get("/currency", params={"symbols": ["UNKNOWN"]})
    assert response.status_code == 200
    assert response.json() == {"UNKNOWN": 0.0}


async def test_currency_empty_symbols_async(async_client: httpx.AsyncClient):
    """GET /currency без symbols или с пустым списком — пустой объект."""
    response = await async_client.get("/currency", params={"symbols": []})
    assert response.status_code == 200
    assert response.json() == {}
