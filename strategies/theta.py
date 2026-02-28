"""
Strategy 6 — Resolution Theta

Signal: close_time within THETA_DAYS_TO_CLOSE days AND yes_ask >= THETA_MIN_YES_PRICE
Opportunity: sell No contracts (cheap, near-guaranteed win if yes_ask is very high).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List
import config


def _parse_dt(dt_str: str) -> datetime:
    """Parse ISO-8601 datetime string to a timezone-aware datetime."""
    if not dt_str:
        raise ValueError("empty datetime string")
    # Handle various formats from the API
    for fmt in (
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%dT%H:%M:%S",
    ):
        try:
            dt = datetime.strptime(dt_str, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse datetime: {dt_str!r}")


def run(markets: List[Dict], **_kwargs: Any) -> List[Dict]:
    signals = []
    now = datetime.now(timezone.utc)

    for m in markets:
        yes_ask = m.get("yes_ask")
        if yes_ask is None or yes_ask < config.THETA_MIN_YES_PRICE:
            continue

        close_time_str = m.get("close_time") or m.get("expiration_time")
        if not close_time_str:
            continue

        try:
            close_dt = _parse_dt(close_time_str)
        except ValueError:
            continue

        delta = close_dt - now
        days_left = delta.total_seconds() / 86400

        if 0 < days_left <= config.THETA_DAYS_TO_CLOSE:
            no_ask = m.get("no_ask", 100 - yes_ask)
            hours_left = delta.total_seconds() / 3600
            signals.append({
                "ticker": m.get("ticker", ""),
                "title": m.get("title", ""),
                "yes_ask": yes_ask,
                "no_ask": no_ask,
                "days_left": round(days_left, 2),
                "hours_left": round(hours_left, 1),
                "close_time": close_time_str,
            })

    signals.sort(key=lambda x: x["yes_ask"], reverse=True)
    return signals
