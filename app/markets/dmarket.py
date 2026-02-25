import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.markets.base import MarketplaceBase

class DMarketClient(MarketplaceBase):
    name = "dmarket"

    async def fetch_listings(self, item_name: str) -> List[Dict[str, Any]]:
        params = {
            "side": "market",
            "orderBy": "price",
            "orderDir": "asc",
            "title": item_name,
            "currency": "USD",
            "limit": 50,
            "gameid": "a8db"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.dmarket.com/exchange/v1/market/items",
                params=params
            )
            resp.raise_for_status()
            data = resp.json()
            objects = data.get('objects', [])
            if objects:
                listings = []

                for item in objects:
                    rawPrice = item.get('price').get('USD')
                    price = float(rawPrice) / 100

                    listings.append({
                        "marketplace": self.name,
                        "item_name": item_name,
                        "price": round(price, 2),
                        "float_value": item.get('extra').get('floatValue'),
                        "currency": "USD",
                        "url": f"https://dmarket.com/ingame-items/item-list/csgo-skins?userOfferId={item.get('extra').get('linkId')}",
                        "last_updated": datetime.now(timezone.utc),
                    })
                return listings
            return []  # No listings