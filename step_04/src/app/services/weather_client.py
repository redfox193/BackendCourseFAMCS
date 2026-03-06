"""Клиент для получения данных о погоде из внешнего API."""
import httpx
from app.config import get_api_base_url


class WeatherClient:
    """Синхронный клиент погоды."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or get_api_base_url()

    def get_weather(self, city: str) -> dict:
        """Получить погоду для города. Возвращает dict с ключами temp, condition."""
        response = httpx.get(f"{self.base_url}/weather", params={"city": city})
        response.raise_for_status()
        return response.json()


async def fetch_weather_async(city: str) -> dict:
    """Асинхронная функция получения погоды."""
    async with httpx.AsyncClient() as client:
        base_url = get_api_base_url()
        response = await client.get(f"{base_url}/weather", params={"city": city})
        response.raise_for_status()
        return response.json()
