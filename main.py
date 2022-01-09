# main.py

from fastapi import FastAPI
from nft import get_floor_price

app = FastAPI()

@app.get("/")
async def root():
    return {"message": get_floor_price('crypto-dino-v3')}
