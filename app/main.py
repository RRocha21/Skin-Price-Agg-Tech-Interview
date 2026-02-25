from fastapi import FastAPI, Query
from .models import PricesResponse
from .services import get_prices

app = FastAPI(title="Skin Price Aggregator")

@app.get("/prices", response_model=PricesResponse)
async def prices(item_name: str = Query(..., min_length=1)):
    return await get_prices(item_name)

@app.get("/")
def root():
    return {"message": "Skin API", "endpoint": "/prices?item_name=AK-47 | Redline"}
