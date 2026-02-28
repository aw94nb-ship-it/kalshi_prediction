"""
Kalshi Prediction Monitor — main entry point.

Polling loop:
  1. Fetch active markets
  2. Fetch order books for a sample of tickers
  3. Update data store (rolling price history)
  4. Run all 6 strategies
  5. Render Rich live dashboard
  6. Fire alerts on new signals
  7. Sleep POLL_INTERVAL_SECS and repeat
"""

import time
import sys
import random
from typing import Dict, List

import config
import data_store
import display
import alerts
from kalshi_client import KalshiClient
from strategies import (
    spread_arb,
    correlated_arb,
    order_book,
    market_maker,
    mean_reversion,
    theta,
)


def run_all_strategies(
    markets: List[Dict],
    orderbooks: Dict[str, Dict],
) -> Dict:
    return {
        "spread_arb": spread_arb(markets),
        "correlated_arb": correlated_arb(markets),
        "order_book": order_book(markets, orderbooks=orderbooks),
        "market_maker": market_maker(markets),
        "mean_reversion": mean_reversion(markets),
        "theta": theta(markets),
    }


def main() -> None:
    client = KalshiClient()
    prev_signals: Dict = {}

    live = display.start_live()

    try:
        while True:
            # --- 1. Fetch markets ---
            try:
                markets = client.get_markets(
                    limit=config.MAX_MARKETS, status="active"
                )
            except Exception as exc:
                markets = []
                display.console.log(f"[red]Error fetching markets: {exc}[/red]")

            # --- 2. Fetch order books (sample to limit API calls) ---
            tickers = [m["ticker"] for m in markets if m.get("ticker")]
            sample = random.sample(
                tickers, min(config.OB_SAMPLE_TOP_N, len(tickers))
            )
            orderbooks: Dict[str, Dict] = {}
            for ticker in sample:
                try:
                    orderbooks[ticker] = client.get_orderbook(ticker)
                except Exception:
                    pass

            # --- 3. Update rolling data store ---
            data_store.update(markets)

            # --- 4. Run strategies ---
            signals = run_all_strategies(markets, orderbooks)

            # --- 5. Render dashboard ---
            display.render(signals, market_count=len(markets))

            # --- 6. Alerts ---
            alerts.check_and_fire(signals, prev_signals)
            prev_signals = signals

            # --- 7. Sleep ---
            time.sleep(config.POLL_INTERVAL_SECS)

    except KeyboardInterrupt:
        pass
    finally:
        display.stop_live()
        print("\nKalshi Monitor stopped.")


if __name__ == "__main__":
    main()
