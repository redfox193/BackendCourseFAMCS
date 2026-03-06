import pytest
import httpx
import respx


CURRENCY_API_BASE_URL = "https://api.coingecko.com/api/v3"


async def test_currency_multiple_symbols_async(simple_async_client):
    with respx.mock(base_url=CURRENCY_API_BASE_URL) as respx_mock:  # контекстный менеджер [page:4]
        route = respx_mock.get("/simple/price").mock(
            return_value=httpx.Response(
                200,
                json={
                    "bitcoin": {"usd": 50000.0},
                    "ethereum": {"usd": 3000.0},
                    "solana": {"usd": 100.0},
                },
            )
        )

        response = await simple_async_client.get(
            "/currency",
            params={"symbols": ["BTC", "ETH", "SOL"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["BTC"] == 50000.0
        assert data["ETH"] == 3000.0
        assert data["SOL"] == 100.0

        assert route.called
        req = route.calls[0].request
        assert req.url.params["ids"] == "bitcoin,ethereum,solana"
        assert req.url.params["vs_currencies"] == "usd"


@pytest.mark.respx(base_url=CURRENCY_API_BASE_URL)
async def test_currency_multiple_symbols_async(simple_async_client, respx_mock):
    route = respx_mock.get("/simple/price").mock(
        return_value=httpx.Response(
            200,
            json={
                "bitcoin": {"usd": 50000.0},
                "ethereum": {"usd": 3000.0},
                "solana": {"usd": 100.0},
            },
        )
    )

    response = await simple_async_client.get(
        "/currency",
        params={"symbols": ["BTC", "ETH", "SOL"]},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["BTC"] == 50000.0
    assert data["ETH"] == 3000.0
    assert data["SOL"] == 100.0

    req = route.calls[0].request
    assert req.url.params["ids"] == "bitcoin,ethereum,solana"
    assert req.url.params["vs_currencies"] == "usd"


@pytest.mark.respx(base_url=CURRENCY_API_BASE_URL)
async def test_currency_unknown_symbol_returns_zero_async(simple_async_client, respx_mock):
    route = respx_mock.get("/simple/price").mock(
        return_value=httpx.Response(200, json={})
    )

    response = await simple_async_client.get("/currency", params={"symbols": ["UNKNOWN"]})

    assert response.status_code == 200
    assert response.json() == {"UNKNOWN": 0.0}

    req = route.calls[0].request
    assert req.url.params["ids"] == "unknown"
    assert req.url.params["vs_currencies"] == "usd"


async def test_currency_empty_symbols_async(simple_async_client):
    response = await simple_async_client.get("/currency", params={"symbols": []})

    assert response.status_code == 200
    assert response.json() == {}
