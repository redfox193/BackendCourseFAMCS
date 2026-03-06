"""Зависимости приложения — реальные реализации (PostgreSQL, внешний API)."""
from app.config import get_currency_api_base_url, get_database_url
from app.repositories.user import PostgresUserRepository, UserRepository
from app.services.currency import CoinGeckoCurrencyRatesClient, CurrencyRatesClient


def get_user_repository() -> UserRepository:
    return PostgresUserRepository(get_database_url())


def get_currency_client() -> CurrencyRatesClient:
    return CoinGeckoCurrencyRatesClient(get_currency_api_base_url())
