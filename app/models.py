from datetime import datetime
from pydantic import BaseModel, HttpUrl
from typing import List

class Listing(BaseModel):
    marketplace: str
    item_name: str
    price: float
    float_value: float | None = None
    currency: str
    url: HttpUrl
    last_updated: datetime

class PricesResponse(BaseModel):
    item_name: str
    listings: List[Listing]
    cheapest_listing: Listing | None = None
    best_deal_listing: Listing | None = None
