from fastapi import FastAPI
import random

app = FastAPI()


@app.get("/random")
async def get_random():
    return {"number": random.randint(1, 100)}
