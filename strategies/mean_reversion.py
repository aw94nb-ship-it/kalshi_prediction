"""
Strategy 5 — Probability Trend + Mean Reversion

Signal: |price_now - price_N_ago| > MEAN_REVERSION_MOVE_CENTS
     AND volume_delta < LOW_VOLUME_THRESHOLD (move not backed by volume)
Suggests fading the move (betting it reverses).
"""

from typing import Any, Dict, List
import data_store
import config


def run(markets: List[Dict], **_kwargs: Any) -> List[Dict]:
    signals = []

    for m in markets:
        ticker = m.get("ticker")
        if not ticker:
            continue

        history = data_store.get_history(ticker)
        if len(history) < 2:
            continue

        ts_now, price_now, vol_now = history[-1]
        ts_old, price_old, vol_old = history[0]

        price_delta = price_now - price_old
        if abs(price_delta) < config.MEAN_REVERSION_MOVE_CENTS:
            continue

        vol_delta = vol_now - vol_old

        if vol_delta < config.LOW_VOLUME_THRESHOLD:
            direction = "UP" if price_delta > 0 else "DOWN"
            fade = "SELL" if direction == "UP" else "BUY"
            signals.append({
                "ticker": ticker,
                "title": m.get("title", ""),
                "price_now": price_now,
                "price_old": price_old,
                "price_delta": price_delta,
                "direction": direction,
                "fade": fade,
                "vol_delta": vol_delta,
                "samples": len(history),
            })

    signals.sort(key=lambda x: abs(x["price_delta"]), reverse=True)
    return signals
