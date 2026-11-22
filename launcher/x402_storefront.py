#!/usr/bin/env python3
"""Live Metered x402 (HTTP 402 Payment Required) Agent Storefront & USDC Revenue Ledger.

Logs metered AI-agent micropayment calls into `.startup/x402_ledger.json` so real-time
agent-economy revenue streams directly into the Startup Command Center & Web Studio.
Defaults safely to `base-sepolia` testnet.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _ledger_path(workspace: Path) -> Path:
    sdir = workspace.resolve() / ".startup"
    sdir.mkdir(parents=True, exist_ok=True)
    return sdir / "x402_ledger.json"


def load_x402_ledger(workspace: Path) -> dict[str, Any]:
    path = _ledger_path(workspace)
    if not path.exists():
        return {
            "network": "base-sepolia",
            "pricePerCallUsdc": 0.05,
            "endpoint": "/api/x402/agent-call",
            "payTo": "0xYOUR_BASE_SEPOLIA_TREASURY",
            "totalCalls": 0,
            "totalRevenueUsdc": 0.0,
            "events": [],
        }
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"network": "base-sepolia", "pricePerCallUsdc": 0.05, "totalCalls": 0, "totalRevenueUsdc": 0.0, "events": []}


def build_402_challenge(workspace: Path) -> dict[str, Any]:
    ledger = load_x402_ledger(workspace)
    return {
        "x402Version": 1,
        "accepts": [
            {
                "scheme": "exact",
                "network": ledger.get("network", "base-sepolia"),
                "asset": "USDC",
                "maxAmountRequired": f"{float(ledger.get('pricePerCallUsdc', 0.05)):.4f}",
                "payTo": ledger.get("payTo", "0xYOUR_BASE_SEPOLIA_TREASURY"),
                "resource": ledger.get("endpoint", "/api/x402/agent-call"),
            }
        ],
    }


def record_x402_payment(
    workspace: Path,
    agent_id: str,
    payment_proof: str,
    amount_usdc: float | None = None,
    resource: str = "/api/x402/agent-call",
) -> dict[str, Any]:
    ledger = load_x402_ledger(workspace)
    amt = float(amount_usdc if amount_usdc is not None else ledger.get("pricePerCallUsdc", 0.05))
    event = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agentId": agent_id or "autonomous-agent",
        "resource": resource,
        "amountUsdc": round(amt, 4),
        "network": ledger.get("network", "base-sepolia"),
        "proofPrefix": (payment_proof or "")[:28],
    }
    events = ledger.setdefault("events", [])
    events.append(event)
    # Keep last 200 events in ledger
    ledger["events"] = events[-200:]
    ledger["totalCalls"] = int(ledger.get("totalCalls", 0)) + 1
    ledger["totalRevenueUsdc"] = round(float(ledger.get("totalRevenueUsdc", 0.0)) + amt, 4)
    _ledger_path(workspace).write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    return {"ok": True, "event": event, "totalCalls": ledger["totalCalls"], "totalRevenueUsdc": ledger["totalRevenueUsdc"]}
