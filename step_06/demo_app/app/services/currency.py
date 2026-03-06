"""Клиент курсов валют — абстракция над внешним API."""
from typing import Protocol

import httpx


class CurrencyRatesClient(Protocol):

    def get_rates_usd(self, symbols: list[str]) -> dict[str, float]:
        ...


COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "USDT": "tether",
    "USDC": "usd-coin",
}


class CoinGeckoCurrencyRatesClient:

    def __init__(self, base_url: str):
        self._base_url = base_url.rstrip("/")

    def get_rates_usd(self, symbols: list[str]) -> dict[str, float]:
        if not symbols:
            return {}

        ids = [COINGECKO_IDS.get(s.upper(), s.lower()) for s in symbols]
        ids_param = ",".join(ids)
        url = f"{self._base_url}/simple/price"
        params = {"ids": ids_param, "vs_currencies": "usd"}
        with httpx.Client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        result: dict[str, float] = {}
        for sym in symbols:
            cg_id = COINGECKO_IDS.get(sym.upper(), sym.lower())
            if cg_id in data and "usd" in data[cg_id]:
                result[sym] = float(data[cg_id]["usd"])
            else:
                result[sym] = 0.0
        return result
