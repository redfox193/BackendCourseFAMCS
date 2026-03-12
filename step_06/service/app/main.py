from contextlib import asynccontextmanager

from fastapi import FastAPI
import random

import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/random")
async def get_random():
    value = random.randint(1, 100)
    db.save_number(value)
    return {"number": value}


@app.get("/random/last")
async def get_last_random():
    return {"items": db.get_last_numbers(10)}
