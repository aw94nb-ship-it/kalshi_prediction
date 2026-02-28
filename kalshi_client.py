"""Thin HTTP wrapper for the Kalshi public REST API."""

import requests
from typing import Any, Dict, List, Optional
import config


class KalshiClient:
    def __init__(self, base_url: str = config.BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        url = f"{self.base_url}{path}"
        resp = self.session.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_markets(
        self,
        limit: int = 200,
        status: str = "active",
        cursor: Optional[str] = None,
    ) -> List[Dict]:
        """Fetch active markets, auto-paginating up to `limit` total."""
        markets: List[Dict] = []
        params: Dict[str, Any] = {"limit": min(limit, 200), "status": status}
        if cursor:
            params["cursor"] = cursor

        while True:
            data = self._get("/markets", params=params)
            batch = data.get("markets", [])
            markets.extend(batch)
            next_cursor = data.get("cursor")
            if not next_cursor or len(markets) >= limit:
                break
            params["cursor"] = next_cursor

        return markets[:limit]

    def get_market(self, ticker: str) -> Dict:
        """Fetch a single market by ticker."""
        data = self._get(f"/markets/{ticker}")
        return data.get("market", data)

    def get_orderbook(self, ticker: str, depth: int = 10) -> Dict:
        """
        Fetch order book for a market.
        Returns dict with 'yes' and 'no' lists of [price, qty] pairs.
        """
        data = self._get(f"/markets/{ticker}/orderbook", params={"depth": depth})
        return data.get("orderbook", {"yes": [], "no": []})

    def get_events(self, limit: int = 100, status: str = "open") -> List[Dict]:
        """Fetch events."""
        data = self._get("/events", params={"limit": limit, "status": status})
        return data.get("events", [])
