"""In-memory rolling time-series store for per-ticker price history."""

from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import config

# { ticker: deque([(timestamp, yes_ask, volume), ...], maxlen=WINDOW) }
_store: Dict[str, deque] = {}


def update(markets: List[dict]) -> None:
    """Ingest the latest poll snapshot for all markets."""
    ts = datetime.utcnow()
    for m in markets:
        ticker = m.get("ticker")
        if not ticker:
            continue
        yes_ask = m.get("yes_ask") or m.get("last_price") or 0
        volume = m.get("volume") or m.get("volume_24h") or 0
        if ticker not in _store:
            _store[ticker] = deque(maxlen=config.DATA_STORE_WINDOW)
        _store[ticker].append((ts, yes_ask, volume))


def get_history(ticker: str) -> List[Tuple[datetime, int, int]]:
    """Return the rolling history list for a ticker (oldest first)."""
    return list(_store.get(ticker, []))


def latest(ticker: str) -> Optional[Tuple[datetime, int, int]]:
    """Return the most recent snapshot for a ticker."""
    buf = _store.get(ticker)
    if buf:
        return buf[-1]
    return None


def oldest(ticker: str) -> Optional[Tuple[datetime, int, int]]:
    """Return the oldest snapshot still in the window."""
    buf = _store.get(ticker)
    if buf:
        return buf[0]
    return None


def clear() -> None:
    _store.clear()
