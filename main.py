# main.py

from fastapi import FastAPI
from nft import get_floor_price
from typing import Optional


app = FastAPI()

@app.get("/")
async def root(collection: str, prop: Optional[str] = None, prop_val: Optional[str] = None):
    if prop:
        if not prop_val:
            return {"success":false, 'detail': 'If specifying property, must specify value'}
    return {"message": get_floor_price(collection, prop, prop_val)}
