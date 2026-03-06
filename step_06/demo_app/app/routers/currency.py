from fastapi import APIRouter, Depends, Query

from app.deps import get_currency_client
from app.services.currency import CurrencyRatesClient

router = APIRouter(prefix="/currency", tags=["currency"])


@router.get("")
def get_currency_rates(
    symbols: list[str] = Query(default=[], description="Список тикеров, например BTC,ETH,SOL"),
    client: CurrencyRatesClient = Depends(get_currency_client),
):
    if not symbols:
        return {}
    return client.get_rates_usd(symbols)
