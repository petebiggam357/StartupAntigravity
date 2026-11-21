#!/usr/bin/env python3
"""PreToolUse hook: Blocks secret/PII Git leaks and nudges on premature heavy infra."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SECRET_GIT_RE = re.compile(
    r"\bgit\s+(add|commit)\b.*(\.env\b|\.pem\b|\.key\b|id_rsa|secrets?\.(json|ya?ml)|investor[_-]?pii)",
    re.IGNORECASE,
)
HEAVY_INFRA_RE = re.compile(
    r"\b(terraform\s+apply|kubectl\s+apply|helm\s+(install|upgrade)|eksctl\s+create|gcloud\s+container\s+clusters\s+create)\b",
    re.IGNORECASE,
)


def _get_stage(payload: dict) -> str:
    ws_paths = payload.get("workspacePaths") or []
    raw_ws = ws_paths[0] if ws_paths else payload.get("cwd")
    if not raw_ws:
        return ""
    state_file = Path(raw_ws) / ".startup" / "state.json"
    if not state_file.exists():
        return ""
    try:
        return str(json.loads(state_file.read_text(encoding="utf-8")).get("stage", ""))
    except Exception:
        return ""


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        print(json.dumps({"decision": "allow"}))
        return 0

    tc = payload.get("toolCall") or {}
    tname = str(tc.get("name", ""))
    args = tc.get("args") or {}

    if tname == "run_command":
        cmd = str(args.get("CommandLine") or args.get("command") or "")
        if SECRET_GIT_RE.search(cmd):
            print(
                json.dumps(
                    {
                        "decision": "deny",
                        "reason": (
                            "Blocked by Startup Antigravity Mensarius Hygiene Guard: "
                            "never stage or commit .env files, private keys, or raw secret/PII files."
                        ),
                    }
                )
            )
            return 0

        stage = _get_stage(payload)
        if stage in ("idea", "validation") and HEAVY_INFRA_RE.search(cmd):
            print(
                json.dumps(
                    {
                        "decision": "ask",
                        "reason": (
                            f"Startup Antigravity Lean Guard: Current stage is '{stage}'. "
                            "Confirm you truly need production cluster infrastructure before closing "
                            "your first paying customers / Customer PACTs."
                        ),
                    }
                )
            )
            return 0

    print(json.dumps({"decision": "allow"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
