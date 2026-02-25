import httpx
from datetime import datetime, timezone
from typing import List, Dict, Any
import secrets
import string
from app.markets.base import MarketplaceBase

def generate_base64_like_string():
    chars = string.ascii_letters + string.digits + '+/'
    random_part = ''.join(secrets.choice(chars) for _ in range(24))
    return random_part + '=='

class UUSkinsClient(MarketplaceBase):
    name = "uuskins"

    async def fetch_listings(self, item_name: str) -> List[Dict[str, Any]]:
        requestIdString = generate_base64_like_string()
        body_data = {
            "filterCondition": {},
            "searchKeyword": item_name,
            "pageIndex": 1,
            "pageSize": 50, # use the same number as other market
            "sortType": 2,  # Assumes price asc
            "language": "en",
            "appId": "730",
            "requestId": requestIdString
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.uuskins.com/api/vertex/commodity/query/sku/list",
                json=body_data
            )
            resp.raise_for_status()
            items = resp.json().get('data', {}).get('items', [])
            if items:
                listings = []
                for item in items:
                    price = float(item.get('price') or 0)

                    listings.append({
                        "marketplace": self.name,
                        "item_name": item_name,
                        "price": round(price, 2),
                        "float_value": item.get('wearValue'),
                        "currency": "USD",
                        "url": f"https://uuskins.com/items/{item.get('spuHashName', 'unknown')}", # not possible to get single listing so redirecting to entire item_name listings page
                        "last_updated": datetime.now(timezone.utc)
                    })
                return listings
            return []  # No listings