#!/usr/bin/env python3
"""SessionStart hook: Injects Day-0 kickstart cue or a concise Founder Pulse."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        payload = {}

    ws_paths = payload.get("workspacePaths") or []
    raw_ws = ws_paths[0] if ws_paths else payload.get("cwd")
    if not raw_ws:
        print("{}")
        return 0

    ws = Path(raw_ws)
    # Do not nag inside the plugin's own source repository
    plugin_manifest = _read_json(ws / "plugin.json", {})
    if isinstance(plugin_manifest, dict) and plugin_manifest.get("name") == "startup-antigravity":
        print("{}")
        return 0

    state_file = ws / ".startup" / "state.json"
    if not state_file.exists():
        msg = (
            "[Startup Antigravity OS] This workspace is not initialized as a startup project yet "
            "(`.startup/state.json` not found). When the user asks to launch, validate, or plan a "
            "business idea, activate the `startup-kickstart` skill to draft their FI One-Sentence "
            "Pitch, 14-day First-Dollar Plan, For-Progress iKPI, and interactive Pitch Deck."
        )
        print(json.dumps({"injectSteps": [{"systemMessage": {"systemMessage": msg}}]}))
        return 0

    state = _read_json(state_file, {})
    assumptions = _read_json(ws / ".startup" / "assumptions.json", [])
    interviews = _read_json(ws / ".startup" / "interviews.json", [])
    pacts = _read_json(ws / ".startup" / "pacts.json", [])

    untested = [a for a in assumptions if a.get("status") not in ("validated", "invalidated")]
    untested.sort(key=lambda x: x.get("riskScore", 0), reverse=True)
    top_risk = untested[0]["statement"] if untested else "None logged — add top risk via assumption_manage."

    cust_pacts = sum(
        float(p.get("amountUsd", 0))
        for p in pacts
        if p.get("kind") == "customer" and p.get("status") in ("pact_signed", "closed_cash")
    )

    ikpi = state.get("ikpi") or {}
    ikpi_str = f"{ikpi.get('name', 'Unset')} ({ikpi.get('current', 0)}/{ikpi.get('target', 0)})"

    pulse = (
        f"[Startup Antigravity Pulse — {state.get('companyName', 'Startup')}]\n"
        f"- FI Stage: {state.get('stage', 'idea')} | MRR: ${state.get('mrrUsd', 0):,.0f} | "
        f"Customer PACTs: ${cust_pacts:,.0f} | Interviews: {len(interviews)}/15\n"
        f"- Top Untested Risk: {top_risk}\n"
        f"- For-Progress iKPI: {ikpi_str}"
    )
    print(json.dumps({"injectSteps": [{"systemMessage": {"systemMessage": pulse}}]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
