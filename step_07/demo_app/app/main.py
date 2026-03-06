"""FastAPI приложение: CRUD пользователей и курсы валют."""
from fastapi import FastAPI

from app.deps import get_currency_client, get_user_repository
from app.routers import currency, user

app = FastAPI(title="Demo API", version="0.1.0")

app.include_router(user.router)
app.include_router(currency.router)


@app.get("/health")
def health():
    return {"status": "ok"}
