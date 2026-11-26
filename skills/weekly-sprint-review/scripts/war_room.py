#!/usr/bin/env python3
"""Autonomous 4-Executive Startup War Room Debate & Decision Memo Engine.

Orchestrates 4 distinct lenses (Lean CTO, Fractional CFO, PMF Truth Auditor,
Exponential Growth Strategist) against a strategic founder question + live
.startup/*.json state, writing `docs/WAR_ROOM_DECISION_MEMO.md`.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def run_war_room(
    workspace: Path,
    question: str,
    write_memo: bool = True,
) -> dict[str, Any]:
    ws = workspace.resolve()
    q = (question or "").strip()
    if not q:
        raise ValueError("'question' is required for war_room_run.")

    sdir = ws / ".startup"
    state = _load_json(sdir / "state.json", {})
    pacts = _load_json(sdir / "pacts.json", [])
    pmf = _load_json(sdir / "pmf.json", {})
    exo = _load_json(sdir / "exponential.json", {})

    company = state.get("companyName") or ws.name
    stage = state.get("stage", "idea")
    metrics = state.get("metrics") or {}
    mrr = float(metrics.get("mrrUsd", state.get("mrrUsd", 0)) or 0)
    gm = float(metrics.get("grossMarginPct", state.get("grossMarginPct", 80)) or 80)
    cash = float(metrics.get("cashOnHandUsd", state.get("cashOnHandUsd", 0)) or 0)
    burn = float(metrics.get("monthlyBurnUsd", state.get("monthlyBurnUsd", 0)) or 0)
    runway = round(cash / burn, 1) if burn > 0 else None

    surveys = pmf.get("surveys") or pmf.get("responses") or []
    very_dis = sum(1 for r in surveys if r.get("disappointment") == "very_disappointed")
    pmf_pct = round((very_dis / len(surveys)) * 100.0, 1) if surveys else None
    paid_pacts = sum(1 for p in pacts if p.get("type", "customer") == "customer" and p.get("status") in ("signed", "paid", "closed"))

    q_lower = q.lower()
    is_fundraising = any(k in q_lower for k in ("raise", "fundrais", "seed", "investor", "safe", "vc", "bridge"))
    is_hiring = any(k in q_lower for k in ("hire", "hiring", "engineer", "team", "sales rep"))
    is_x402 = any(k in q_lower for k in ("x402", "token", "usdc", "crypto", "blockchain", "agent"))
    is_pricing = any(k in q_lower for k in ("price", "pricing", "acv", "discount", "undercut", "margin"))
    is_runway = any(k in q_lower for k in ("runway", "crunch", "burn", "cash", "prepay", "default-alive"))
    is_pivot = any(k in q_lower for k in ("pivot", "icp", "segment", "niche", "reposition"))

    # 4 Executive Perspectives
    cto_view = {
        "role": "Lean CTO & Margin Architect",
        "stance": "SHIP_7_DAY_SLICE" if stage in ("idea", "validation") else "PROTECT_MARGIN_AND_EVALS",
        "argument": (
            f"Current gross margin is {gm:.0f}% (stage={stage}). "
            + (
                "If exploring x402 or agent endpoints, start on Base Sepolia testnet via `x402_starter_scaffold` with zero custom token overhead."
                if is_x402
                else (
                    "Cut non-essential cloud/model COGS immediately via tiered model routing and prompt caching before touching core product velocity."
                    if is_runway
                    else (
                        "Before rebuilding for a pivot, isolate the reusable 20% core workflow and test the new ICP with a 7-day concierge slice."
                        if is_pivot
                        else "Ship a 7-day vertical slice with boring low-ops tech and automated evals; defer heavy infra or premature headcount."
                    )
                )
            )
        ),
    }

    cfo_view = {
        "role": "Fractional CFO & Profit OS",
        "stance": "DEFEND_RUNWAY" if (is_runway or (runway is not None and runway < 12)) else "COMPOUND_DEFAULT_ALIVE",
        "argument": (
            f"MRR is ${mrr:,.0f}/mo with {'Default-Alive / N/A' if runway is None else f'{runway} months'} runway. "
            + (
                "Runway defense first: trim 20–30% discretionary burn, offer 15% annual-prepay Customer PACTs to pull cash forward, and freeze non-revenue spend."
                if is_runway
                else (
                    "Never fight a race-to-the-bottom price war—test a 25–40% ACV lift anchored to quantified ROI and protect >=75% gross margins."
                    if is_pricing
                    else (
                        "Before raising external dilution, lock 30–50% soft-circle via VC Lab Investor PACTs and verify <3-mo CAC payback."
                        if is_fundraising
                        else "Every new dollar of fixed burn (hiring or ads) must map to verified payback under 3 months."
                    )
                )
            )
        ),
    }

    pmf_view = {
        "role": "PMF Truth Auditor",
        "stance": "PROVEN_PULL_SCALE_HXC" if (pmf_pct is not None and pmf_pct >= 40.0) else "DO_NOT_SCALE_PRE_PMF",
        "argument": (
            f"Sean Ellis score is {f'{pmf_pct}%' if pmf_pct is not None else 'unmeasured'} with {paid_pacts} signed/paid Customer PACTs. "
            + (
                "Segment Sean Ellis responses by persona before pivoting—often 1 narrow HXC sub-segment is already >=40% while the broad list dilutes it."
                if is_pivot
                else (
                    "Test the new price point on 5 fresh ICP prospects via 48-hour Customer PACTs; real willingness-to-pay beats hypothetical objections."
                    if is_pricing
                    else (
                        "PMF >=40% gives permission to pour fuel strictly into your High-Expectation Customer (HXC) segment."
                        if (pmf_pct is not None and pmf_pct >= 40.0)
                        else "Never scale hiring or paid ads before hitting >=40% Very Disappointed in a focused HXC niche."
                    )
                )
            )
        ),
    }

    exo_view = {
        "role": "Exponential & Ethical Growth Strategist",
        "stance": "LEVERAGE_10X_WITHOUT_HEADCOUNT",
        "argument": (
            f"ExO Quotient is {exo.get('exoQuotient', 'unscored')}. "
            + (
                "Before adding fixed salaries, ask how AI agents, Staff-on-Demand, and partner channels can deliver 10x output first."
                if is_hiring
                else (
                    "Reframe pricing around 10x outcome value (e.g. recovered revenue or hours saved) rather than seat-count parity with legacy incumbents."
                    if is_pricing
                    else "Pair 10x Moonshot positioning (6Ds Why-Now) with zero-dark-pattern audit-led onboarding and x402/MCP distribution."
                )
            )
        ),
    }

    perspectives = [cto_view, cfo_view, pmf_view, exo_view]
    consensus = [
        f"Protect >=75% gross margin (currently {gm:.0f}%) and Default-Alive optionality.",
        "Anchor every major spend or build decision in verified Customer PACT or Sean Ellis PMF evidence.",
    ]
    tensions = [
        "Speed vs. Burn: Growth/ExO wants aggressive 10x capture, while CFO & PMF Auditor gate spend until HXC payback is verified.",
        "Vision vs. Focus: Singularity/x402 opportunities expand TAM, while Lean CTO insists on 7-day vertical slices.",
    ]
    decision = (
        "EXECUTE_CONTROLLED_EXPANSION"
        if (pmf_pct is not None and pmf_pct >= 40.0 and gm >= 75.0)
        else "VALIDATE_WITH_7_DAY_EXPERIMENT_FIRST"
    )
    next_steps = [
        f"Run a 7-day low-cost test directly answering: '{q[:90]}'",
        "Review live metrics in Startup Command Center (`dashboard/index.html`) after 7 days before committing fixed burn.",
        "Log verified outcome into `.startup/experiments.json` and update `docs/INVESTOR_UPDATE.md`.",
    ]

    memo_path: str | None = None
    if write_memo:
        docs_dir = ws / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        memo_file = docs_dir / "WAR_ROOM_DECISION_MEMO.md"
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        lines = [
            f"# {company} — Startup War Room Decision Memo",
            "",
            f"> Generated by Startup Antigravity (`war_room_run`) • {now_iso}",
            f"> **Strategic Question:** {q}",
            f"> **Unified Decision:** `{decision}`",
            "",
            "## 4-Executive Debate",
            *[f"### {p['role']} (`{p['stance']}`)\n{p['argument']}\n" for p in perspectives],
            "## Points of Consensus",
            *[f"- {c}" for c in consensus],
            "",
            "## Key Tradeoffs & Tensions",
            *[f"- {t}" for t in tensions],
            "",
            "## Immediate 7-Day Action Plan",
            *[f"{i}. {s}" for i, s in enumerate(next_steps, 1)],
        ]
        memo_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        memo_path = str(memo_file)

    return {
        "ok": True,
        "company": company,
        "question": q,
        "decision": decision,
        "perspectives": perspectives,
        "consensus": consensus,
        "tensions": tensions,
        "nextSteps": next_steps,
        "memoPath": memo_path,
    }
