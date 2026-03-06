"""FastAPI приложение — сервис оповещений о погоде."""
from fastapi import FastAPI
from app.services.alert_service import check_and_alert, check_and_alert_async, get_weather_summary

app = FastAPI(title="Weather Alert Service")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/alerts/check")
def check_alert(city: str, user_id: str):
    """Проверить погоду и отправить алерт при необходимости."""
    return check_and_alert(city, user_id)


@app.post("/alerts/check-async")
async def check_alert_async(city: str, user_id: str):
    """Асинхронная проверка и алерт."""
    return await check_and_alert_async(city, user_id)


@app.get("/weather/{city}")
def weather_summary(city: str):
    """Краткое описание погоды для города."""
    return {"summary": get_weather_summary(city)}
