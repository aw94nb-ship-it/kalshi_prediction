"""
Strategy 4 — Market Making Wide Spread

Signal: yes_ask - yes_bid > WIDE_SPREAD_MIN_CENTS
Suggested orders: post bid at yes_bid + 1, ask at yes_ask - 1
"""

from typing import Any, Dict, List
import config


def run(markets: List[Dict], **_kwargs: Any) -> List[Dict]:
    signals = []

    for m in markets:
        yes_bid = m.get("yes_bid")
        yes_ask = m.get("yes_ask")
        if yes_bid is None or yes_ask is None:
            continue

        spread = yes_ask - yes_bid
        if spread > config.WIDE_SPREAD_MIN_CENTS:
            signals.append({
                "ticker": m.get("ticker", ""),
                "title": m.get("title", ""),
                "yes_bid": yes_bid,
                "yes_ask": yes_ask,
                "spread": spread,
                "suggested_bid": yes_bid + 1,
                "suggested_ask": yes_ask - 1,
                "volume": m.get("volume") or m.get("volume_24h") or 0,
            })

    signals.sort(key=lambda x: x["spread"], reverse=True)
    return signals
