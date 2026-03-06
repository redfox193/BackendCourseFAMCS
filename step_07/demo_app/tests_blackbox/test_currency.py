from __future__ import annotations


async def test_currency_multiple_symbols_with_mockserver(service_client, mock_currency_api):
    mock_currency_api.set_price_response(
        {
            "bitcoin": {"usd": 50000.0},
            "ethereum": {"usd": 3000.0},
            "solana": {"usd": 100.0},
        }
    )
    response = await service_client.get(
        "/currency",
        params={"symbols": ["BTC", "ETH", "SOL"]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "BTC": 50000.0,
        "ETH": 3000.0,
        "SOL": 100.0,
    }
    assert mock_currency_api.last_query is not None
    assert mock_currency_api.last_query["ids"] == "bitcoin,ethereum,solana"
    assert mock_currency_api.last_query["vs_currencies"] == "usd"


async def test_currency_unknown_symbol_returns_zero(service_client, mock_currency_api):
    mock_currency_api.set_price_response({})
    response = await service_client.get("/currency", params={"symbols": ["UNKNOWN"]})
    assert response.status_code == 200
    assert response.json() == {"UNKNOWN": 0.0}
    assert mock_currency_api.last_query is not None
    assert mock_currency_api.last_query["ids"] == "unknown"


async def test_currency_empty_symbols_without_external_call(service_client, mock_currency_api):
    mock_currency_api.set_price_response({"bitcoin": {"usd": 1.0}})
    response = await service_client.get("/currency", params={"symbols": []})
    assert response.status_code == 200
    assert response.json() == {}
    # При пустом symbols сервис не должен ходить во внешний API.
    assert mock_currency_api.last_query is None
