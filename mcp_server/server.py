#!/usr/bin/env python3
"""
Startup Antigravity — Bundled Local Stdio MCP Server (`startup-antigravity-os`).

Pure Python 3 standard library implementation (zero external pip dependencies).
Exposes deterministic startup operating tools grounded in Founder Institute (fi.co),
VC Lab / Decile Group (govclab.com), and high-margin ethical profit velocity.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
DECK_SCRIPTS_DIR = PLUGIN_ROOT / "skills" / "pitch-deck-builder" / "scripts"
LANDING_SCRIPTS_DIR = PLUGIN_ROOT / "skills" / "revenue-first-validation" / "scripts"
CONNECTOR_SCRIPTS_DIR = PLUGIN_ROOT / "skills" / "multi-ai-connectors" / "scripts"
DASHBOARD_SCRIPTS_DIR = PLUGIN_ROOT / "skills" / "unit-economics-and-profit-os" / "scripts"
DATAROOM_SCRIPTS_DIR = PLUGIN_ROOT / "skills" / "vc-lab-fundraising-os" / "scripts"
AI_X402_SCRIPTS_DIR = PLUGIN_ROOT / "skills" / "ai-native-and-x402-finance" / "scripts"
BOARD_SCRIPTS_DIR = PLUGIN_ROOT / "skills" / "weekly-sprint-review" / "scripts"
EXO_SCRIPTS_DIR = PLUGIN_ROOT / "skills" / "exponential-thinking-and-singularity" / "scripts"
I18N_DIR = PLUGIN_ROOT / "i18n"
IKPI_CATALOG_PATH = Path(__file__).resolve().parent / "ikpi_catalog.json"
FOUNDER_RESOURCES_PATH = Path(__file__).resolve().parent / "founder_resources.json"

for _p in (
    DECK_SCRIPTS_DIR,
    LANDING_SCRIPTS_DIR,
    CONNECTOR_SCRIPTS_DIR,
    DASHBOARD_SCRIPTS_DIR,
    DATAROOM_SCRIPTS_DIR,
    AI_X402_SCRIPTS_DIR,
    BOARD_SCRIPTS_DIR,
    EXO_SCRIPTS_DIR,
    I18N_DIR,
):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from ai_connector import detect_connectors, run_second_opinion, sync_ai_context  # noqa: E402
from ai_x402_calc import run_ai_x402_calc  # noqa: E402
from board_review import run_board_review  # noqa: E402
from build_dashboard import build_dashboard  # noqa: E402
from build_data_room import build_data_room  # noqa: E402
from build_deck import (  # noqa: E402
    BANNED_BUZZWORDS,
    build_deck,
    export_design_briefs,
    lint_deck,
    lint_one_sentence_pitch,
)
from build_landing_page import build_landing_page  # noqa: E402
from exponential_audit import run_exponential_audit  # noqa: E402
from i18n import list_supported_languages, set_workspace_locale  # noqa: E402
from voice_pitch_coach import analyze_voice_pitch  # noqa: E402
from war_room import run_war_room  # noqa: E402

SERVER_NAME = "startup-antigravity-os"
SERVER_VERSION = "0.3.1-beta"
PROTOCOL_VERSION = "2024-11-05"

FI_STAGE_BENCHMARKS: dict[str, dict[str, Any]] = {
    "idea": {
        "order": 1,
        "label": "Idea & Problem Discovery",
        "nextStage": "validation",
        "exitCriteria": [
            "FI One-Sentence Pitch passes linter with zero errors",
            "For-Progress Impact Thesis & primary iKPI defined",
            "15+ unbiased Customer Discovery interviews logged",
        ],
    },
    "validation": {
        "order": 2,
        "label": "Revenue-First Validation",
        "nextStage": "mvp",
        "exitCriteria": [
            "Top 3 Riskiest Assumptions tested via pre-committed experiments",
            "At least 1 paid pilot / pre-order Customer PACT signed (First Dollar proven)",
            "7-day vertical slice MVP spec + Cut-List written",
        ],
    },
    "mvp": {
        "order": 3,
        "label": "MVP & FI Accelerator Stage ($1K–$10K MRR)",
        "nextStage": "pre_seed_traction",
        "exitCriteria": [
            "Live MVP in paying customer hands",
            "$1,000–$10,000 MRR with >70% gross margin",
            "Repeatable weekly customer acquisition channel identified",
        ],
    },
    "pre_seed_traction": {
        "order": 4,
        "label": "FI Pre-Seed Traction ($10K–$25K MRR)",
        "nextStage": "seed_scale",
        "exitCriteria": [
            "$10,000–$25,000 MRR growing 10–20%+ MoM",
            "LTV:CAC >= 3:1 and CAC payback < 6 months",
            "Traction Pitch Deck & VC Lab Data Room ready",
        ],
    },
    "seed_scale": {
        "order": 5,
        "label": "FI Seed & Scale ($25K–$200K+ MRR)",
        "nextStage": "series_a",
        "exitCriteria": [
            "$25,000–$200,000+ MRR with strong retention",
            "Default-Alive option or disciplined Investor PACT round closed",
            "Verified For-Progress iKPI scaling with revenue",
        ],
    },
}

# Founder Institute FAST Agreement standard advisory equity percentages
# Rows: stage (idea, startup, growth); Cols: tier (standard, strategic, expert)
FAST_EQUITY_MATRIX: dict[str, dict[str, dict[str, Any]]] = {
    "idea": {
        "standard": {"equityPct": 0.25, "monthlyHours": 2, "meetings": "Monthly 1h + email"},
        "strategic": {"equityPct": 0.50, "monthlyHours": 5, "meetings": "Bi-weekly + warm intros"},
        "expert": {"equityPct": 1.00, "monthlyHours": 10, "meetings": "Weekly + active recruiting/sales"},
    },
    "startup": {
        "standard": {"equityPct": 0.20, "monthlyHours": 2, "meetings": "Monthly 1h + email"},
        "strategic": {"equityPct": 0.40, "monthlyHours": 5, "meetings": "Bi-weekly + warm intros"},
        "expert": {"equityPct": 0.80, "monthlyHours": 10, "meetings": "Weekly + active recruiting/sales"},
    },
    "growth": {
        "standard": {"equityPct": 0.15, "monthlyHours": 2, "meetings": "Monthly 1h + email"},
        "strategic": {"equityPct": 0.30, "monthlyHours": 5, "meetings": "Bi-weekly + strategic intros"},
        "expert": {"equityPct": 0.60, "monthlyHours": 10, "meetings": "Weekly + board-level guidance"},
    },
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _resolve_workspace(workspace_path: str | None) -> Path:
    if workspace_path:
        return Path(workspace_path).expanduser().resolve()
    return Path.cwd().resolve()


def _startup_dir(workspace_path: str | None) -> Path:
    d = _resolve_workspace(workspace_path) / ".startup"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Tool Implementations
# ---------------------------------------------------------------------------


def tool_startup_get_state(args: dict[str, Any]) -> dict[str, Any]:
    ws = _resolve_workspace(args.get("workspace_path"))
    sdir = ws / ".startup"
    state_file = sdir / "state.json"
    if not state_file.exists():
        return {
            "initialized": False,
            "workspace": str(ws),
            "nextAction": "Run the `startup-kickstart` skill to initialize this startup workspace.",
        }

    state = _read_json(state_file, {})
    assumptions = _read_json(sdir / "assumptions.json", [])
    experiments = _read_json(sdir / "experiments.json", [])
    interviews = _read_json(sdir / "interviews.json", [])
    pacts = _read_json(sdir / "pacts.json", [])

    untested = [a for a in assumptions if a.get("status") not in ("validated", "invalidated")]
    untested.sort(key=lambda x: x.get("riskScore", 0), reverse=True)

    customer_pacts_usd = sum(
        float(p.get("amountUsd", 0))
        for p in pacts
        if p.get("kind") == "customer" and p.get("status") in ("pact_signed", "closed_cash")
    )
    investor_pacts_usd = sum(
        float(p.get("amountUsd", 0))
        for p in pacts
        if p.get("kind") == "investor" and p.get("status") in ("pact_signed", "closed_cash")
    )

    stage = state.get("stage", "idea")
    benchmark = FI_STAGE_BENCHMARKS.get(stage, FI_STAGE_BENCHMARKS["idea"])

    deck_file = ws / "pitch-deck" / "deck.json"
    deck_score = None
    if deck_file.exists():
        try:
            deck_score = lint_deck(json.loads(deck_file.read_text(encoding="utf-8")))["readinessScore"]
        except Exception:
            deck_score = 0

    return {
        "initialized": True,
        "workspace": str(ws),
        "state": state,
        "fiBenchmark": benchmark,
        "telemetry": {
            "totalAssumptions": len(assumptions),
            "untestedAssumptions": len(untested),
            "topRiskyAssumption": untested[0] if untested else None,
            "experimentsCount": len(experiments),
            "interviewsCount": len(interviews),
            "fiInterviewTarget": 15,
            "customerPactsCommittedUsd": round(customer_pacts_usd, 2),
            "investorPactsCommittedUsd": round(investor_pacts_usd, 2),
            "pitchDeckReadinessScore": deck_score,
        },
    }


def tool_startup_update_stage(args: dict[str, Any]) -> dict[str, Any]:
    sdir = _startup_dir(args.get("workspace_path"))
    state_file = sdir / "state.json"
    state = _read_json(
        state_file,
        {
            "companyName": "Unnamed Startup",
            "stage": "idea",
            "fiOneSentencePitch": "",
            "mrrUsd": 0,
            "monthlyBurnUsd": 0,
            "cashOnHandUsd": 0,
            "grossMarginPct": 80,
            "targetFirstDollarDate": "",
            "impactThesis": "",
            "ikpi": {"name": "", "current": 0, "target": 0, "sdg": ""},
            "activeSprintGoal": "",
            "createdAt": _now_iso(),
        },
    )

    updatable = [
        "companyName",
        "stage",
        "fiOneSentencePitch",
        "mrrUsd",
        "monthlyBurnUsd",
        "cashOnHandUsd",
        "grossMarginPct",
        "targetFirstDollarDate",
        "impactThesis",
        "activeSprintGoal",
        "archetype",
    ]
    for key in updatable:
        if key in args and args[key] is not None:
            if key == "stage" and args[key] not in FI_STAGE_BENCHMARKS:
                raise ValueError(
                    f"Invalid stage '{args[key]}'. Must be one of: {', '.join(FI_STAGE_BENCHMARKS)}"
                )
            state[key] = args[key]

    if "ikpi" in args and isinstance(args["ikpi"], dict):
        state.setdefault("ikpi", {})
        state["ikpi"].update(args["ikpi"])

    state["updatedAt"] = _now_iso()
    _write_json(state_file, state)

    pitch_lint = (
        lint_one_sentence_pitch(state["fiOneSentencePitch"])
        if state.get("fiOneSentencePitch")
        else None
    )
    return {
        "saved": str(state_file),
        "state": state,
        "fiBenchmark": FI_STAGE_BENCHMARKS.get(state.get("stage", "idea")),
        "pitchLint": pitch_lint,
    }


def tool_fi_pitch_lint(args: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    if args.get("pitch"):
        out["oneSentencePitch"] = lint_one_sentence_pitch(str(args["pitch"]))

    deck_path = args.get("deck_path")
    if not deck_path and args.get("workspace_path"):
        candidate = _resolve_workspace(args["workspace_path"]) / "pitch-deck" / "deck.json"
        if candidate.exists():
            deck_path = str(candidate)

    if deck_path:
        p = Path(deck_path).expanduser().resolve()
        if not p.exists():
            raise FileNotFoundError(f"Deck file not found: {p}")
        data = json.loads(p.read_text(encoding="utf-8"))
        out["deckAudit"] = lint_deck(data)

    if not out:
        raise ValueError("Provide either 'pitch' text or 'deck_path' / 'workspace_path'.")
    return out


def tool_assumption_manage(args: dict[str, Any]) -> dict[str, Any]:
    action = args.get("action", "board")
    sdir = _startup_dir(args.get("workspace_path"))
    path = sdir / "assumptions.json"
    items: list[dict[str, Any]] = _read_json(path, [])

    if action == "add":
        statement = str(args.get("statement", "")).strip()
        if not statement:
            raise ValueError("'statement' is required when action='add'.")
        impact = max(1, min(5, int(args.get("impact", 4))))
        uncertainty = max(1, min(5, int(args.get("uncertainty", 4))))
        entry = {
            "id": f"A-{len(items) + 1:03d}",
            "statement": statement,
            "category": args.get("category", "desirability"),
            "impact": impact,
            "uncertainty": uncertainty,
            "riskScore": impact * uncertainty,
            "status": "untested",
            "evidence": "",
            "createdAt": _now_iso(),
        }
        items.append(entry)
        _write_json(path, items)
        return {"added": entry, "total": len(items)}

    if action == "update":
        aid = args.get("id")
        target = next((x for x in items if x.get("id") == aid), None)
        if not target:
            raise ValueError(f"Assumption '{aid}' not found.")
        for k in ("status", "evidence", "statement", "category"):
            if k in args and args[k] is not None:
                target[k] = args[k]
        if "impact" in args and args["impact"] is not None:
            target["impact"] = max(1, min(5, int(args["impact"])))
        if "uncertainty" in args and args["uncertainty"] is not None:
            target["uncertainty"] = max(1, min(5, int(args["uncertainty"])))
        target["riskScore"] = target["impact"] * target["uncertainty"]
        target["updatedAt"] = _now_iso()
        _write_json(path, items)
        return {"updated": target}

    # board
    ranked = sorted(
        items,
        key=lambda x: (
            0 if x.get("status") not in ("validated", "invalidated") else 1,
            -int(x.get("riskScore", 0)),
        ),
    )
    return {
        "total": len(ranked),
        "untested": sum(1 for x in ranked if x.get("status") not in ("validated", "invalidated")),
        "validated": sum(1 for x in ranked if x.get("status") == "validated"),
        "invalidated": sum(1 for x in ranked if x.get("status") == "invalidated"),
        "assumptions": ranked,
    }


def tool_experiment_manage(args: dict[str, Any]) -> dict[str, Any]:
    action = args.get("action", "list")
    sdir = _startup_dir(args.get("workspace_path"))
    path = sdir / "experiments.json"
    items: list[dict[str, Any]] = _read_json(path, [])

    if action == "create":
        hypothesis = str(args.get("hypothesis", "")).strip()
        threshold = str(args.get("success_threshold", "")).strip()
        if not hypothesis or not threshold:
            raise ValueError("Both 'hypothesis' and 'success_threshold' are required.")
        entry = {
            "id": f"EXP-{len(items) + 1:03d}",
            "assumptionId": args.get("assumption_id", ""),
            "hypothesis": hypothesis,
            "method": args.get("method", "smoke_test"),
            "successThreshold": threshold,
            "deadline": args.get("deadline", ""),
            "status": "running",
            "observedResult": "",
            "decision": "",
            "createdAt": _now_iso(),
        }
        items.append(entry)
        _write_json(path, items)
        return {"created": entry}

    if action == "record_result":
        eid = args.get("id")
        target = next((x for x in items if x.get("id") == eid), None)
        if not target:
            raise ValueError(f"Experiment '{eid}' not found.")
        outcome = args.get("outcome", "inconclusive")
        if outcome not in ("validated", "invalidated", "inconclusive"):
            raise ValueError("'outcome' must be 'validated', 'invalidated', or 'inconclusive'.")
        target["status"] = outcome
        target["observedResult"] = args.get("observed_result", "")
        target["decision"] = args.get("decision", "")
        target["completedAt"] = _now_iso()
        _write_json(path, items)
        return {"updated": target}

    return {"total": len(items), "experiments": items}


def tool_interview_manage(args: dict[str, Any]) -> dict[str, Any]:
    action = args.get("action", "summary")
    sdir = _startup_dir(args.get("workspace_path"))
    path = sdir / "interviews.json"
    items: list[dict[str, Any]] = _read_json(path, [])

    if action == "log":
        persona = str(args.get("persona", "")).strip()
        if not persona:
            raise ValueError("'persona' is required when action='log'.")
        entry = {
            "id": f"INT-{len(items) + 1:03d}",
            "persona": persona,
            "companySegment": args.get("company_segment", ""),
            "painSeverity": max(1, min(5, int(args.get("pain_severity", 3)))),
            "currentWorkaround": args.get("current_workaround", ""),
            "willingnessToPayUsd": float(args.get("willingness_to_pay_usd", 0)),
            "pledgedPilot": bool(args.get("pledged_pilot", False)),
            "verbatimQuote": args.get("verbatim_quote", ""),
            "loggedAt": _now_iso(),
        }
        items.append(entry)
        _write_json(path, items)
        return {"logged": entry, "totalInterviews": len(items), "fiValidationTarget": 15}

    count = len(items)
    if count == 0:
        return {
            "totalInterviews": 0,
            "fiValidationTarget": 15,
            "avgPainSeverity": 0,
            "willingToPayPct": 0,
            "medianWtpUsd": 0,
            "pilotsPledged": 0,
            "verdict": "No interviews logged yet. Log at least 15 unbiased Mom Test interviews.",
        }

    pains = [int(i.get("painSeverity", 0)) for i in items]
    wtps = sorted(
        float(i.get("willingnessToPayUsd", 0))
        for i in items
        if float(i.get("willingnessToPayUsd", 0)) > 0
    )
    pilots = sum(1 for i in items if i.get("pledgedPilot"))
    median_wtp = wtps[len(wtps) // 2] if wtps else 0.0
    avg_pain = round(sum(pains) / count, 2)
    wtp_pct = round((len(wtps) / count) * 100, 1)

    verdict = (
        "Strong signal — push immediately to paid pilot PACTs."
        if avg_pain >= 4.0 and wtp_pct >= 40
        else "Keep discovering — pain or willingness-to-pay is not yet hair-on-fire."
    )
    return {
        "totalInterviews": count,
        "fiValidationTarget": 15,
        "avgPainSeverity": avg_pain,
        "willingToPayPct": wtp_pct,
        "medianWtpUsd": round(median_wtp, 2),
        "pilotsPledged": pilots,
        "verdict": verdict,
        "recentQuotes": [i["verbatimQuote"] for i in items[-5:] if i.get("verbatimQuote")],
    }


def tool_pact_pipeline_manage(args: dict[str, Any]) -> dict[str, Any]:
    action = args.get("action", "summary")
    sdir = _startup_dir(args.get("workspace_path"))
    path = sdir / "pacts.json"
    items: list[dict[str, Any]] = _read_json(path, [])

    valid_statuses = ("prospect", "verbal", "pact_signed", "closed_cash", "lost")

    if action == "add":
        name = str(args.get("counterparty", "")).strip()
        kind = args.get("kind", "customer")
        if kind not in ("customer", "investor"):
            raise ValueError("'kind' must be 'customer' or 'investor'.")
        if not name:
            raise ValueError("'counterparty' is required when action='add'.")
        status = args.get("status", "prospect")
        if status not in valid_statuses:
            raise ValueError(f"'status' must be one of: {', '.join(valid_statuses)}")
        prob_defaults = {
            "prospect": 0.10,
            "verbal": 0.30,
            "pact_signed": 0.75,
            "closed_cash": 1.00,
            "lost": 0.0,
        }
        entry = {
            "id": f"PACT-{len(items) + 1:03d}",
            "kind": kind,
            "counterparty": name,
            "amountUsd": float(args.get("amount_usd", 0)),
            "targetCloseDate": args.get("target_close_date", ""),
            "status": status,
            "probability": float(args.get("probability", prob_defaults[status])),
            "notes": args.get("notes", ""),
            "createdAt": _now_iso(),
        }
        items.append(entry)
        _write_json(path, items)
        return {"added": entry}

    if action == "update":
        pid = args.get("id")
        target = next((x for x in items if x.get("id") == pid), None)
        if not target:
            raise ValueError(f"PACT '{pid}' not found.")
        if "status" in args and args["status"] is not None:
            if args["status"] not in valid_statuses:
                raise ValueError(f"'status' must be one of: {', '.join(valid_statuses)}")
            target["status"] = args["status"]
        if "amount_usd" in args and args["amount_usd"] is not None:
            target["amountUsd"] = float(args["amount_usd"])
        if "probability" in args and args["probability"] is not None:
            target["probability"] = float(args["probability"])
        if "notes" in args and args["notes"] is not None:
            target["notes"] = args["notes"]
        target["updatedAt"] = _now_iso()
        _write_json(path, items)
        return {"updated": target}

    kind_filter = args.get("kind")
    filtered = [x for x in items if not kind_filter or x.get("kind") == kind_filter]
    closed_cash = sum(x["amountUsd"] for x in filtered if x["status"] == "closed_cash")
    signed_pacts = sum(x["amountUsd"] for x in filtered if x["status"] == "pact_signed")
    weighted = sum(
        x["amountUsd"] * x.get("probability", 0)
        for x in filtered
        if x["status"] != "lost"
    )
    return {
        "count": len(filtered),
        "closedCashUsd": round(closed_cash, 2),
        "signedPactUsd": round(signed_pacts, 2),
        "probabilityWeightedUsd": round(weighted, 2),
        "pacts": filtered,
    }


def tool_financial_calc(args: dict[str, Any]) -> dict[str, Any]:
    mode = args.get("mode")

    if mode == "runway":
        cash = float(args.get("cash_usd", 0))
        burn = float(args.get("monthly_burn_usd", 0))
        rev = float(args.get("monthly_revenue_usd", 0))
        growth = float(args.get("monthly_growth_pct", 0)) / 100.0
        gross_margin = float(args.get("gross_margin_pct", 80)) / 100.0

        def simulate(g: float) -> dict[str, Any]:
            c = cash
            r = rev
            months = 0
            profitable_month = None
            while months < 60:
                gp = r * gross_margin
                net_flow = gp - burn
                if net_flow >= 0 and profitable_month is None:
                    profitable_month = months
                c += net_flow
                if c <= 0:
                    return {
                        "runwayMonths": months,
                        "defaultAlive": False,
                        "monthsToProfitable": profitable_month,
                    }
                r = r * (1.0 + g)
                months += 1
            return {
                "runwayMonths": "60+ (Default Alive)",
                "defaultAlive": True,
                "monthsToProfitable": profitable_month if profitable_month is not None else "profitable_now",
            }

        net_burn_now = round(burn - rev * gross_margin, 2)
        base = simulate(growth)
        return {
            "mode": "runway",
            "currentNetBurnUsd": net_burn_now,
            "defaultAlive": base["defaultAlive"],
            "scenarios": {
                "conservative": simulate(max(0.0, growth * 0.5)),
                "base": base,
                "optimistic": simulate(growth * 1.5),
            },
        }

    if mode == "unit_economics":
        arpa = float(args.get("arpa_monthly_usd", 0))
        gm = float(args.get("gross_margin_pct", 80)) / 100.0
        churn = float(args.get("monthly_churn_pct", 5)) / 100.0
        cac = float(args.get("cac_usd", 0))
        if churn <= 0:
            raise ValueError("'monthly_churn_pct' must be > 0.")
        gross_profit_monthly = arpa * gm
        avg_lifetime_months = 1.0 / churn
        ltv = gross_profit_monthly * avg_lifetime_months
        ltv_cac = (ltv / cac) if cac > 0 else math.inf
        payback_months = (cac / gross_profit_monthly) if gross_profit_monthly > 0 else math.inf

        health = "Strong — high-margin profit engine"
        if gm < 0.70:
            health = "Warning — gross margin below 70%; reduce COGS or raise value-based pricing."
        elif cac > 0 and ltv_cac < 3.0:
            health = "Warning — LTV:CAC below 3:1; lower CAC or cut churn before scaling."
        elif cac > 0 and payback_months > 12:
            health = "Caution — CAC payback exceeds 12 months; consider annual upfront billing."

        return {
            "mode": "unit_economics",
            "monthlyGrossProfitPerCustomerUsd": round(gross_profit_monthly, 2),
            "avgCustomerLifetimeMonths": round(avg_lifetime_months, 1),
            "ltvUsd": round(ltv, 2),
            "cacUsd": round(cac, 2),
            "ltvToCacRatio": round(ltv_cac, 2) if math.isfinite(ltv_cac) else "infinite (zero CAC)",
            "cacPaybackMonths": round(payback_months, 2) if math.isfinite(payback_months) else None,
            "verdict": health,
        }

    if mode == "tam_bottom_up":
        total_buyers = int(args.get("total_buyers", 0))
        acv = float(args.get("annual_acv_usd", 0))
        sam_pct = float(args.get("sam_pct", 20))
        som_buyers = int(args.get("som_buyers", 0))
        tam = total_buyers * acv
        sam = tam * (sam_pct / 100.0)
        som = som_buyers * acv
        som_share_of_sam = (som / sam * 100.0) if sam > 0 else 0.0
        return {
            "mode": "tam_bottom_up",
            "formula": f"{total_buyers:,} buyers × ${acv:,.0f} ACV",
            "tamUsd": round(tam, 2),
            "samUsd": round(sam, 2),
            "somUsd": round(som, 2),
            "somBuyers": som_buyers,
            "somShareOfSamPct": round(som_share_of_sam, 2),
            "vcScaleCheck": (
                "Venture-scale TAM ($1B+)"
                if tam >= 1_000_000_000
                else "Niche/Cash-Cow TAM (<$1B) — ideal for high-profit bootstrapping or strategic niche!"
            ),
        }

    if mode == "safe_dilution":
        raise_usd = float(args.get("raise_usd", 0))
        cap_usd = float(args.get("valuation_cap_usd", 0))
        safe_type = args.get("safe_type", "post_money")
        pool_pct = float(args.get("option_pool_pct", 10))
        founders = max(1, int(args.get("founder_count", 1)))
        if cap_usd <= 0:
            raise ValueError("'valuation_cap_usd' must be > 0.")

        if safe_type == "post_money":
            investor_pct = (raise_usd / cap_usd) * 100.0
        else:
            investor_pct = (raise_usd / (cap_usd + raise_usd)) * 100.0

        founders_total_pct = max(0.0, 100.0 - investor_pct - pool_pct)
        return {
            "mode": "safe_dilution",
            "safeType": safe_type,
            "raiseUsd": raise_usd,
            "valuationCapUsd": cap_usd,
            "investorOwnershipPct": round(investor_pct, 2),
            "optionPoolPct": round(pool_pct, 2),
            "foundersCombinedPct": round(founders_total_pct, 2),
            "perFounderEqualSplitPct": round(founders_total_pct / founders, 2),
            "disclaimer": "Educational SAFE dilution estimate only — confirm final cap table with startup counsel.",
        }

    if mode == "fast_advisor_equity":
        stage = str(args.get("stage", "idea")).lower()
        tier = str(args.get("tier", "standard")).lower()
        if stage not in FAST_EQUITY_MATRIX:
            raise ValueError("'stage' must be 'idea', 'startup', or 'growth'.")
        if tier not in FAST_EQUITY_MATRIX[stage]:
            raise ValueError("'tier' must be 'standard', 'strategic', or 'expert'.")
        row = FAST_EQUITY_MATRIX[stage][tier]
        return {
            "mode": "fast_advisor_equity",
            "framework": "Founder Institute FAST Agreement Standard",
            "stage": stage,
            "tier": tier,
            "recommendedEquityPct": row["equityPct"],
            "vestingScheduleMonths": 24,
            "cliffMonths": 3,
            "monthlyHoursCommitment": row["monthlyHours"],
            "engagementScope": row["meetings"],
            "monthlyVestingPct": round(row["equityPct"] / 24.0, 4),
            "disclaimer": "Based on FI FAST benchmarks. Review formal advisor agreements & 83(b) timelines with counsel.",
        }

    if mode == "cap_table_model":
        raw_founders = args.get("founders") or [{"name": "Founder 1", "pct": 100.0}]
        raw_advisors = args.get("advisors") or []
        safe_raise = float(args.get("safe_raise_usd", 0))
        safe_cap = float(args.get("safe_cap_usd", 0))
        safe_type = str(args.get("safe_type", "post_money"))
        seed_raise = float(args.get("seed_raise_usd", 0))
        seed_pre = float(args.get("seed_pre_money_usd", 0))
        seed_pool_pct = float(args.get("seed_option_pool_pct", 10.0))

        # Stage 1: Initial Founders + FI FAST Advisors (advisors dilute founders proportionally)
        advisor_total = sum(max(0.0, float(a.get("pct", 0))) for a in raw_advisors)
        founder_raw_sum = sum(max(0.0, float(f.get("pct", 0))) for f in raw_founders) or 100.0
        founder_pool_pre = max(0.0, 100.0 - advisor_total)

        pre_safe: list[dict[str, Any]] = []
        for f in raw_founders:
            pct = (float(f.get("pct", 0)) / founder_raw_sum) * founder_pool_pre
            pre_safe.append({"name": str(f.get("name", "Founder")), "role": "founder", "pct": round(pct, 2)})
        for a in raw_advisors:
            pre_safe.append({"name": str(a.get("name", "Advisor")), "role": "advisor_fast", "pct": round(float(a.get("pct", 0)), 2)})

        # Stage 2: Pre-Seed SAFE conversion
        safe_pct = 0.0
        if safe_raise > 0 and safe_cap > 0:
            if safe_type == "post_money":
                safe_pct = (safe_raise / safe_cap) * 100.0
            else:
                safe_pct = (safe_raise / (safe_cap + safe_raise)) * 100.0
        safe_scale = max(0.0, 100.0 - safe_pct) / 100.0

        post_safe: list[dict[str, Any]] = [
            {**row, "pct": round(row["pct"] * safe_scale, 2)} for row in pre_safe
        ]
        if safe_pct > 0:
            post_safe.append({"name": "Pre-Seed SAFE Investors", "role": "safe_investor", "pct": round(safe_pct, 2)})

        # Stage 3: Seed Priced Round + Option Pool Refresh
        seed_post_money = seed_pre + seed_raise if (seed_raise > 0 and seed_pre > 0) else 0.0
        seed_inv_pct = (seed_raise / seed_post_money * 100.0) if seed_post_money > 0 else 0.0
        pool_pct_applied = seed_pool_pct if seed_post_money > 0 else 0.0
        seed_scale = max(0.0, 100.0 - seed_inv_pct - pool_pct_applied) / 100.0

        post_seed: list[dict[str, Any]] = []
        for row in post_safe:
            new_pct = round(row["pct"] * seed_scale, 2)
            entry = {**row, "pct": new_pct}
            if seed_post_money > 0:
                entry["impliedValueUsd"] = round(seed_post_money * (new_pct / 100.0), 2)
            post_seed.append(entry)
        if pool_pct_applied > 0:
            post_seed.append(
                {
                    "name": "Employee Option Pool",
                    "role": "option_pool",
                    "pct": round(pool_pct_applied, 2),
                    "impliedValueUsd": round(seed_post_money * (pool_pct_applied / 100.0), 2),
                }
            )
        if seed_inv_pct > 0:
            post_seed.append(
                {
                    "name": "Seed Lead & Syndicate",
                    "role": "seed_investor",
                    "pct": round(seed_inv_pct, 2),
                    "impliedValueUsd": round(seed_raise, 2),
                }
            )

        founders_final_pct = round(sum(r["pct"] for r in post_seed if r["role"] == "founder"), 2)
        return {
            "mode": "cap_table_model",
            "seedPostMoneyValuationUsd": round(seed_post_money, 2),
            "foundersFinalCombinedPct": founders_final_pct,
            "stages": {
                "preSafe": pre_safe,
                "postSafe": post_safe,
                "postSeed": post_seed,
            },
            "disclaimer": "Educational multi-round cap table model — verify exact share math & pro-rata rights with startup counsel.",
        }

    raise ValueError(
        "Invalid mode. Use one of: runway, unit_economics, tam_bottom_up, safe_dilution, fast_advisor_equity, cap_table_model."
    )


def tool_pitch_deck_build(args: dict[str, Any]) -> dict[str, Any]:
    deck_path = args.get("deck_path")
    if not deck_path:
        ws = _resolve_workspace(args.get("workspace_path"))
        deck_path = str(ws / "pitch-deck" / "deck.json")
    p = Path(deck_path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Pitch deck JSON not found: {p}")
    return build_deck(p, export_pptx=bool(args.get("export_pptx", False)))


def tool_pitch_deck_design_brief(args: dict[str, Any]) -> dict[str, Any]:
    deck_path = args.get("deck_path")
    if not deck_path:
        ws = _resolve_workspace(args.get("workspace_path"))
        deck_path = str(ws / "pitch-deck" / "deck.json")
    p = Path(deck_path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Pitch deck JSON not found: {p}")
    target = str(args.get("target", "all")).lower()
    if target not in ("all", "both", "canva", "figma", "replit"):
        raise ValueError("'target' must be 'all', 'both', 'canva', 'figma', or 'replit'.")
    return export_design_briefs(p, target=target)


def tool_replit_workspace_prepare(args: dict[str, Any]) -> dict[str, Any]:
    """Scaffold zero-double-token Replit handoff config (.replit, replit.md, .env.example, docs/REPLIT_HANDOFF.md)."""
    ws = _resolve_workspace(args.get("workspace_path"))
    ws.mkdir(parents=True, exist_ok=True)
    app_type = str(args.get("app_type", "web-node")).lower()
    if app_type not in ("web-node", "web-python", "mobile-expo"):
        raise ValueError("'app_type' must be 'web-node', 'web-python', or 'mobile-expo'.")

    state = _read_json(ws / ".startup" / "state.json", {})
    company = str(args.get("company_name") or state.get("companyName") or "Your Startup")
    pitch = str(state.get("fiOneSentencePitch") or "Define via startup-kickstart.")

    replit_configs = {
        "web-node": {
            "label": "Full-Stack Web Platform (Node.js / Next.js / Vite)",
            "dot_replit": (
                'run = "npm run dev"\n'
                'entrypoint = "package.json"\n\n'
                "[nix]\n"
                'channel = "stable-24_05"\n\n'
                "[[ports]]\n"
                "localPort = 3000\n"
                "externalPort = 80\n"
            ),
            "env_example": (
                "# Copy these keys into Replit Secrets (NEVER commit real values to Git)\n"
                "DATABASE_URL=\n"
                "STRIPE_SECRET_KEY=\n"
                "STRIPE_PUBLISHABLE_KEY=\n"
                "APP_BASE_URL=\n"
            ),
            "preview_note": "Click Run in Replit to open the live Webview URL and share it with pilot customers.",
        },
        "web-python": {
            "label": "Full-Stack Web / API Platform (Python 3 / FastAPI / Flask)",
            "dot_replit": (
                'run = "python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"\n'
                'entrypoint = "main.py"\n\n'
                "[nix]\n"
                'channel = "stable-24_05"\n\n'
                "[[ports]]\n"
                "localPort = 8000\n"
                "externalPort = 80\n"
            ),
            "env_example": (
                "# Copy these keys into Replit Secrets (NEVER commit real values to Git)\n"
                "DATABASE_URL=\n"
                "STRIPE_SECRET_KEY=\n"
                "SECRET_KEY=\n"
            ),
            "preview_note": "Click Run in Replit to boot FastAPI/Uvicorn on port 8000 with instant public preview.",
        },
        "mobile-expo": {
            "label": "Cross-Platform Mobile App (React Native + Expo Go QR)",
            "dot_replit": (
                'run = "npx expo start --tunnel"\n'
                'entrypoint = "App.tsx"\n\n'
                "[nix]\n"
                'channel = "stable-24_05"\n\n'
                "[[ports]]\n"
                "localPort = 8081\n"
                "externalPort = 80\n"
            ),
            "env_example": (
                "# Copy these keys into Replit Secrets (NEVER commit real values to Git)\n"
                "EXPO_PUBLIC_API_URL=\n"
                "EXPO_PUBLIC_STRIPE_KEY=\n"
            ),
            "preview_note": "Install Expo Go on iOS/Android, click Run in Replit, and scan the QR code to test live on your phone.",
        },
    }
    cfg = replit_configs[app_type]

    replit_md = f"""# {company} — Replit Workspace Rules (Zero Double-Token Burn)

> **FI One-Sentence Pitch:** {pitch}
> **Stack Target:** `{app_type}` ({cfg['label']})

## CRITICAL: Antigravity + Replit Collaboration Contract
This repository is authored locally in **Google Antigravity** and synced to **Replit** via GitHub to avoid burning duplicate AI tokens on Replit's Free/Starter tier.

1. **Do NOT re-architect or rewrite existing features** already committed from Antigravity.
2. **Pull updates via Replit's Git pane** whenever local changes are pushed to GitHub (0 AI tokens used).
3. **Use Replit primarily for:**
   - **Replit Design Mode** (living style guide & visual UI iteration)
   - **Live Cloud Runtime, Postgres, Secrets & Hosting**
   - **Expo Go Mobile QR Previews** (for `mobile-expo` builds)
   - **One-Shot Replit Slides** (using `pitch-deck/design-handoff/REPLIT_SLIDES_BRIEF.md`)
4. **Gross Margin & Ethics Guardrail:** Keep architecture simple, maintain >=75% gross margins, never commit `.env` secrets, and reject dark patterns.
"""

    handoff_md = f"""# {company} — Antigravity to Replit Free-Tier Handoff

> **Get Started on Replit (Free Tier):** https://replit.com/refer/peterbiggam *(creator referral link & personal endorsement)*

## Why Use Replit Here?
Replit lets you run your **Design System (Design Mode)**, **Web Platform or Expo Mobile App**, **Managed DB & Secrets**, **1-Click Hosting**, and **Replit Slides** in one unified cloud workspace—eliminating local Docker, Xcode, or AWS setup while staying on the Free/Starter tier until paying customers fund upgrades.

## Zero-Double-Token Sync Steps
1. **Start Visually (Optional):** Prototype your core screen in **Replit Design Mode** first to establish your living Design System, then pull the tokens back locally.
2. **Push Local Antigravity Repo to Private GitHub:**
   ```bash
   gh repo create --private --source=. --remote=origin --push
   ```
3. **Import Into Replit:** Open [Replit](https://replit.com/refer/peterbiggam) -> **Create Repl -> Import from GitHub** -> select your private repository.
4. **Configure Replit Secrets:** Copy every variable name from `.env.example` into Replit's encrypted **Secrets** pane (never commit real keys).
5. **Run & Preview ({cfg['label']}):**
   - {cfg['preview_note']}
6. **Ongoing Zero-Token Loop:** Build heavy features locally in Antigravity -> `git push` -> click **Pull** in Replit's Git pane (0 Replit AI tokens consumed).
7. **Optional Replit Slides Deck:** Run `pitch_deck_design_brief(target="replit")` and paste `pitch-deck/design-handoff/REPLIT_SLIDES_BRIEF.md` into Replit Slides as a single one-shot prompt.
"""

    dot_replit_path = ws / ".replit"
    replit_md_path = ws / "replit.md"
    env_example_path = ws / ".env.example"
    handoff_path = ws / "docs" / "REPLIT_HANDOFF.md"

    dot_replit_path.write_text(cfg["dot_replit"], encoding="utf-8")
    replit_md_path.write_text(replit_md, encoding="utf-8")
    if not env_example_path.exists():
        env_example_path.write_text(cfg["env_example"], encoding="utf-8")
    handoff_path.parent.mkdir(parents=True, exist_ok=True)
    handoff_path.write_text(handoff_md, encoding="utf-8")

    return {
        "companyName": company,
        "appType": app_type,
        "replitSignupUrl": "https://replit.com/refer/peterbiggam",
        "filesCreated": [
            str(dot_replit_path),
            str(replit_md_path),
            str(env_example_path),
            str(handoff_path),
        ],
        "nextStep": "Push this workspace to a private GitHub repo, then Import from GitHub inside Replit (0 Replit AI tokens burned).",
    }


def tool_product_hunt_kit_build(args: dict[str, Any]) -> dict[str, Any]:
    """Lint Product Hunt limits & buzzwords and generate launch/product-hunt/PH_LAUNCH_KIT.md + launch-plan.json."""
    ws = _resolve_workspace(args.get("workspace_path"))
    state = _read_json(ws / ".startup" / "state.json", {})

    company = str(args.get("product_name") or state.get("companyName") or "Your Startup").strip()
    offering = str(state.get("offering") or "workflow automation software").strip()
    audience = str(state.get("audience") or "focused operators").strip()
    problem = str(state.get("problem") or "eliminate costly manual bottlenecks").strip()
    secret = str(state.get("secretSauce") or "purpose-built automation").strip()
    ikpi_obj = state.get("ikpi") or {}
    ikpi_name = str(ikpi_obj.get("name") or "Measurable customer progress tracked monthly")
    impact_thesis = str(state.get("impactThesis") or f"Deliver transparent, ethical ROI for {audience}.")

    default_tagline = f"{offering.capitalize()} for {audience}"
    if len(default_tagline) > 60:
        default_tagline = default_tagline[:57].rstrip() + "..."
    tagline = str(args.get("tagline") or default_tagline).strip()

    default_desc = (
        f"{company} helps {audience} {problem} using {secret}. "
        "Transparent value pricing, 100% customer-owned data, and measurable ROI in week one."
    )
    if len(default_desc) > 260:
        default_desc = default_desc[:257].rstrip() + "..."
    description = str(args.get("description") or default_desc).strip()

    topics = args.get("topics") or ["SaaS", "Productivity", "Developer Tools"]
    topics = [str(t).strip() for t in topics if str(t).strip()]
    ph_offer = str(
        args.get("ph_offer")
        or "Founding Product Hunt Community Offer: 25% off for 6 months + 14-day risk-free paid pilot guarantee."
    ).strip()
    launch_date = str(args.get("launch_date") or "TBD (Target Tuesday–Thursday at 12:01 AM PT)").strip()

    # Lint Product Hunt hard constraints + FI anti-buzzword discipline
    issues: list[dict[str, str]] = []
    if len(company) > 40:
        issues.append({"severity": "error", "rule": "ph-name-40", "message": f"Product name is {len(company)} chars (max 40)."})
    if len(tagline) > 60:
        issues.append({"severity": "error", "rule": "ph-tagline-60", "message": f"Tagline is {len(tagline)} chars (max 60)."})
    if len(description) > 260:
        issues.append({"severity": "error", "rule": "ph-desc-260", "message": f"Description is {len(description)} chars (max 260)."})
    if len(topics) > 3:
        issues.append({"severity": "warning", "rule": "ph-max-3-topics", "message": f"Selected {len(topics)} topics (Product Hunt allows max 3)."})

    lowered_copy = f"{tagline} {description}".lower()
    found_buzz = [bw for bw in BANNED_BUZZWORDS if bw in lowered_copy]
    if found_buzz:
        issues.append(
            {
                "severity": "warning",
                "rule": "fi-no-buzzwords",
                "message": f"Remove buzzwords from PH copy: {', '.join(found_buzz)}.",
            }
        )

    errors = sum(1 for i in issues if i["severity"] == "error")
    lint_report = {
        "passed": errors == 0,
        "nameChars": len(company),
        "taglineChars": len(tagline),
        "descriptionChars": len(description),
        "topicCount": len(topics),
        "issues": issues,
    }

    maker_comment = (
        f"Hey Product Hunt! 👋\n\n"
        f"I'm the founder of **{company}**. We built {company} after seeing firsthand how much time and money "
        f"{audience} lose trying to {problem}.\n\n"
        f"**What makes {company} different (our Secret Sauce):**\n"
        f"Instead of bloated enterprise setups or brittle spreadsheets, {company} uses {secret} so you see measurable ROI in your very first week.\n\n"
        f"**Our Ethical & For-Progress Commitment:**\n"
        f"- 100% customer-owned data (instant export, zero lock-in, 1-click cancel)\n"
        f"- Primary For-Progress iKPI we track alongside revenue: *{ikpi_name}*\n\n"
        f"**Product Hunt Community Offer:**\n"
        f"{ph_offer}\n\n"
        f"I'll be here all day answering every single question—would love your brutally honest feedback on what works and what we should sharpen next!"
    )

    out_dir = ws / "launch" / "product-hunt"
    out_dir.mkdir(parents=True, exist_ok=True)

    kit_md = f"""# {company} — Product Hunt Launch Kit

- **Target Launch Window:** `{launch_date}` (Schedule for **12:01 AM PT**)
- **Submission Lint Status:** `{"PASSED" if lint_report["passed"] else "NEEDS FIXES"}`
- **Mensarius Compliance:** Zero upvote rings, zero bots, zero fake urgency — focus on genuine feedback & paying conversions.

---

## 1. Exact Product Hunt Submission Fields

- **Product Name ({len(company)}/40 chars):** `{company}`
- **Tagline ({len(tagline)}/60 chars):** `{tagline}`
- **Topics ({len(topics)}/3):** {", ".join(f"`{t}`" for t in topics[:3])}
- **Description ({len(description)}/260 chars):**
  > {description}
- **Community Offer:** {ph_offer}

---

## 2. First Maker Comment (Post at 12:02 AM PT)

{maker_comment}

---

## 3. Gallery Image Storyboard (`1270 x 760 px` — Build in Canva or Figma)

> Pair with `design-studio-canva-figma` (`canva_canva` / `figma_figma`) or Replit screenshots.

1. **Thumbnail (`240 x 240 px`):** High-contrast `{company}` logo mark readable at feed size.
2. **Slide 1 — Clear Outcome Hero:** `{tagline}` + clean UI visual showing the core result.
3. **Slide 2 — 3-Step Workflow:** Step 1 (2-min connect) -> Step 2 (`{secret}`) -> Step 3 (Verified ROI output).
4. **Slide 3 — Live Product Screenshot:** Real annotated product screen (zero stock illustrations).
5. **Slide 4 — Honest Comparison / ROI Proof:** `{company}` vs. legacy tools & manual spreadsheets.
6. **Slide 5 — Transparent Pricing & For-Progress Charter:** `{impact_thesis}` + `{ph_offer}`.

---

## 4. Ethical Launch-Day Outreach Templates (Zero Upvote Begging)

### Warm Supporter / FI Mentor / Pilot Customer Note
> Subject: We're live on Product Hunt today — would love your honest take!
>
> Hey [Name], thanks again for your feedback while we built {company}. We just launched on Product Hunt today to help {audience} {problem}.
>
> If you have 2 minutes, I'd genuinely appreciate your honest feedback or a tough question in the comments: [Product Hunt URL]
>
> — [Founder Name]

### LinkedIn / X Launch Post
> Today we're launching **{company}** on Product Hunt.
>
> Why we built it: {audience} lose way too much time and cash trying to {problem}.
>
> How it works: {secret} — delivering clear ROI in week one with transparent pricing and 100% customer-owned data.
>
> Come tear it apart and ask us anything in the comments today: [Product Hunt URL]

---

## 5. Launch-Day Execution Checklist
- [ ] Coming Soon teaser live by T-7 days
- [ ] Live landing page (`landing/index.html`) or Replit URL + checkout verified end-to-end
- [ ] 60–90s founder demo video uploaded (real product shown in first 5 seconds)
- [ ] Launch scheduled for 12:01 AM PT; First Maker Comment posted at 12:02 AM PT
- [ ] Reply to every comment inside 15 minutes; log warm buyer leads into `pact_pipeline_manage(kind="customer")`
"""

    kit_path = out_dir / "PH_LAUNCH_KIT.md"
    plan_path = out_dir / "launch-plan.json"
    plan_data = {
        "productName": company,
        "tagline": tagline,
        "description": description,
        "topics": topics[:3],
        "phOffer": ph_offer,
        "launchDate": launch_date,
        "lint": lint_report,
        "generatedAt": _now_iso(),
    }

    kit_path.write_text(kit_md, encoding="utf-8")
    plan_path.write_text(json.dumps(plan_data, indent=2) + "\n", encoding="utf-8")

    return {
        "kitPath": str(kit_path),
        "planPath": str(plan_path),
        "lint": lint_report,
        "nextStep": "Review PH_LAUNCH_KIT.md, generate 1270x760 gallery visuals in Canva/Figma, and schedule launch for 12:01 AM PT.",
    }


def tool_ai_connectors_manage(args: dict[str, Any]) -> dict[str, Any]:
    action = str(args.get("action", "detect")).lower()
    if action == "detect":
        return detect_connectors()
    if action == "sync_context":
        ws = _resolve_workspace(args.get("workspace_path"))
        targets = args.get("targets") if isinstance(args.get("targets"), list) else ["all"]
        return sync_ai_context(ws, targets)
    if action == "second_opinion":
        provider = str(args.get("provider", "")).strip()
        prompt = str(args.get("prompt", "")).strip()
        if not provider or not prompt:
            raise ValueError("'provider' and 'prompt' are required when action='second_opinion'.")
        ws = _resolve_workspace(args.get("workspace_path")) if args.get("workspace_path") else None
        return run_second_opinion(
            provider=provider,
            prompt=prompt,
            workspace_path=ws,
            model=args.get("model"),
            dry_run=bool(args.get("dry_run", False)),
        )
    raise ValueError("Invalid action. Use 'detect', 'sync_context', or 'second_opinion'.")


def _compute_pmf_scorecard(pmf_data: dict[str, Any]) -> dict[str, Any]:
    surveys: list[dict[str, Any]] = pmf_data.get("surveys") or []
    cohorts: list[dict[str, Any]] = pmf_data.get("cohorts") or []
    total = len(surveys)

    if total == 0:
        return {
            "totalResponses": 0,
            "recommendedMinSample": 15,
            "seanEllisScorePct": 0.0,
            "payingPct": 0.0,
            "organicReferralPct": 0.0,
            "segmentBreakdown": [],
            "strongestSegment": None,
            "retentionLatest": cohorts[-1] if cohorts else None,
            "roadmap5050": {"doubleDownOn": [], "fixFrictionFor": [], "ignoreCount": 0},
            "verdict": "NO_DATA",
            "recommendation": "Log real user responses via pmf_engine_manage(action='log_survey') before scaling GTM.",
        }

    very = [s for s in surveys if s.get("disappointment") == "very_disappointed"]
    somewhat = [s for s in surveys if s.get("disappointment") == "somewhat_disappointed"]
    not_dis = [s for s in surveys if s.get("disappointment") == "not_disappointed"]

    se_score = round((len(very) / total) * 100.0, 1)
    paying_pct = round((sum(1 for s in surveys if s.get("paying")) / total) * 100.0, 1)
    ref_pct = round((sum(1 for s in surveys if s.get("referredSomeone")) / total) * 100.0, 1)

    # Per-segment Superhuman HXC breakdown
    seg_buckets: dict[str, list[dict[str, Any]]] = {}
    for s in surveys:
        seg = str(s.get("userSegment") or "Unspecified").strip()
        seg_buckets.setdefault(seg, []).append(s)

    seg_rows: list[dict[str, Any]] = []
    for seg, rows in seg_buckets.items():
        v_cnt = sum(1 for r in rows if r.get("disappointment") == "very_disappointed")
        pct = round((v_cnt / len(rows)) * 100.0, 1)
        seg_rows.append(
            {
                "segment": seg,
                "responses": len(rows),
                "veryDisappointedCount": v_cnt,
                "pmfScorePct": pct,
                "meets40PctRule": pct >= 40.0,
            }
        )
    seg_rows.sort(key=lambda x: (-x["pmfScorePct"], -x["responses"]))
    strongest = seg_rows[0] if seg_rows else None
    has_winning_niche = any(r["pmfScorePct"] >= 40.0 and r["responses"] >= 3 for r in seg_rows)

    latest_cohort = cohorts[-1] if cohorts else None
    retention_flattening = None
    if latest_cohort:
        d30 = float(latest_cohort.get("day30Pct", 0))
        d90 = latest_cohort.get("day90Pct")
        if d90 is not None:
            retention_flattening = float(d90) >= max(20.0, d30 * 0.75)
        else:
            retention_flattening = d30 >= 40.0

    if se_score >= 40.0 and (retention_flattening is not False):
        verdict = "PMF_PROVEN_READY_TO_SCALE"
        rec = (
            f"Strong PMF signal ({se_score}% Very Disappointed >= 40% Sean Ellis bar). "
            "Green light to scale repeatable GTM channels and document validated proof for investors."
        )
    elif se_score >= 25.0 or has_winning_niche:
        verdict = "APPROACHING_PMF_NARROW_ICP"
        niche_hint = (
            f" Segment '{strongest['segment']}' is already at {strongest['pmfScorePct']}%!"
            if strongest and strongest["pmfScorePct"] >= 40.0
            else ""
        )
        rec = (
            f"Emerging PMF ({se_score}% overall).{niche_hint} Narrow ICP to your High-Expectation "
            "Customer segment and execute the 50/50 roadmap before spending on broad acquisition."
        )
    else:
        verdict = "PRE_PMF_PIVOT_RISK"
        rec = (
            f"Weak PMF signal ({se_score}% Very Disappointed < 25%). Do NOT spend on paid ads or heavy "
            "engineering—re-run Mom Test discovery (`revenue-first-validation`) or pivot ICP/problem."
        )

    return {
        "totalResponses": total,
        "recommendedMinSample": 15,
        "sampleConfidence": "high" if total >= 30 else ("moderate" if total >= 15 else "early_signal"),
        "seanEllisScorePct": se_score,
        "counts": {
            "veryDisappointed": len(very),
            "somewhatDisappointed": len(somewhat),
            "notDisappointed": len(not_dis),
        },
        "payingPct": paying_pct,
        "organicReferralPct": ref_pct,
        "segmentBreakdown": seg_rows,
        "strongestSegment": strongest,
        "retentionLatest": latest_cohort,
        "retentionFlattening": retention_flattening,
        "roadmap5050": {
            "doubleDownOn": [s["mainBenefit"] for s in very if s.get("mainBenefit")][:5],
            "fixFrictionFor": [s["requestedImprovement"] for s in somewhat if s.get("requestedImprovement")][:5],
            "ignoreCount": len(not_dis),
        },
        "verdict": verdict,
        "recommendation": rec,
    }


def tool_pmf_engine_manage(args: dict[str, Any]) -> dict[str, Any]:
    action = str(args.get("action", "scorecard")).lower()
    ws = _resolve_workspace(args.get("workspace_path"))
    sdir = _startup_dir(args.get("workspace_path"))
    pmf_path = sdir / "pmf.json"
    pmf_data: dict[str, Any] = _read_json(pmf_path, {"surveys": [], "cohorts": []})

    if action == "log_survey":
        dis = str(args.get("disappointment", "")).lower().strip()
        if dis not in ("very_disappointed", "somewhat_disappointed", "not_disappointed"):
            raise ValueError("'disappointment' must be 'very_disappointed', 'somewhat_disappointed', or 'not_disappointed'.")
        entry = {
            "id": f"PMF-{len(pmf_data['surveys']) + 1:03d}",
            "userSegment": str(args.get("user_segment") or "Core ICP").strip(),
            "disappointment": dis,
            "mainBenefit": str(args.get("main_benefit") or "").strip(),
            "requestedImprovement": str(args.get("requested_improvement") or "").strip(),
            "paying": bool(args.get("paying", False)),
            "referredSomeone": bool(args.get("referred_someone", False)),
            "loggedAt": _now_iso(),
        }
        pmf_data["surveys"].append(entry)
        _write_json(pmf_path, pmf_data)
        return {"logged": entry, "scorecard": _compute_pmf_scorecard(pmf_data)}

    if action == "record_retention":
        label = str(args.get("cohort_label") or "").strip()
        if not label:
            raise ValueError("'cohort_label' is required when action='record_retention'.")
        cohort = {
            "cohortLabel": label,
            "cohortSize": max(1, int(args.get("cohort_size", 1))),
            "day7Pct": float(args.get("day7_pct", 0)),
            "day30Pct": float(args.get("day30_pct", 0)),
            "day90Pct": float(args["day90_pct"]) if args.get("day90_pct") is not None else None,
            "netDollarRetentionPct": float(args["net_dollar_retention_pct"])
            if args.get("net_dollar_retention_pct") is not None
            else None,
            "recordedAt": _now_iso(),
        }
        pmf_data["cohorts"].append(cohort)
        _write_json(pmf_path, pmf_data)
        return {"recorded": cohort, "scorecard": _compute_pmf_scorecard(pmf_data)}

    scorecard = _compute_pmf_scorecard(pmf_data)
    if action == "generate_report":
        state = _read_json(sdir / "state.json", {})
        company = state.get("companyName", "Startup")
        seg_lines = [
            f"| {r['segment']} | {r['responses']} | {r['pmfScorePct']}% | {'YES (>=40%)' if r['meets40PctRule'] else 'Below 40%'} |"
            for r in scorecard["segmentBreakdown"]
        ] or ["| No survey responses logged yet | 0 | 0% | — |"]
        double_down = scorecard["roadmap5050"]["doubleDownOn"] or ["Collect more `very_disappointed` main-benefit responses."]
        fix_friction = scorecard["roadmap5050"]["fixFrictionFor"] or ["Collect more `somewhat_disappointed` improvement requests."]
        ret = scorecard["retentionLatest"]
        ret_line = (
            f"Cohort `{ret['cohortLabel']}` (n={ret['cohortSize']}): D7={ret['day7Pct']}%, D30={ret['day30Pct']}%"
            + (f", D90={ret['day90Pct']}%" if ret.get("day90Pct") is not None else "")
            + (f", NDR={ret['netDollarRetentionPct']}%" if ret.get("netDollarRetentionPct") is not None else "")
            if ret
            else "No retention cohorts logged yet — log via `pmf_engine_manage(action='record_retention')`."
        )

        md = "\n".join(
            [
                f"# {company} — Product-Market Fit (PMF) Scorecard",
                "",
                f"- **Verdict:** `{scorecard['verdict']}`",
                f"- **Sean Ellis Score (% Very Disappointed):** `{scorecard['seanEllisScorePct']}%` (Target: `>= 40%` | Responses: `{scorecard['totalResponses']}`)",
                f"- **Paying Customers Share:** `{scorecard['payingPct']}%` | **Organic Referral Share:** `{scorecard['organicReferralPct']}%`",
                f"- **Retention Check:** {ret_line}",
                "",
                f"> **Actionable Guidance:** {scorecard['recommendation']}",
                "",
                "## Segment-by-Segment PMF Breakdown (Superhuman HXC Discovery)",
                "| User Segment | Responses | % Very Disappointed | 40% Rule |",
                "| :--- | ---: | ---: | :--- |",
                *seg_lines,
                "",
                "## Superhuman 50/50 PMF Roadmap",
                "### 50% — Double Down On What `Very Disappointed` Users Love",
                *[f"- {x}" for x in double_down],
                "",
                "### 50% — Fix Top Blockers for `Somewhat Disappointed` Users",
                *[f"- {x}" for x in fix_friction],
                "",
                f"*Ignored `{scorecard['roadmap5050']['ignoreCount']}` `not_disappointed` responses so the roadmap stays razor-focused on true high-fit buyers.*",
                "",
            ]
        )
        out_path = ws / "docs" / "PMF_SCORECARD.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        return {"reportPath": str(out_path), "scorecard": scorecard, "markdown": md}

    return scorecard


STAGE_RECOMMENDED_SKILLS: dict[str, list[str]] = {
    "idea": ["startup-kickstart", "revenue-first-validation", "pitch-deck-builder"],
    "validation": ["revenue-first-validation", "market-and-unfair-moat", "replit-launchpad"],
    "mvp": ["mvp-and-profit-architecture", "product-market-fit-engine", "product-hunt-launch", "weekly-sprint-review"],
    "pre_seed_traction": ["product-market-fit-engine", "gtm-and-cash-velocity", "unit-economics-and-profit-os", "vc-lab-fundraising-os"],
    "seed_scale": ["vc-lab-fundraising-os", "quickbooks-cfo-and-zapier", "fi-alumni-scale-stack", "weekly-sprint-review"],
}


def tool_founder_resources_hub(args: dict[str, Any]) -> dict[str, Any]:
    action = str(args.get("action", "search")).lower()
    builtin: list[dict[str, Any]] = _read_json(FOUNDER_RESOURCES_PATH, [])
    ws_raw = args.get("workspace_path")
    custom: list[dict[str, Any]] = []
    if ws_raw:
        custom_path = _resolve_workspace(ws_raw) / ".startup" / "custom_resources.json"
        custom = _read_json(custom_path, [])

    combined = builtin + custom

    if action == "save_custom":
        sdir = _startup_dir(ws_raw)
        cpath = sdir / "custom_resources.json"
        existing: list[dict[str, Any]] = _read_json(cpath, [])
        title = str(args.get("title", "")).strip()
        url = str(args.get("url", "")).strip()
        if not title:
            raise ValueError("'title' is required when action='save_custom'.")
        entry = {
            "id": f"CUST-{len(existing) + 1:03d}",
            "title": title,
            "category": str(args.get("category") or "custom").strip().lower(),
            "stages": args.get("stages") or ["idea", "validation", "mvp", "pre_seed_traction", "seed_scale"],
            "format": str(args.get("format") or "playbook").strip().lower(),
            "source": str(args.get("source") or "Founder Custom Bookmark").strip(),
            "url": url,
            "summary": str(args.get("summary") or "").strip(),
            "keyTakeaway": str(args.get("key_takeaway") or "").strip(),
            "tags": [str(t).strip().lower() for t in (args.get("tags") or []) if str(t).strip()],
            "savedAt": _now_iso(),
        }
        existing.append(entry)
        _write_json(cpath, existing)
        return {"saved": entry, "totalCustomResources": len(existing)}

    if action == "categories":
        counts: dict[str, int] = {}
        for item in combined:
            cat = str(item.get("category", "uncategorized"))
            counts[cat] = counts.get(cat, 0) + 1
        return {
            "totalResources": len(combined),
            "builtinCount": len(builtin),
            "customCount": len(custom),
            "categories": [
                {"category": k, "count": v}
                for k, v in sorted(counts.items(), key=lambda x: (-x[1], x[0]))
            ],
        }

    if action == "stage_kit":
        stage = str(args.get("stage") or "").strip().lower()
        if not stage and ws_raw:
            state = _read_json(_resolve_workspace(ws_raw) / ".startup" / "state.json", {})
            stage = str(state.get("stage") or "idea").lower()
        if stage not in FI_STAGE_BENCHMARKS:
            stage = "idea"
        limit = max(1, min(20, int(args.get("limit", 8))))
        matched = [r for r in combined if stage in (r.get("stages") or [])][:limit]
        return {
            "stage": stage,
            "fiBenchmark": FI_STAGE_BENCHMARKS[stage],
            "recommendedSkills": STAGE_RECOMMENDED_SKILLS.get(stage, []),
            "matchCount": len(matched),
            "resources": matched,
        }

    # search
    query = str(args.get("query", "")).strip().lower()
    cat_filter = str(args.get("category", "")).strip().lower()
    stage_filter = str(args.get("stage", "")).strip().lower()
    fmt_filter = str(args.get("format", "")).strip().lower()
    limit = max(1, min(32, int(args.get("limit", 6))))
    tokens = [t for t in query.split() if t]

    scored: list[tuple[int, dict[str, Any]]] = []
    for item in combined:
        if cat_filter and str(item.get("category", "")).lower() != cat_filter:
            continue
        if stage_filter and stage_filter not in [s.lower() for s in (item.get("stages") or [])]:
            continue
        if fmt_filter and str(item.get("format", "")).lower() != fmt_filter:
            continue
        if not tokens:
            scored.append((1, item))
        else:
            tags = [str(t).lower() for t in (item.get("tags") or [])]
            blob = " ".join(
                [
                    str(item.get("title", "")),
                    str(item.get("summary", "")),
                    str(item.get("keyTakeaway", "")),
                    str(item.get("source", "")),
                    str(item.get("category", "")),
                    " ".join(tags),
                ]
            ).lower()
            score = sum(3 if t in tags else (1 if t in blob else 0) for t in tokens)
            if score > 0:
                scored.append((score, item))

    scored.sort(key=lambda x: (-x[0], x[1].get("id", "")))
    matches = [item for _, item in scored[:limit]]
    return {
        "query": query,
        "filters": {"category": cat_filter or None, "stage": stage_filter or None, "format": fmt_filter or None},
        "totalCatalogSize": len(combined),
        "matchCount": len(matches),
        "resources": matches,
    }


def tool_founder_dashboard_build(args: dict[str, Any]) -> dict[str, Any]:
    ws = _resolve_workspace(args.get("workspace_path"))
    return build_dashboard(ws)


def tool_data_room_build(args: dict[str, Any]) -> dict[str, Any]:
    ws = _resolve_workspace(args.get("workspace_path"))
    return build_data_room(ws)


def tool_ai_x402_calc(args: dict[str, Any]) -> dict[str, Any]:
    needs_ws = args.get("workspace_path") or args.get("write_spec") or args.get("action") == "x402_starter_scaffold"
    ws = _resolve_workspace(args.get("workspace_path")) if needs_ws else None
    return run_ai_x402_calc(args, workspace=ws)


def tool_board_review_run(args: dict[str, Any]) -> dict[str, Any]:
    ws = _resolve_workspace(args.get("workspace_path"))
    write_memo = bool(args.get("write_memo", True))
    return run_board_review(ws, write_memo=write_memo)


def tool_exponential_audit(args: dict[str, Any]) -> dict[str, Any]:
    needs_ws = args.get("workspace_path") or args.get("write_doc")
    ws = _resolve_workspace(args.get("workspace_path")) if needs_ws else None
    return run_exponential_audit(args, workspace=ws)


def tool_voice_pitch_coach(args: dict[str, Any]) -> dict[str, Any]:
    return analyze_voice_pitch(
        transcript=str(args.get("transcript", "")),
        duration_seconds=float(args.get("duration_seconds", 180.0)),
        target_seconds=float(args.get("target_seconds", 180.0)),
    )


def tool_war_room_run(args: dict[str, Any]) -> dict[str, Any]:
    ws = _resolve_workspace(args.get("workspace_path"))
    return run_war_room(
        workspace=ws,
        question=str(args.get("question", "")),
        write_memo=bool(args.get("write_memo", True)),
    )


def tool_i18n_locale_manage(args: dict[str, Any]) -> dict[str, Any]:
    action = str(args.get("action", "list")).strip()
    if action == "list":
        langs = list_supported_languages()
        return {"ok": True, "count": len(langs), "languages": langs}
    if action == "set":
        ws = _resolve_workspace(args.get("workspace_path"))
        return set_workspace_locale(ws, str(args.get("locale", "en")))
    raise ValueError("action must be 'list' or 'set'.")


def tool_competitor_manage(args: dict[str, Any]) -> dict[str, Any]:
    """Track structured competitors in .startup/competitors.json and export battlecards."""
    ws = _resolve_workspace(args.get("workspace_path"))
    sdir = ws / ".startup"
    sdir.mkdir(parents=True, exist_ok=True)
    comp_file = sdir / "competitors.json"
    items: list[dict[str, Any]] = []
    if comp_file.exists():
        try:
            items = json.loads(comp_file.read_text(encoding="utf-8"))
        except Exception:
            items = []

    action = str(args.get("action", "list")).strip()
    if action == "list":
        return {"count": len(items), "competitors": items}

    if action == "add":
        name = str(args.get("name", "")).strip()
        if not name:
            raise ValueError("'name' is required to add a competitor.")
        entry = {
            "id": f"COMP-{len(items) + 1:02d}",
            "name": name,
            "pricing": str(args.get("pricing", "Unknown")).strip(),
            "icp": str(args.get("icp", "")).strip(),
            "strengths": str(args.get("strengths", "")).strip(),
            "weaknesses": str(args.get("weaknesses", "")).strip(),
            "ourEdge": str(args.get("our_edge", "")).strip(),
            "xScore": max(0, min(100, int(args.get("x_score", 40)))),
            "yScore": max(0, min(100, int(args.get("y_score", 45)))),
        }
        items.append(entry)
        comp_file.write_text(json.dumps(items, indent=2), encoding="utf-8")
        return {"ok": True, "added": entry, "count": len(items)}

    if action == "remove":
        target_id = str(args.get("id", "")).strip()
        before = len(items)
        items = [c for c in items if c.get("id") != target_id and c.get("name") != target_id]
        comp_file.write_text(json.dumps(items, indent=2), encoding="utf-8")
        return {"ok": True, "removed": before - len(items), "count": len(items)}

    if action == "export_battlecard":
        docs_dir = ws / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        bc_file = docs_dir / "COMPETITOR_BATTLECARD.md"
        lines = [
            "# Competitive Landscape & FI Secret Sauce Battlecard",
            "",
            "| Competitor | Pricing | Target ICP | Weaknesses | Our Unfair Edge |",
            "| :--- | :--- | :--- | :--- | :--- |",
        ]
        for c in items:
            lines.append(
                f"| **{c.get('name', '')}** | {c.get('pricing', '')} | {c.get('icp', '')} | {c.get('weaknesses', '')} | {c.get('ourEdge', '')} |"
            )
        if not items:
            lines.append("| *(None logged yet)* | — | — | — | Run `competitor_manage(action='add')` |")
        bc_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"ok": True, "battlecardPath": str(bc_file), "count": len(items)}

    raise ValueError(f"Unknown competitor_manage action '{action}'. Use 'list', 'add', 'remove', or 'export_battlecard'.")


def tool_transcript_ingest(args: dict[str, Any]) -> dict[str, Any]:
    """Extract structured Mom Test discovery signals from raw call transcripts and optionally log into .startup/interviews.json."""
    text = str(args.get("transcript_text") or "").strip()
    if not text:
        raise ValueError("'transcript_text' is required.")
    persona = str(args.get("persona") or "Interviewee").strip()
    segment = str(args.get("company_segment") or "").strip()

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.strip()) >= 12]
    lower = text.lower()

    # Extract dollar amounts ($500, $4,000, $10k)
    money_vals: list[float] = []
    for m in re.finditer(r"\$\s*([0-9][0-9,]*(?:\.[0-9]+)?)\s*([kKmM])?", text):
        raw_num = float(m.group(1).replace(",", ""))
        suffix = (m.group(2) or "").lower()
        if suffix == "k":
            raw_num *= 1000.0
        elif suffix == "m":
            raw_num *= 1_000_000.0
        money_vals.append(raw_num)

    # Pain urgency scoring (1-5)
    pain_hits = re.findall(
        r"\b(hate|painful|nightmare|broken|losing|waste|wasting|hours|manual|frustrat\w*|expensive|headache|error|rejected|urgent|costly)\b",
        lower,
    )
    pain_severity = min(5, max(1, 2 + len(set(pain_hits)) // 2))
    if len(money_vals) > 0 and pain_severity < 4:
        pain_severity = 4

    # Workaround detection
    workarounds = sorted(
        set(
            re.findall(
                r"\b(spreadsheet|spreadsheets|excel|google sheets|manual|agency|agencies|email|intern|contractor|legacy|quickbooks|csv|pdf)\b",
                lower,
            )
        )
    )
    workaround_str = ", ".join(workarounds) if workarounds else "Not explicitly stated"

    # Pilot / buying pull detection
    pilot_intent = bool(
        re.search(
            r"\b(pilot|sign|pay for|willing to pay|budget|next week|when can we start|send (me |us )?(a |the )?(contract|invoice|pact|link))\b",
            lower,
        )
    )

    # Mom Test bias detector (flags leading founder questions in transcript)
    mom_test_warnings: list[str] = []
    if re.search(r"\b(would you (use|pay|buy)|do you think this is a good idea|do you like our)\b", lower):
        mom_test_warnings.append(
            "Detected leading/hypothetical Mom Test question ('would you use/pay...' or 'do you like...'). "
            "Weight future-tense praise lower than past spend or signed PACTs."
        )

    # Pick highest-signal verbatim quotes
    scored_quotes: list[tuple[int, str]] = []
    for s in sentences:
        sl = s.lower()
        qscore = (
            (3 if "$" in s else 0)
            + (2 if re.search(r"\b(hate|losing|waste|hours|manual|broken|spreadsheet|pilot|pay)\b", sl) else 0)
        )
        if qscore > 0:
            scored_quotes.append((qscore, s))
    scored_quotes.sort(key=lambda x: -x[0])
    top_quotes = [q for _, q in scored_quotes[:3]] or sentences[:1]

    wtp_guess = min(money_vals) if money_vals else 0.0
    extracted = {
        "persona": persona,
        "companySegment": segment,
        "estimatedPainSeverity": pain_severity,
        "currentWorkaround": workaround_str,
        "dollarAmountsMentioned": sorted(set(round(v, 2) for v in money_vals)),
        "estimatedWtpUsd": round(wtp_guess, 2),
        "pledgedPilotSignal": pilot_intent,
        "topVerbatimQuotes": top_quotes,
        "momTestBiasWarnings": mom_test_warnings,
    }

    logged_entry = None
    if bool(args.get("auto_log", True)) and args.get("workspace_path"):
        logged_entry = tool_interview_manage(
            {
                "action": "log",
                "workspace_path": args["workspace_path"],
                "persona": persona,
                "company_segment": segment,
                "pain_severity": pain_severity,
                "current_workaround": workaround_str,
                "willingness_to_pay_usd": wtp_guess,
                "pledged_pilot": pilot_intent,
                "verbatim_quote": top_quotes[0] if top_quotes else "",
            }
        )

    return {
        "extracted": extracted,
        "loggedInterview": logged_entry,
        "nextStep": (
            "Strong pilot signal detected — immediately offer a 1-page Paid Pilot PACT and log in pact_pipeline_manage!"
            if pilot_intent or pain_severity >= 4
            else "Review extracted workaround & pain; dig deeper on past budget spent in next discovery call."
        ),
    }


def tool_landing_page_build(args: dict[str, Any]) -> dict[str, Any]:
    ws = _resolve_workspace(args.get("workspace_path"))
    overrides = args.get("overrides") if isinstance(args.get("overrides"), dict) else {}
    if args.get("contact_email"):
        overrides["contactEmail"] = str(args["contact_email"])
    return build_landing_page(ws, overrides or None)


def tool_ikpi_catalog_search(args: dict[str, Any]) -> dict[str, Any]:
    catalog: list[dict[str, Any]] = _read_json(IKPI_CATALOG_PATH, [])
    query = str(args.get("query", "")).strip().lower()
    sdg_num = args.get("sdg_number")
    limit = max(1, min(20, int(args.get("limit", 5))))

    results: list[tuple[int, dict[str, Any]]] = []
    tokens = [t for t in query.split() if t]
    for item in catalog:
        if sdg_num is not None and int(item.get("sdgNumber", 0)) != int(sdg_num):
            continue
        blob = " ".join(
            [
                str(item.get("sdgName", "")),
                str(item.get("metricName", "")),
                str(item.get("measurementFormula", "")),
                " ".join(item.get("sectorTags", [])),
            ]
        ).lower()
        if not tokens:
            results.append((1, item))
        else:
            score = sum(2 if t in item.get("sectorTags", []) else (1 if t in blob else 0) for t in tokens)
            if score > 0:
                results.append((score, item))

    results.sort(key=lambda x: (-x[0], x[1]["sdgNumber"], x[1]["id"]))
    matches = [item for _, item in results[:limit]]
    return {
        "query": query,
        "sdgFilter": sdg_num,
        "totalCatalogEntries": len(catalog),
        "matchCount": len(matches),
        "matches": matches,
    }


def tool_sprint_manage(args: dict[str, Any]) -> dict[str, Any]:
    action = args.get("action", "list")
    ws = _resolve_workspace(args.get("workspace_path"))
    sdir = _startup_dir(args.get("workspace_path"))
    sprints_path = sdir / "sprints.json"
    sprints: list[dict[str, Any]] = _read_json(sprints_path, [])

    if action == "start":
        goal = str(args.get("primary_goal", "")).strip()
        if not goal:
            raise ValueError("'primary_goal' is required when action='start'.")
        week_num = len(sprints) + 1
        entry = {
            "id": f"SPRINT-{week_num:03d}",
            "weekLabel": args.get("week_label") or f"Week {week_num}",
            "primaryGoal": goal,
            "targets": {
                "interviews": int(args.get("target_interviews", 5)),
                "pacts": int(args.get("target_pacts", 2)),
                "mrrDeltaUsd": float(args.get("target_mrr_delta_usd", 0)),
            },
            "actuals": {},
            "status": "active",
            "startedAt": _now_iso(),
        }
        sprints.append(entry)
        _write_json(sprints_path, sprints)

        state_file = sdir / "state.json"
        if state_file.exists():
            state = _read_json(state_file, {})
            state["activeSprintGoal"] = goal
            state["updatedAt"] = _now_iso()
            _write_json(state_file, state)
        return {"started": entry, "totalSprints": len(sprints)}

    if action == "close":
        sid = args.get("id")
        target = (
            next((x for x in sprints if x.get("id") == sid), None)
            if sid
            else next((x for x in reversed(sprints) if x.get("status") == "active"), None)
        )
        if not target:
            raise ValueError("No active sprint found to close.")
        score = max(1.0, min(5.0, float(args.get("fi_velocity_score", 3.5))))
        target["status"] = "closed"
        target["actuals"] = {
            "interviewsCompleted": int(args.get("interviews_completed", 0)),
            "pactsSent": int(args.get("pacts_sent", 0)),
            "pactsSigned": int(args.get("pacts_signed", 0)),
            "mrrDeltaUsd": float(args.get("mrr_delta_usd", 0)),
            "ikpiDelta": float(args.get("ikpi_delta", 0)),
            "fiVelocityScore": round(score, 1),
        }
        target["highlights"] = args.get("highlights") or []
        target["lowlights"] = args.get("lowlights") or []
        target["blockers"] = args.get("blockers") or []
        target["closedAt"] = _now_iso()
        _write_json(sprints_path, sprints)
        return {"closed": target}

    if action == "investor_update":
        state = _read_json(sdir / "state.json", {})
        interviews = _read_json(sdir / "interviews.json", [])
        pacts = _read_json(sdir / "pacts.json", [])
        closed_sprints = [s for s in sprints if s.get("status") == "closed"]
        latest = closed_sprints[-1] if closed_sprints else (sprints[-1] if sprints else {})

        company = state.get("companyName", "Startup")
        mrr = float(state.get("mrrUsd", 0))
        burn = float(state.get("monthlyBurnUsd", 0))
        cash = float(state.get("cashOnHandUsd", 0))
        gm = float(state.get("grossMarginPct", 80))
        net_burn = max(0.0, burn - mrr * (gm / 100.0))
        runway_str = "Default-Alive" if net_burn == 0 else f"{round(cash / net_burn, 1)} months"
        cust_pacts = sum(
            float(p.get("amountUsd", 0))
            for p in pacts
            if p.get("kind") == "customer" and p.get("status") in ("pact_signed", "closed_cash")
        )
        inv_pacts = sum(
            float(p.get("amountUsd", 0))
            for p in pacts
            if p.get("kind") == "investor" and p.get("status") in ("pact_signed", "closed_cash")
        )
        ikpi = state.get("ikpi") or {}
        ikpi_line = f"{ikpi.get('name', 'Unset')} ({ikpi.get('current', 0)} / {ikpi.get('target', 0)})"

        highlights = args.get("highlights") or latest.get("highlights") or ["Log verified sprint highlights before sending."]
        lowlights = args.get("lowlights") or latest.get("lowlights") or ["Document top risk or missed target honestly."]
        asks = args.get("asks") or ["Warm intro to 3 ICP decision-makers", "Feedback on current pricing tier"]

        month_str = datetime.now(timezone.utc).strftime("%B %Y")
        md = "\n".join(
            [
                f"# {company} — Investor & Mentor Update ({month_str})",
                "",
                f"**Subject:** `{company} Update — {month_str} | ${mrr:,.0f} MRR | FI Stage: {state.get('stage', 'idea')}`",
                "",
                "## TL;DR",
                f"> {state.get('fiOneSentencePitch') or 'Update .startup/state.json with your linted FI One-Sentence Pitch.'}",
                "",
                "## Verified Key Metrics",
                "| Metric | Value |",
                "| :--- | :--- |",
                f"| **FI Stage** | `{state.get('stage', 'idea')}` |",
                f"| **MRR** | `${mrr:,.0f}` |",
                f"| **Gross Margin** | `{gm:.0f}%` |",
                f"| **Monthly Burn / Cash** | `${burn:,.0f}` / `${cash:,.0f}` |",
                f"| **Estimated Runway** | `{runway_str}` |",
                f"| **Customer Discovery Interviews** | `{len(interviews)} / 15 FI target` |",
                f"| **Customer PACTs Committed** | `${cust_pacts:,.0f}` |",
                f"| **Investor PACTs Soft-Circled** | `${inv_pacts:,.0f}` |",
                f"| **For-Progress iKPI** | {ikpi_line} |",
                "",
                "## Top Highlights",
                *[f"- {h}" for h in highlights],
                "",
                "## Lowlights & Risks (Mensarius Honesty)",
                *[f"- {lo}" for lo in lowlights],
                "",
                "## Specific Asks",
                *[f"- {a}" for a in asks],
                "",
            ]
        )
        out_path = ws / "docs" / "INVESTOR_UPDATE.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        return {"updatePath": str(out_path), "markdown": md}

    active = [s for s in sprints if s.get("status") == "active"]
    closed = [s for s in sprints if s.get("status") == "closed"]
    avg_score = (
        round(
            sum(float(s.get("actuals", {}).get("fiVelocityScore", 0)) for s in closed) / len(closed),
            2,
        )
        if closed
        else None
    )
    return {
        "totalSprints": len(sprints),
        "activeSprint": active[-1] if active else None,
        "avgFiVelocityScore": avg_score,
        "sprints": sprints,
    }


# ---------------------------------------------------------------------------
# MCP Tool Registry & JSON-RPC 2.0 Stdio Loop
# ---------------------------------------------------------------------------

TOOLS: list[dict[str, Any]] = [
    {
        "name": "startup_get_state",
        "description": "Read .startup/state.json plus live counts of assumptions, interviews, PACT pipeline, FI stage criteria, and pitch deck readiness score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_path": {"type": "string", "description": "Path to the startup workspace root."}
            },
        },
    },
    {
        "name": "startup_update_stage",
        "description": "Create or update .startup/state.json with FI stage, One-Sentence Pitch, MRR, burn, cash, gross margin, For-Progress Impact Thesis & iKPI.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_path": {"type": "string"},
                "companyName": {"type": "string"},
                "stage": {"type": "string", "enum": list(FI_STAGE_BENCHMARKS.keys())},
                "fiOneSentencePitch": {"type": "string"},
                "archetype": {"type": "string"},
                "mrrUsd": {"type": "number"},
                "monthlyBurnUsd": {"type": "number"},
                "cashOnHandUsd": {"type": "number"},
                "grossMarginPct": {"type": "number"},
                "targetFirstDollarDate": {"type": "string"},
                "impactThesis": {"type": "string"},
                "activeSprintGoal": {"type": "string"},
                "ikpi": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "current": {"type": "number"},
                        "target": {"type": "number"},
                        "sdg": {"type": "string"},
                    },
                },
            },
        },
    },
    {
        "name": "fi_pitch_lint",
        "description": "Lint an FI One-Sentence Madlibs Pitch (+ Secret Sauce) and/or pitch-deck/deck.json against Founder Institute buzzword, 10-word headline, bullet, and evidence rules.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pitch": {"type": "string", "description": "One-sentence pitch string to lint."},
                "workspace_path": {"type": "string"},
                "deck_path": {"type": "string"},
            },
        },
    },
    {
        "name": "assumption_manage",
        "description": "Manage Riskiest Assumptions in .startup/assumptions.json ranked by Impact x Uncertainty.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "update", "board"]},
                "workspace_path": {"type": "string"},
                "id": {"type": "string"},
                "statement": {"type": "string"},
                "category": {"type": "string"},
                "impact": {"type": "integer", "minimum": 1, "maximum": 5},
                "uncertainty": {"type": "integer", "minimum": 1, "maximum": 5},
                "status": {"type": "string", "enum": ["untested", "testing", "validated", "invalidated"]},
                "evidence": {"type": "string"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "experiment_manage",
        "description": "Create pre-committed validation experiments (with pass/fail thresholds) and record results in .startup/experiments.json.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["create", "record_result", "list"]},
                "workspace_path": {"type": "string"},
                "id": {"type": "string"},
                "assumption_id": {"type": "string"},
                "hypothesis": {"type": "string"},
                "method": {"type": "string"},
                "success_threshold": {"type": "string"},
                "deadline": {"type": "string"},
                "outcome": {"type": "string", "enum": ["validated", "invalidated", "inconclusive"]},
                "observed_result": {"type": "string"},
                "decision": {"type": "string"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "interview_manage",
        "description": "Log unbiased Mom Test customer discovery interviews and compute aggregate pain & willingness-to-pay signals.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["log", "summary"]},
                "workspace_path": {"type": "string"},
                "persona": {"type": "string"},
                "company_segment": {"type": "string"},
                "pain_severity": {"type": "integer", "minimum": 1, "maximum": 5},
                "current_workaround": {"type": "string"},
                "willingness_to_pay_usd": {"type": "number"},
                "pledged_pilot": {"type": "boolean"},
                "verbatim_quote": {"type": "string"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "pact_pipeline_manage",
        "description": "Track VC Lab PACT-style written intent commitments for both paying Customer Pilots/Pre-Orders and Investor Soft-Circles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["add", "update", "summary"]},
                "workspace_path": {"type": "string"},
                "id": {"type": "string"},
                "kind": {"type": "string", "enum": ["customer", "investor"]},
                "counterparty": {"type": "string"},
                "amount_usd": {"type": "number"},
                "target_close_date": {"type": "string"},
                "status": {"type": "string", "enum": ["prospect", "verbal", "pact_signed", "closed_cash", "lost"]},
                "probability": {"type": "number"},
                "notes": {"type": "string"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "financial_calc",
        "description": "Deterministic startup math engine: runway (Default-Alive), unit_economics (CAC/LTV/Payback), tam_bottom_up, safe_dilution, FI fast_advisor_equity, and multi-round cap_table_model.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": [
                        "runway",
                        "unit_economics",
                        "tam_bottom_up",
                        "safe_dilution",
                        "fast_advisor_equity",
                        "cap_table_model",
                    ],
                },
                "cash_usd": {"type": "number"},
                "monthly_burn_usd": {"type": "number"},
                "monthly_revenue_usd": {"type": "number"},
                "monthly_growth_pct": {"type": "number"},
                "gross_margin_pct": {"type": "number"},
                "arpa_monthly_usd": {"type": "number"},
                "monthly_churn_pct": {"type": "number"},
                "cac_usd": {"type": "number"},
                "total_buyers": {"type": "integer"},
                "annual_acv_usd": {"type": "number"},
                "sam_pct": {"type": "number"},
                "som_buyers": {"type": "integer"},
                "raise_usd": {"type": "number"},
                "valuation_cap_usd": {"type": "number"},
                "safe_type": {"type": "string", "enum": ["post_money", "pre_money"]},
                "option_pool_pct": {"type": "number"},
                "founder_count": {"type": "integer"},
                "stage": {"type": "string", "enum": ["idea", "startup", "growth"]},
                "tier": {"type": "string", "enum": ["standard", "strategic", "expert"]},
                "founders": {"type": "array", "items": {"type": "object"}},
                "advisors": {"type": "array", "items": {"type": "object"}},
                "safe_raise_usd": {"type": "number"},
                "safe_cap_usd": {"type": "number"},
                "seed_raise_usd": {"type": "number"},
                "seed_pre_money_usd": {"type": "number"},
                "seed_option_pool_pct": {"type": "number"},
            },
            "required": ["mode"],
        },
    },
    {
        "name": "pitch_deck_build",
        "description": "Lint pitch-deck/deck.json against FI standards and compile interactive 16:9 pitch-deck/index.html + Marp pitch-deck/DECK.md.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_path": {"type": "string"},
                "deck_path": {"type": "string"},
                "export_pptx": {"type": "boolean"},
            },
        },
    },
    {
        "name": "pitch_deck_design_brief",
        "description": "Export FI-linted pitch-deck/deck.json into Canva (`CANVA_DECK_BRIEF.md`), Figma Slides (`FIGMA_SLIDES_BRIEF.md` + W3C `FIGMA_TOKENS.json`), and one-shot Replit Slides (`REPLIT_SLIDES_BRIEF.md`) production handoffs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_path": {"type": "string"},
                "deck_path": {"type": "string"},
                "target": {"type": "string", "enum": ["all", "both", "canva", "figma", "replit"]},
            },
        },
    },
    {
        "name": "replit_workspace_prepare",
        "description": "Prepare a local Antigravity startup repo for zero-double-token Git sync with Replit Free/Starter tier (creates .replit, replit.md, .env.example, and docs/REPLIT_HANDOFF.md for web-node, web-python, or mobile-expo).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_path": {"type": "string"},
                "app_type": {"type": "string", "enum": ["web-node", "web-python", "mobile-expo"]},
                "company_name": {"type": "string"},
            },
        },
    },
    {
        "name": "landing_page_build",
        "description": "Generate a deploy-ready, zero-dependency 48-hour ethical smoke-test landing page (landing/index.html + landing/landing.json) with interactive ROI calculator, transparent 3-tier pricing, and Paid-Pilot PACT intake.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_path": {"type": "string"},
                "contact_email": {"type": "string"},
                "overrides": {"type": "object"},
            },
        },
    },
    {
        "name": "ikpi_catalog_search",
        "description": "Search the bundled Founder Institute For-Progress UN SDG 1-17 iKPI catalog by keyword, sector, or SDG number to pick an audit-grade impact metric.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Industry, sector, or impact keyword (e.g. 'healthcare', 'climate', 'saas', 'education')."},
                "sdg_number": {"type": "integer", "minimum": 1, "maximum": 17},
                "limit": {"type": "integer", "minimum": 1, "maximum": 20},
            },
        },
    },
    {
        "name": "sprint_manage",
        "description": "Manage FI weekly execution sprints in .startup/sprints.json (start, close, list) and compile a VC Lab / FI monthly update at docs/INVESTOR_UPDATE.md.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["start", "close", "list", "investor_update"]},
                "workspace_path": {"type": "string"},
                "id": {"type": "string"},
                "week_label": {"type": "string"},
                "primary_goal": {"type": "string"},
                "target_interviews": {"type": "integer"},
                "target_pacts": {"type": "integer"},
                "target_mrr_delta_usd": {"type": "number"},
                "interviews_completed": {"type": "integer"},
                "pacts_sent": {"type": "integer"},
                "pacts_signed": {"type": "integer"},
                "mrr_delta_usd": {"type": "number"},
                "ikpi_delta": {"type": "number"},
                "fi_velocity_score": {"type": "number"},
                "highlights": {"type": "array", "items": {"type": "string"}},
                "lowlights": {"type": "array", "items": {"type": "string"}},
                "blockers": {"type": "array", "items": {"type": "string"}},
                "asks": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["action"],
        },
    },
    {
        "name": "product_hunt_kit_build",
        "description": "Lint Product Hunt character limits (name<=40, buzzword-free tagline<=60, description<=260) and generate launch/product-hunt/PH_LAUNCH_KIT.md + launch-plan.json (Maker Comment, 1270x760 gallery storyboard, ethical outreach & launch-day checklist).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_path": {"type": "string"},
                "product_name": {"type": "string"},
                "tagline": {"type": "string"},
                "description": {"type": "string"},
                "topics": {"type": "array", "items": {"type": "string"}},
                "ph_offer": {"type": "string"},
                "launch_date": {"type": "string"},
            },
        },
    },
    {
        "name": "ai_connectors_manage",
        "description": "Optional BYO-AI connector hub for Antigravity-first founders: detect installed CLIs (claude, codex, gemini, ollama, aider) & API env vars (XAI_API_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY), sync workspace context files (CLAUDE.md, docs/GROK_CONTEXT.md, docs/AI_CONTEXT_PACK.md), or run optional multi-model second opinions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["detect", "sync_context", "second_opinion"]},
                "workspace_path": {"type": "string"},
                "targets": {"type": "array", "items": {"type": "string"}},
                "provider": {"type": "string", "enum": ["xai", "grok", "openai", "anthropic", "ollama", "claude-cli", "codex-cli", "gemini-cli"]},
                "prompt": {"type": "string"},
                "model": {"type": "string"},
                "dry_run": {"type": "boolean"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "pmf_engine_manage",
        "description": "Measure and prove Product-Market Fit in .startup/pmf.json using Sean Ellis's 40% Very Disappointed rule, Superhuman per-segment HXC discovery & 50/50 roadmap, cohort retention flattening checks, and docs/PMF_SCORECARD.md report generation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["log_survey", "record_retention", "scorecard", "generate_report"]},
                "workspace_path": {"type": "string"},
                "user_segment": {"type": "string"},
                "disappointment": {"type": "string", "enum": ["very_disappointed", "somewhat_disappointed", "not_disappointed"]},
                "main_benefit": {"type": "string"},
                "requested_improvement": {"type": "string"},
                "paying": {"type": "boolean"},
                "referred_someone": {"type": "boolean"},
                "cohort_label": {"type": "string"},
                "cohort_size": {"type": "integer"},
                "day7_pct": {"type": "number"},
                "day30_pct": {"type": "number"},
                "day90_pct": {"type": "number"},
                "net_dollar_retention_pct": {"type": "number"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "founder_resources_hub",
        "description": "Search the curated offline Founder Resources Library (36+ FI.co, VC Lab, Startup Grind, Founders Guild, PMF, Mom Test, legal/equity, accounting, Replit, Canva, Figma, Zapier, Dipity & Shelled AI resources), get a stage-matched Action Kit from .startup/state.json, browse categories, or save custom team/cohort bookmarks to .startup/custom_resources.json.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["search", "stage_kit", "categories", "save_custom"]},
                "workspace_path": {"type": "string"},
                "query": {"type": "string"},
                "category": {"type": "string"},
                "stage": {"type": "string", "enum": ["idea", "validation", "mvp", "pre_seed_traction", "seed_scale"]},
                "format": {"type": "string"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 36},
                "title": {"type": "string"},
                "url": {"type": "string"},
                "source": {"type": "string"},
                "summary": {"type": "string"},
                "key_takeaway": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "stages": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["action"],
        },
    },
    {
        "name": "founder_dashboard_build",
        "description": "Compile all live .startup/*.json telemetry (FI stage, MRR, runway, PMF 40% SVG gauge, PACT pipeline, Riskiest Assumptions, weekly sprints & For-Progress iKPI) into a single-file interactive local browser dashboard at dashboard/index.html.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_path": {"type": "string"},
            },
        },
    },
    {
        "name": "transcript_ingest",
        "description": "Parse a raw Zoom/Loom/Otter customer discovery call transcript to deterministically extract pain severity (1-5), dollar WTP mentions, current workarounds, pilot intent, verbatim quotes, and Mom Test bias warnings — optionally auto-logging directly into .startup/interviews.json.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "transcript_text": {"type": "string"},
                "persona": {"type": "string"},
                "company_segment": {"type": "string"},
                "workspace_path": {"type": "string"},
                "auto_log": {"type": "boolean"},
            },
            "required": ["transcript_text"],
        },
    },
    {
        "name": "data_room_build",
        "description": "Compile an investor-ready VC Lab / Founder Institute Data Room (data-room/index.html, DATA_ROOM_INDEX.md, Executive One-Pager, pitch deck, metrics dashboard, PII-redacted customer proof, and diligence readiness checklist) from .startup/ state.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_path": {"type": "string"},
            },
        },
    },
    {
        "name": "ai_x402_calc",
        "description": "Deterministic AI-native economics & programmable-finance engine: (1) 'ai_cogs_margin' models LLM token COGS, model routing & caching against the 75% gross margin floor; (2) 'x402_micropayment_model' compares legacy card rails vs x402 HTTP 402 USDC settlement for AI agent pay-per-call APIs and optionally exports docs/X402_AGENT_MONETIZATION_SPEC.md; (3) 'tokenization_readiness' runs an ethical 'Do You Even Need a Token?' scorecard; (4) 'x402_starter_scaffold' generates a runnable HTTP 402 pay-per-call starter (Python or Node, Base Sepolia testnet default).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": [
                        "ai_cogs_margin",
                        "x402_micropayment_model",
                        "tokenization_readiness",
                        "x402_starter_scaffold",
                    ],
                },
                "stack": {"type": "string", "enum": ["python-fastapi", "node-express"]},
                "workspace_path": {"type": "string"},
                "monthly_arpu_usd": {"type": "number"},
                "monthly_requests_per_user": {"type": "number"},
                "avg_input_tokens": {"type": "number"},
                "avg_output_tokens": {"type": "number"},
                "cache_hit_pct": {"type": "number"},
                "fast_model_share_pct": {"type": "number"},
                "price_per_call_usd": {"type": "number"},
                "monthly_paid_calls": {"type": "integer"},
                "endpoint_path": {"type": "string"},
                "network": {"type": "string"},
                "write_spec": {"type": "boolean"},
                "use_case": {"type": "string"},
                "needs_agent_micropayments": {"type": "boolean"},
                "needs_cross_border_settlement": {"type": "boolean"},
                "represents_regulated_rwa": {"type": "boolean"},
                "has_paying_fiat_customers": {"type": "boolean"},
                "plans_public_speculative_token": {"type": "boolean"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "board_review_run",
        "description": "Run a deterministic 3-lens Partner & Mentor Board Review (FI Mentor, VC Lab Partner, PMF Truth Auditor) across .startup/ telemetry & pitch-deck, scoring each 1-5 and writing docs/BOARD_REVIEW_MEMO.md with top 3 prioritized 7-day fixes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "workspace_path": {"type": "string"},
                "write_memo": {"type": "boolean"},
            },
        },
    },
    {
        "name": "competitor_manage",
        "description": "Track competitors, pricing, weaknesses, 2x2 coordinates, and your FI Secret Sauce in .startup/competitors.json and export docs/COMPETITOR_BATTLECARD.md.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "add", "remove", "export_battlecard"]},
                "workspace_path": {"type": "string"},
                "id": {"type": "string"},
                "name": {"type": "string"},
                "pricing": {"type": "string"},
                "icp": {"type": "string"},
                "strengths": {"type": "string"},
                "weaknesses": {"type": "string"},
                "our_edge": {"type": "string"},
                "x_score": {"type": "integer"},
                "y_score": {"type": "integer"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "exponential_audit",
        "description": "Deterministic Singularity & Exponential Thinking engine: (1) 'exo_scorecard' scores Massive Transformative Purpose (MTP) + SCALE + IDEAS attributes (0-100 ExO Quotient) and optionally writes docs/EXPONENTIAL_BLUEPRINT.md; (2) 'six_ds_map' maps your industry on the 6Ds of Exponentials for Why-Now pitch strategy; (3) 'accelerating_returns_sim' models 12/24/36-month gross-margin expansion under Ray Kurzweil's Law of Accelerating Returns.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["exo_scorecard", "six_ds_map", "accelerating_returns_sim"],
                },
                "workspace_path": {"type": "string"},
                "company_name": {"type": "string"},
                "mtp": {"type": "string"},
                "scale": {"type": "object"},
                "ideas": {"type": "object"},
                "write_doc": {"type": "boolean"},
                "industry": {"type": "string"},
                "current_stage": {
                    "type": "string",
                    "enum": ["digitized", "deceptive", "disruptive", "demonetized", "dematerialized", "democratized"],
                },
                "monthly_arpu_usd": {"type": "number"},
                "current_monthly_ai_cogs_usd": {"type": "number"},
                "other_monthly_cogs_usd": {"type": "number"},
                "annual_price_perf_multiplier": {"type": "number"},
            },
            "required": ["action"],
        },
    },
    {
        "name": "voice_pitch_coach",
        "description": "Analyze a spoken 3-minute FI pitch transcript for delivery pace (WPM), filler words, FI banned buzzwords, quantified proof, and clear Ask — returning a 0-100 clarity score and 5 tailored VC Lab / FI Partner grilling questions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "transcript": {"type": "string"},
                "duration_seconds": {"type": "number"},
                "target_seconds": {"type": "number"},
            },
            "required": ["transcript"],
        },
    },
    {
        "name": "war_room_run",
        "description": "Run an autonomous 4-Executive Startup War Room debate (Lean CTO, Fractional CFO, PMF Truth Auditor, Exponential Growth Strategist) on any strategic founder question using live .startup/*.json telemetry, writing docs/WAR_ROOM_DECISION_MEMO.md.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string"},
                "workspace_path": {"type": "string"},
                "write_memo": {"type": "boolean"},
            },
            "required": ["question"],
        },
    },
    {
        "name": "i18n_locale_manage",
        "description": "List all 10 supported global founder languages (en, es, zh, hi, ar RTL, pt, fr, de, ja, ko) or set the startup workspace locale in .startup/state.json.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["list", "set"]},
                "locale": {"type": "string"},
                "workspace_path": {"type": "string"},
            },
            "required": ["action"],
        },
    },
]

TOOL_HANDLERS = {
    "startup_get_state": tool_startup_get_state,
    "startup_update_stage": tool_startup_update_stage,
    "fi_pitch_lint": tool_fi_pitch_lint,
    "assumption_manage": tool_assumption_manage,
    "experiment_manage": tool_experiment_manage,
    "interview_manage": tool_interview_manage,
    "pact_pipeline_manage": tool_pact_pipeline_manage,
    "financial_calc": tool_financial_calc,
    "pitch_deck_build": tool_pitch_deck_build,
    "pitch_deck_design_brief": tool_pitch_deck_design_brief,
    "replit_workspace_prepare": tool_replit_workspace_prepare,
    "landing_page_build": tool_landing_page_build,
    "ikpi_catalog_search": tool_ikpi_catalog_search,
    "sprint_manage": tool_sprint_manage,
    "product_hunt_kit_build": tool_product_hunt_kit_build,
    "ai_connectors_manage": tool_ai_connectors_manage,
    "pmf_engine_manage": tool_pmf_engine_manage,
    "founder_resources_hub": tool_founder_resources_hub,
    "founder_dashboard_build": tool_founder_dashboard_build,
    "transcript_ingest": tool_transcript_ingest,
    "data_room_build": tool_data_room_build,
    "ai_x402_calc": tool_ai_x402_calc,
    "board_review_run": tool_board_review_run,
    "competitor_manage": tool_competitor_manage,
    "exponential_audit": tool_exponential_audit,
    "voice_pitch_coach": tool_voice_pitch_coach,
    "war_room_run": tool_war_room_run,
    "i18n_locale_manage": tool_i18n_locale_manage,
}


def handle_request(req: dict[str, Any]) -> dict[str, Any] | None:
    method = req.get("method")
    req_id = req.get("id")
    params = req.get("params") or {}

    # Notifications have no id and expect no reply
    if req_id is None:
        return None

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }

    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}

    if method == "tools/call":
        name = params.get("name")
        tool_args = params.get("arguments") or {}
        handler = TOOL_HANDLERS.get(name)
        if not handler:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Unknown tool: {name}"},
            }
        try:
            res = handler(tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(res, indent=2)}],
                    "isError": False,
                },
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps({"error": str(exc)})}],
                    "isError": True,
                },
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def main() -> None:
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            err = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"},
            }
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()
            continue

        resp = handle_request(req)
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
