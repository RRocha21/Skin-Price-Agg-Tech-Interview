import asyncio
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple

from .models import Listing, PricesResponse
from app.markets.base import MarketplaceBase

# Registry (populate from app.main)
from app.markets.dmarket import DMarketClient
from app.markets.uuskins import UUSkinsClient

MARKETPLACES: List[MarketplaceBase] = [
    DMarketClient(),
    UUSkinsClient(),
]
CACHE: Dict[str, Tuple[datetime, PricesResponse]] = {}
CACHE_TTL = timedelta(seconds=60)


def float_penalty(float_val: float) -> float:
    """Lower float = lower penalty (better). Caps extreme floats."""
    """Price multiplier: 0.00=1.0x (FN), 0.15=1.3x (MW), 0.45=2.0x (WW), 1.0=3.0x (BS)"""
    if float_val is None:
        return 1.5  # Default poor float
    # Exponential penalty: 0.00=1.0x, 0.15=1.3x, 0.45=2.0x, 1.0=3.0x
    return 1.0 + min((float_val ** 1.5) * 2.0, 3.0)

async def get_prices(item_name: str) -> PricesResponse:
    key = item_name.strip().lower()
    now = datetime.now(timezone.utc)

    # Cache
    if key in CACHE:
        ts, cached = CACHE[key]
        if now - ts <= CACHE_TTL:
            return cached

    # Parallel fetch (fail independently)
    async def fetch(market):
        try:
            return await market.fetch_listings(item_name)
        except Exception as e:
            print(f"{market.name} failed: {e}")
            return []

    tasks = [fetch(m) for m in MARKETPLACES]
    results = await asyncio.gather(*tasks)
    listings_data = [item for sub in results for item in sub]
    listings = [Listing(**data) for data in listings_data]

    if listings:
        cheapest = min(listings, key=lambda l: l.price)
        best_deal = min(listings, key=lambda l: (
            l.price * float_penalty(l.float_value) * 
            (1.03 if l.marketplace == "uuskins" else 1),  # Marketplace factors -> uuskins has 3.2% deposit fee
        ))
        listings = sorted(listings, key=lambda l: l.price)
        
        resp = PricesResponse(
            item_name=item_name,
            listings=listings,
            cheapest_listing=cheapest,
            best_deal_listing=best_deal
        )
    else:
        resp = PricesResponse(item_name=item_name, listings=[])

    CACHE[key] = (now, resp)
    return resp