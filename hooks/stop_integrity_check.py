#!/usr/bin/env python3
"""Stop hook: Ensures .startup/state.json and pitch-deck/deck.json remain valid JSON."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        print("{}")
        return 0

    # Prevent infinite loops when already continuing
    if payload.get("continuationActive"):
        print("{}")
        return 0

    if payload.get("terminationReason") not in ("NO_TOOL_CALL", None, ""):
        print("{}")
        return 0

    ws_paths = payload.get("workspacePaths") or []
    raw_ws = ws_paths[0] if ws_paths else payload.get("cwd")
    if not raw_ws:
        print("{}")
        return 0

    ws = Path(raw_ws)
    broken: list[str] = []
    for rel in (".startup/state.json", "pitch-deck/deck.json"):
        f = ws / rel
        if f.exists():
            try:
                json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                broken.append(f"{rel} (line {exc.lineno}, col {exc.colno}: {exc.msg})")

    if broken:
        print(
            json.dumps(
                {
                    "decision": "continue",
                    "reason": (
                        "Startup Antigravity Integrity Check detected invalid JSON in: "
                        + "; ".join(broken)
                        + ". Please repair the JSON syntax before finishing."
                    ),
                }
            )
        )
        return 0

    stale: list[str] = []
    deck_json = ws / "pitch-deck" / "deck.json"
    deck_html = ws / "pitch-deck" / "index.html"
    if deck_json.exists() and deck_html.exists():
        if deck_json.stat().st_mtime - deck_html.stat().st_mtime > 1.0:
            stale.append("pitch-deck/index.html (stale vs pitch-deck/deck.json — run pitch_deck_build)")

    state_json = ws / ".startup" / "state.json"
    dash_html = ws / "dashboard" / "index.html"
    if state_json.exists() and dash_html.exists():
        if state_json.stat().st_mtime - dash_html.stat().st_mtime > 1.0:
            stale.append("dashboard/index.html (stale vs .startup/state.json — run founder_dashboard_build)")

    if stale:
        print(
            json.dumps(
                {
                    "decision": "continue",
                    "reason": (
                        "Startup Antigravity Drift Check detected outdated compiled artifacts: "
                        + "; ".join(stale)
                        + "."
                    ),
                }
            )
        )
        return 0

    print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
