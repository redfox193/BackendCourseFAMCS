import os


def get_database_url() -> str:
    return os.environ["DATABASE_URL"]


def get_currency_api_base_url() -> str:
    return os.environ.get("CURRENCY_API_BASE_URL", "https://api.coingecko.com/api/v3")
