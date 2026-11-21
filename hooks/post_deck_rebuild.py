#!/usr/bin/env python3
"""PostToolUse hook: Automatically rebuilds index.html & DECK.md whenever pitch-deck/deck.json changes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
DECK_SCRIPTS = PLUGIN_ROOT / "skills" / "pitch-deck-builder" / "scripts"
DASHBOARD_SCRIPTS = PLUGIN_ROOT / "skills" / "unit-economics-and-profit-os" / "scripts"
DATAROOM_SCRIPTS = PLUGIN_ROOT / "skills" / "vc-lab-fundraising-os" / "scripts"
for _p in (DECK_SCRIPTS, DASHBOARD_SCRIPTS, DATAROOM_SCRIPTS):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from build_dashboard import build_dashboard  # noqa: E402
from build_data_room import build_data_room  # noqa: E402
from build_deck import build_deck  # noqa: E402


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        print("{}")
        return 0

    if payload.get("error"):
        print("{}")
        return 0

    tc = payload.get("toolCall") or {}
    args = tc.get("args") or {}
    target_path = str(args.get("Path") or args.get("path") or "")

    normalized = target_path.replace("\\", "/")
    if normalized.endswith("pitch-deck/deck.json"):
        p = Path(target_path)
        if p.exists():
            try:
                build_deck(p)
            except Exception:
                # Never break the tool loop; Stop hook will catch invalid JSON cleanly
                pass
            ws = p.parent.parent
            if (ws / "data-room" / "index.html").exists():
                try:
                    build_data_room(ws)
                except Exception:
                    pass
    elif "/.startup/" in normalized and normalized.endswith(".json"):
        p = Path(target_path)
        ws = p.parent.parent
        if (ws / "dashboard" / "index.html").exists():
            try:
                build_dashboard(ws)
            except Exception:
                pass
        if (ws / "data-room" / "index.html").exists():
            try:
                build_data_room(ws)
            except Exception:
                pass

    print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
