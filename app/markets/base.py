# app/markets/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class MarketplaceBase(ABC):
    name: str

    @abstractmethod
    async def fetch_listings(self, item_name: str) -> List[Dict[str, Any]]:
        """Fetch and return normalized listings for item_name."""
        ...