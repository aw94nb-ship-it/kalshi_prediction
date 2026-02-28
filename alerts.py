"""
Alerts — play a system beep and print a Rich panel when new signals appear.
"""

import os
import subprocess
import platform
from typing import Dict, List, Set

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

_SOUND_FILE = "/System/Library/Sounds/Glass.aiff"


def _beep() -> None:
    """Play an audio alert appropriate for the current OS."""
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(
                ["afplay", _SOUND_FILE],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif system == "Linux":
            # Try paplay (PulseAudio) then bell fallback
            try:
                subprocess.Popen(
                    ["paplay", "/usr/share/sounds/freedesktop/stereo/bell.oga"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except FileNotFoundError:
                print("\a", end="", flush=True)
        else:
            print("\a", end="", flush=True)
    except Exception:
        pass


def _signal_keys(all_signals: Dict) -> Set[str]:
    """Build a flat set of unique signal identifiers from all strategies."""
    keys: Set[str] = set()
    for strategy, signals in all_signals.items():
        for s in signals:
            ticker = s.get("ticker") or s.get("event_ticker") or ""
            keys.add(f"{strategy}:{ticker}")
    return keys


def check_and_fire(current: Dict, previous: Dict) -> None:
    """
    Compare current and previous signal sets.
    For each new signal (present now but not before), emit an alert.
    """
    curr_keys = _signal_keys(current)
    prev_keys = _signal_keys(previous)
    new_keys = curr_keys - prev_keys

    if not new_keys:
        return

    _beep()

    lines = Text()
    lines.append(f"  {len(new_keys)} new signal(s) detected\n", style="bold yellow")
    for key in sorted(new_keys):
        strategy, ticker = key.split(":", 1)
        lines.append(f"  [{strategy}] {ticker}\n", style="white")

    panel = Panel(
        lines,
        title="[bold yellow]NEW OPPORTUNITIES[/bold yellow]",
        border_style="yellow",
        expand=False,
    )
    # Print below the live display (will appear briefly; live will overwrite on next render)
    console.print(panel)
