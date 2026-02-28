"""
Strategy 3 — Order Book Imbalance

imbalance = sum(bid_qty) / (sum(bid_qty) + sum(ask_qty))
Signal: imbalance > OB_IMBALANCE_THRESHOLD (buy pressure)
     or imbalance < 1 - OB_IMBALANCE_THRESHOLD (sell pressure)
"""

from typing import Any, Dict, List
import config


def _side_totals(levels: List[List]) -> tuple:
    """Return (total_qty, best_price) from a list of [price, qty] pairs."""
    total = sum(int(level[1]) for level in levels if len(level) >= 2)
    best = levels[0][0] if levels else None
    return total, best


def run(markets: List[Dict], orderbooks: Dict[str, Dict], **_kwargs: Any) -> List[Dict]:
    """
    Returns top imbalanced markets, sorted by distance from 0.5.
    orderbooks: { ticker: {"yes": [[price,qty],...], "no": [[price,qty],...]} }
    """
    signals = []

    for ticker, ob in orderbooks.items():
        yes_levels = ob.get("yes") or []
        no_levels = ob.get("no") or []

        # yes bids (buyers) and no bids (sellers of yes)
        bid_qty, best_bid = _side_totals(yes_levels)
        ask_qty, best_ask = _side_totals(no_levels)

        total = bid_qty + ask_qty
        if total == 0:
            continue

        imbalance = bid_qty / total

        threshold = config.OB_IMBALANCE_THRESHOLD
        if imbalance >= threshold or imbalance <= (1 - threshold):
            direction = "BUY" if imbalance >= threshold else "SELL"
            # Find market title
            market_info = next(
                (m for m in markets if m.get("ticker") == ticker),
                {}
            )
            signals.append({
                "ticker": ticker,
                "title": market_info.get("title", ticker),
                "imbalance": round(imbalance, 3),
                "bid_qty": bid_qty,
                "ask_qty": ask_qty,
                "direction": direction,
                "best_bid": best_bid,
                "best_ask": best_ask,
            })

    # Sort by distance from neutral (0.5), most extreme first
    signals.sort(key=lambda x: abs(x["imbalance"] - 0.5), reverse=True)
    return signals[:10]
