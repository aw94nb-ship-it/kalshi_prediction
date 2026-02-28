"""
Rich live dashboard — renders all 6 strategy panels.
"""

from datetime import datetime
from typing import Dict, List

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()
_live: Live = None


def _make_spread_arb_table(signals: List[Dict]) -> Table:
    t = Table(title="S1: Spread Arb", expand=True, show_lines=False)
    t.add_column("Ticker", style="cyan", no_wrap=True, max_width=22)
    t.add_column("Y+N", justify="right")
    t.add_column("Gross", justify="right")
    t.add_column("Net Est.", justify="right")
    for s in signals[:8]:
        color = "green" if s["net_profit_est"] > 0 else "yellow"
        t.add_row(
            s["ticker"],
            str(s["total"]),
            f"{s['gross_profit']}¢",
            Text(f"{s['net_profit_est']}¢", style=color),
        )
    if not signals:
        t.add_row("[dim]no signals[/dim]", "", "", "")
    return t


def _make_correlated_arb_table(signals: List[Dict]) -> Table:
    t = Table(title="S2: Correlated Arb", expand=True, show_lines=False)
    t.add_column("Event", style="cyan", no_wrap=True, max_width=18)
    t.add_column("Easier", justify="right")
    t.add_column("Harder", justify="right")
    t.add_column("Misprice", justify="right")
    for s in signals[:8]:
        t.add_row(
            s["event_ticker"][:18],
            f"{s['easier_yes_ask']}¢",
            Text(f"{s['harder_yes_ask']}¢", style="yellow"),
            Text(f"+{s['mispricing_cents']}¢", style="green"),
        )
    if not signals:
        t.add_row("[dim]no signals[/dim]", "", "", "")
    return t


def _make_orderbook_table(signals: List[Dict]) -> Table:
    t = Table(title="S3: OB Imbalance", expand=True, show_lines=False)
    t.add_column("Ticker", style="cyan", no_wrap=True, max_width=22)
    t.add_column("Imbal.", justify="right")
    t.add_column("Dir", justify="center")
    t.add_column("BidQ/AskQ", justify="right")
    for s in signals[:8]:
        color = "green" if s["direction"] == "BUY" else "red"
        t.add_row(
            s["ticker"],
            f"{s['imbalance']:.2f}",
            Text(s["direction"], style=color),
            f"{s['bid_qty']}/{s['ask_qty']}",
        )
    if not signals:
        t.add_row("[dim]no signals[/dim]", "", "", "")
    return t


def _make_market_maker_table(signals: List[Dict]) -> Table:
    t = Table(title="S4: Wide Spread (MM)", expand=True, show_lines=False)
    t.add_column("Ticker", style="cyan", no_wrap=True, max_width=22)
    t.add_column("Bid", justify="right")
    t.add_column("Ask", justify="right")
    t.add_column("Spread", justify="right")
    t.add_column("Post@", justify="right")
    for s in signals[:8]:
        t.add_row(
            s["ticker"],
            f"{s['yes_bid']}¢",
            f"{s['yes_ask']}¢",
            Text(f"{s['spread']}¢", style="green"),
            f"{s['suggested_bid']}/{s['suggested_ask']}",
        )
    if not signals:
        t.add_row("[dim]no signals[/dim]", "", "", "", "")
    return t


def _make_mean_reversion_table(signals: List[Dict]) -> Table:
    t = Table(title="S5: Mean Reversion", expand=True, show_lines=False)
    t.add_column("Ticker", style="cyan", no_wrap=True, max_width=22)
    t.add_column("Now", justify="right")
    t.add_column("Delta", justify="right")
    t.add_column("Fade", justify="center")
    t.add_column("Samples", justify="right")
    for s in signals[:8]:
        delta_color = "red" if s["price_delta"] > 0 else "green"
        fade_color = "green" if s["fade"] == "BUY" else "red"
        t.add_row(
            s["ticker"],
            f"{s['price_now']}¢",
            Text(f"{s['price_delta']:+d}¢", style=delta_color),
            Text(s["fade"], style=fade_color),
            str(s["samples"]),
        )
    if not signals:
        t.add_row("[dim]no signals[/dim]", "", "", "", "")
    return t


def _make_theta_table(signals: List[Dict]) -> Table:
    t = Table(title="S6: Resolution Theta", expand=True, show_lines=False)
    t.add_column("Ticker", style="cyan", no_wrap=True, max_width=22)
    t.add_column("Yes Ask", justify="right")
    t.add_column("No Ask", justify="right")
    t.add_column("Hrs Left", justify="right")
    for s in signals[:8]:
        t.add_row(
            s["ticker"],
            Text(f"{s['yes_ask']}¢", style="green"),
            f"{s['no_ask']}¢",
            f"{s['hours_left']}h",
        )
    if not signals:
        t.add_row("[dim]no signals[/dim]", "", "", "")
    return t


def build_layout(all_signals: Dict, market_count: int) -> Layout:
    ts = datetime.now().strftime("%H:%M:%S")

    header_text = (
        f"[bold cyan]KALSHI MONITOR[/bold cyan]  |  "
        f"markets: [yellow]{market_count}[/yellow]  |  "
        f"last update: [white]{ts}[/white]"
    )

    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="row1", ratio=1),
        Layout(name="row2", ratio=1),
        Layout(name="row3", ratio=1),
    )

    layout["header"].update(Panel(header_text))

    layout["row1"].split_row(
        Layout(name="s1", ratio=1),
        Layout(name="s2", ratio=1),
    )
    layout["row2"].split_row(
        Layout(name="s3", ratio=1),
        Layout(name="s4", ratio=1),
    )
    layout["row3"].split_row(
        Layout(name="s5", ratio=1),
        Layout(name="s6", ratio=1),
    )

    layout["s1"].update(_make_spread_arb_table(all_signals.get("spread_arb", [])))
    layout["s2"].update(_make_correlated_arb_table(all_signals.get("correlated_arb", [])))
    layout["s3"].update(_make_orderbook_table(all_signals.get("order_book", [])))
    layout["s4"].update(_make_market_maker_table(all_signals.get("market_maker", [])))
    layout["s5"].update(_make_mean_reversion_table(all_signals.get("mean_reversion", [])))
    layout["s6"].update(_make_theta_table(all_signals.get("theta", [])))

    return layout


def start_live() -> Live:
    global _live
    _live = Live(console=console, refresh_per_second=1, screen=True)
    _live.start()
    return _live


def render(all_signals: Dict, market_count: int = 0) -> None:
    global _live
    if _live is None:
        return
    layout = build_layout(all_signals, market_count)
    _live.update(layout)


def stop_live() -> None:
    global _live
    if _live:
        _live.stop()
        _live = None
