#!/usr/bin/env python3
"""PreToolUse hook: Blocks secret/private-key leaks, guards Data Room PII, and confirms mainnet/heavy-infra actions."""

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
MAINNET_TX_RE = re.compile(
    r"\b(forge\s+script\b.*--broadcast|cast\s+send\b|solana\s+transfer\b|hardhat\s+run\b.*--network\s+(mainnet|base|ethereum|polygon|arbitrum))\b",
    re.IGNORECASE,
)
HARDCODED_SECRET_RE = re.compile(
    r"("
    r"sk_live_[0-9a-zA-Z]{16,}"
    r"|AKIA[0-9A-Z]{16}"
    r"|sk-ant-[a-zA-Z0-9_-]{20,}"
    r"|xai-[a-zA-Z0-9_-]{20,}"
    r"|-----BEGIN\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE\s+KEY-----"
    r"|(?:PRIVATE_KEY|WALLET_PRIVATE_KEY|SIGNER_KEY)\s*[:=]\s*['\"]?0x[0-9a-fA-F]{64}['\"]?"
    r")",
)
RAW_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


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


def _deny(reason: str) -> int:
    print(json.dumps({"decision": "deny", "reason": reason}))
    return 0


def _ask(reason: str) -> int:
    print(json.dumps({"decision": "ask", "reason": reason}))
    return 0


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
            return _deny(
                "Blocked by Startup Antigravity Mensarius Hygiene Guard: "
                "never stage or commit .env files, private keys, or raw secret/PII files."
            )

        if MAINNET_TX_RE.search(cmd):
            return _ask(
                "Startup Antigravity Programmable-Finance Guard: This command broadcasts a live "
                "onchain transaction or mainnet deployment. Please confirm the exact network, "
                "recipient, and amount before proceeding."
            )

        stage = _get_stage(payload)
        if stage in ("idea", "validation") and HEAVY_INFRA_RE.search(cmd):
            return _ask(
                f"Startup Antigravity Lean Guard: Current stage is '{stage}'. "
                "Confirm you truly need production cluster infrastructure before closing "
                "your first paying customers / Customer PACTs."
            )

    elif tname in ("write_file", "edit_file"):
        target_path = str(args.get("Path") or args.get("path") or "").replace("\\", "/")
        content = str(
            args.get("Content")
            or args.get("Replacement")
            or args.get("content")
            or args.get("replacement")
            or ""
        )
        lower_path = target_path.lower()
        is_test_or_example = any(
            tok in lower_path for tok in (".env.example", "/tests/", "test_", "example")
        )

        if content and not is_test_or_example and HARDCODED_SECRET_RE.search(content):
            return _deny(
                "Blocked by Startup Antigravity Secret & Wallet Key Guard: "
                "Detected a live API key, PEM private key, or hex wallet PRIVATE_KEY in file content. "
                "Use environment variables or hardware/multisig custody instead."
            )

        if "/data-room/" in lower_path and content and RAW_EMAIL_RE.search(content):
            return _ask(
                "Startup Antigravity Data Room Privacy Guard: Detected a raw email address being "
                "written inside data-room/. Confirm this is an intentional founder contact and not "
                "raw customer/investor PII."
            )

    print(json.dumps({"decision": "allow"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
