"""
Strategy 1 — Yes/No Spread Arbitrage

Signal: yes_ask + no_ask <= SPREAD_ARB_THRESHOLD (default 93¢)
Net profit estimate: 100 - yes_ask - no_ask minus ~7% fee on winning leg.
"""

from typing import Any, Dict, List
import config

FEE_RATE = 0.07  # approximate fee on winning leg


def run(markets: List[Dict], **_kwargs: Any) -> List[Dict]:
    """
    Returns list of signal dicts for markets where the combined cost
    of buying both Yes and No is below the threshold.
    """
    signals = []
    for m in markets:
        yes_ask = m.get("yes_ask")
        no_ask = m.get("no_ask")
        if yes_ask is None or no_ask is None:
            continue
        total = yes_ask + no_ask
        if total <= config.SPREAD_ARB_THRESHOLD:
            gross = 100 - total
            # fee applies to the winning leg (~50% chance, so expected fee ~= fee_rate * 100 * 0.5,
            # but conservatively charge full fee on the winning leg price
            fee = FEE_RATE * max(yes_ask, no_ask)
            net = gross - fee
            signals.append({
                "ticker": m.get("ticker", ""),
                "title": m.get("title", ""),
                "yes_ask": yes_ask,
                "no_ask": no_ask,
                "total": total,
                "gross_profit": round(gross, 2),
                "net_profit_est": round(net, 2),
            })

    # most profitable first
    signals.sort(key=lambda x: x["net_profit_est"], reverse=True)
    return signals
