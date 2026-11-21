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
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
DECK_SCRIPTS_DIR = PLUGIN_ROOT / "skills" / "pitch-deck-builder" / "scripts"
if str(DECK_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(DECK_SCRIPTS_DIR))

from build_deck import build_deck, lint_deck, lint_one_sentence_pitch  # noqa: E402

SERVER_NAME = "startup-antigravity-os"
SERVER_VERSION = "1.0.0"
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

    raise ValueError(
        "Invalid mode. Use one of: runway, unit_economics, tam_bottom_up, safe_dilution, fast_advisor_equity."
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
        "description": "Deterministic startup math engine: runway (Default-Alive), unit_economics (CAC/LTV/Payback), tam_bottom_up, safe_dilution, and FI fast_advisor_equity.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["runway", "unit_economics", "tam_bottom_up", "safe_dilution", "fast_advisor_equity"],
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
