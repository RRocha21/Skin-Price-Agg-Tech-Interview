import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timezone
from typing import List, Dict, Any
import httpx
from app.markets.dmarket import DMarketClient
from app.markets.uuskins import UUSkinsClient

# ABSOLUTE imports
from app.services import get_prices, MARKETPLACES
from app.models import Listing

@pytest.fixture
def mock_listing(request) -> Dict[str, Any]:
    """Generic mock listing - pass marketplace name."""
    marketplace = getattr(request, 'param', 'dmarket')
    return {
        "marketplace": marketplace,
        "item_name": "AK-47",
        "price": 10.0,
        "float_value": 0.07,
        "currency": "USD",
        "url": f"https://{marketplace}.com/item",
        "last_updated": datetime.now(timezone.utc)
    }

@pytest.mark.asyncio
async def test_get_prices_multiple_markets(mock_listing):
    mock_dmarket = AsyncMock(fetch_listings=AsyncMock(return_value=[mock_listing]))  # Uses default 'dmarket'
    mock_uuskins = AsyncMock(fetch_listings=AsyncMock(side_effect=Exception("down")))
    
    with patch("app.services.MARKETPLACES", [mock_dmarket, mock_uuskins]):
        result = await get_prices("AK-47")
    
    assert len(result.listings) == 1
    

@pytest.mark.asyncio
@pytest.mark.live_api
async def test_dmarket_fetch_listings_live():
    """Calls DMarketClient.fetch_listings LIVE - no mocks."""
    client = DMarketClient()
    listings = await client.fetch_listings("AK-47 | Redline")
    
    print(f"DMarket returned {len(listings)} listings")  # Debug
    
    # Graceful even if empty
    assert isinstance(listings, list)
    for listing in listings:
        assert listing["marketplace"] == "dmarket"
        assert isinstance(listing["price"], (int, float))
        assert "dmarket.com" in listing["url"]
        assert listing["currency"] == "USD"

@pytest.mark.asyncio
@pytest.mark.live_api
async def test_uuskins_fetch_listings_live():
    """Calls UUSkinsClient.fetch_listings LIVE."""
    client = UUSkinsClient()
    listings = await client.fetch_listings("USP-S | Printstream")
    
    print(f"UUSkins returned {len(listings)} listings")
    
    assert isinstance(listings, list)
    for listing in listings:
        assert listing["marketplace"] == "uuskins"
        assert isinstance(listing["price"], (int, float))
        assert "uuskins.com" in listing["url"]

@pytest.mark.asyncio
async def test_dmarket_handles_errors():
    """Tests error handling with invalid item."""
    client = DMarketClient()
    listings = await client.fetch_listings("INVALID_SKIN_999")
    
    # Should return [] not crash
    assert isinstance(listings, list) and len(listings) == 0