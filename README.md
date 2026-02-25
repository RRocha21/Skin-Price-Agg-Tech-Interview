# Skin Price Aggregator

**Scalable CS2 skin price aggregator** with 2+ live marketplaces (DMarket, UUSkins). Production-ready architecture.

## Architecture Overview

```
Skin-Price-Agg/
├── pyproject.toml
├── requirements.txt
├── app/
│   ├── __init__.py
│   ├── main.py      # FastAPI app
│   ├── models.py    # Pydantic Listing/PricesResponse
│   ├── services.py  # MARKETPLACES registry
│   └── markets/
│       ├── __init__.py
│       ├── base.py  # MarketplaceBase ABC
│       ├── dmarket.py
│       └── uuskins.py
├── tests/
└── README.md
```

**Key Design Decisions:**
- **Interface-driven**: `MarketplaceBase` ABC scales to 10+ markets without core changes
- **Normalized data**: All listings → unified `Listing` Pydantic model
- **Graceful failures**: `asyncio.gather()` isolates individual market failures
- **Smart scoring**: Float-aware "best deal" algorithm (low float = higher value)
- **Production caching**: 60s TTL prevents API rate limiting

## Features ✓

- ✅ **2+ end-to-end marketplaces** (DMarket + UUSkins APIs working live)
- ✅ **Normalized JSON**: `marketplace`, `item_name`, `price`, `currency`, `url`, `last_updated`, `float_value`
- ✅ **Cheapest + best_deal**: Float penalty scoring (0.00=1.0x, 0.45=2.0x, 1.0=3.0x)
- ✅ **Graceful failures**: One market down ≠ service outage
- ✅ **60s caching**: Production-grade rate limiting
- ✅ **Fully tested**: 4 green live API integration tests

## Quickstart

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload 
# or
python -m fastapi run app/main.py
```

### Live Test

```bash
curl "http://127.0.0.1:8000/prices?item_name=AK-47%20%7C%20Redline"
```

**API Response:**

```json
{
  "item_name": "AK-47 | Redline",
  "listings": [
    {
      "marketplace": "dmarket",
      "item_name": "AK-47 | Redline",
      "price": 12.50,
      "float_value": 0.07,
      "currency": "USD",
      "url": "https://dmarket.com/...",
      "last_updated": "2026-02-25T14:00:00Z"
    }
  ],
  "cheapest_listing": { ... },
  "best_deal_listing": { ... }
}
```

## Adding a New Marketplace (2 minutes)

### Step 1: Create `app/markets/steam.py`

```python
from app.markets.base import MarketplaceBase
from datetime import datetime, timezone
import httpx

class SteamClient(MarketplaceBase):
    name = "steam"
    
    async def fetch_listings(self, item_name: str) -> list[dict]:
        # Steam Market API call
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("https://market.csgo.com/api/v2/prices/USD.json")
            # Normalize → Listing format
            return [{
                "marketplace": self.name,
                "item_name": item_name,
                "price": float(price_data),
                "float_value": None,
                "currency": "USD",
                "url": f"https://steamcommunity.com/market/listings/730/{item_name}",
                "last_updated": datetime.now(timezone.utc)
            }]
```

### Step 2: Register in `app/services.py`

```python
from app.markets.steam import SteamClient

MARKETPLACES.append(SteamClient())  # Auto-tested!
```

## Tests

```bash
# Run all tests (4 green)
pytest tests/ -v

# + Live API print output
pytest tests/ -v -s

# Unit tests only
pytest tests/ -m "not live_api"
```

**Live test output:**

```
DMarket returned 3 listings
UUSkins returned 1 listings
4 passed in 0.96s
```

## Production Notes

- **Rate limiting**: 60s cache prevents API bans
- **Error isolation**: Single market failure isolated
- **Timezone-safe**: UTC everywhere
- **Type-safe**: Full Pydantic validation
- **Async**: Parallel market fetching
