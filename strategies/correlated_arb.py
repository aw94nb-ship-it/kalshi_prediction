"""
Strategy 2 — Correlated Markets Arbitrage

Within an event, sort by yes_ask. A harder condition (e.g. price > 50bps)
should always have a lower or equal yes_ask than an easier condition
(price > 25bps). Any inversion is a potential mispricing.
"""

from typing import Any, Dict, List
from collections import defaultdict


def run(markets: List[Dict], **_kwargs: Any) -> List[Dict]:
    """
    Groups markets by event_ticker and flags pricing inversions where
    a market with a higher yes_ask is paired with a market whose title
    implies a stricter/harder condition but trades at a lower price.

    Heuristic: within an event group, sort by yes_ask ascending and flag
    any pair where the implied numeric threshold in the title is inverted
    relative to the price ordering.
    """
    # Group by event_ticker
    groups: Dict[str, List[Dict]] = defaultdict(list)
    for m in markets:
        event_ticker = m.get("event_ticker") or m.get("ticker", "")
        groups[event_ticker].append(m)

    signals = []
    for event_ticker, group in groups.items():
        if len(group) < 2:
            continue

        # Filter to markets with valid yes_ask
        valid = [m for m in group if m.get("yes_ask") is not None]
        if len(valid) < 2:
            continue

        # Extract numeric threshold from title for ordering
        import re
        def extract_number(m: Dict) -> float:
            title = m.get("title", "") or m.get("ticker", "")
            nums = re.findall(r"[-+]?\d+\.?\d*", title)
            return float(nums[-1]) if nums else 0.0

        valid.sort(key=extract_number)

        # Now check: as threshold increases, yes_ask should decrease
        # (harder threshold → lower probability → lower yes_ask)
        for i in range(len(valid) - 1):
            low_thresh = valid[i]
            high_thresh = valid[i + 1]

            thresh_low = extract_number(low_thresh)
            thresh_high = extract_number(high_thresh)

            if thresh_low == thresh_high:
                continue

            price_low = low_thresh["yes_ask"]
            price_high = high_thresh["yes_ask"]

            # Harder condition (high_thresh) should have lower yes_ask
            # Inversion: high_thresh.yes_ask > low_thresh.yes_ask
            if price_high > price_low:
                mispricing = price_high - price_low
                signals.append({
                    "event_ticker": event_ticker,
                    "easier_ticker": low_thresh.get("ticker", ""),
                    "easier_title": low_thresh.get("title", ""),
                    "easier_yes_ask": price_low,
                    "harder_ticker": high_thresh.get("ticker", ""),
                    "harder_title": high_thresh.get("title", ""),
                    "harder_yes_ask": price_high,
                    "mispricing_cents": mispricing,
                })

    signals.sort(key=lambda x: x["mispricing_cents"], reverse=True)
    return signals
