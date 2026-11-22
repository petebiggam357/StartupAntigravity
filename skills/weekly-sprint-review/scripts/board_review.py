#!/usr/bin/env python3
"""Deterministic 3-Lens Partner & Mentor Board Review Simulator.

Audits `.startup/*.json` + `pitch-deck/deck.json` across three Founder Institute / VC Lab lenses:
  1. FI Mentor (Pitch Clarity, Stage Execution Velocity & For-Progress iKPI)
  2. VC Lab Partner (Fundability, Unit Economics >=75% Margin, Mensarius Ethics & Data Room)
  3. PMF Truth Auditor (Sean Ellis >=40% Very Disappointed, Paying PACT Pull & Cohort Retention)

Outputs a scored JSON report and writes `docs/BOARD_REVIEW_MEMO.md`.
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


def run_board_review(workspace: Path, write_memo: bool = True) -> dict[str, Any]:
    ws = workspace.resolve()
    sdir = ws / ".startup"
    state = _load_json(sdir / "state.json", {})
    assumptions = _load_json(sdir / "assumptions.json", [])
    interviews = _load_json(sdir / "interviews.json", [])
    pacts = _load_json(sdir / "pacts.json", [])
    pmf = _load_json(sdir / "pmf.json", {})
    sprints = _load_json(sdir / "sprints.json", [])
    competitors = _load_json(sdir / "competitors.json", [])
    deck_exists = (ws / "pitch-deck" / "index.html").exists()
    data_room_exists = (ws / "data-room" / "index.html").exists()

    company = state.get("companyName") or ws.name
    stage = state.get("stage", "idea")
    pitch = str(state.get("oneSentencePitch") or "").strip()
    metrics = state.get("metrics") or {}
    mrr = float(metrics.get("mrrUsd", state.get("mrrUsd", 0)) or 0)
    gm = float(metrics.get("grossMarginPct", 0) or 0)
    cash = float(metrics.get("cashOnHandUsd", 0) or 0)
    burn = float(metrics.get("monthlyBurnUsd", 0) or 0)
    runway = round(cash / burn, 1) if burn > 0 else None
    ikpi = state.get("ikpi") or {}

    customer_pacts = [p for p in pacts if p.get("type", "customer") == "customer"]
    paid_pacts = [p for p in customer_pacts if p.get("status") in ("signed", "paid", "closed")]
    pmf_responses = pmf.get("responses") or []
    very_dis = sum(1 for r in pmf_responses if r.get("disappointment") == "very_disappointed")
    sean_ellis_pct = round((very_dis / len(pmf_responses)) * 100.0, 1) if pmf_responses else None

    # --- Lens 1: FI Mentor (Clarity, Velocity & iKPI) ---
    fi_score = 1.5
    fi_notes: list[str] = []
    actions: list[str] = []
    if pitch:
        fi_score += 1.0
        fi_notes.append("[PASS] FI One-Sentence Pitch is defined.")
    else:
        fi_notes.append("[GAP] Missing FI One-Sentence Pitch in .startup/state.json.")
        actions.append("Craft & lint your FI One-Sentence Madlibs Pitch via `fi_pitch_lint`.")

    if deck_exists:
        fi_score += 0.8
        fi_notes.append("[PASS] Interactive pitch deck compiled at `pitch-deck/index.html`.")
    else:
        fi_notes.append("[GAP] Pitch deck not compiled yet.")
        actions.append("Build your interactive FI Pitch Deck via `pitch_deck_build`.")

    if ikpi.get("metric") or ikpi.get("name"):
        fi_score += 0.7
        fi_notes.append("[PASS] For-Progress iKPI tracked alongside revenue.")
    else:
        fi_notes.append("[GAP] No For-Progress iKPI defined.")
        actions.append("Pick an UN SDG iKPI via `ikpi_catalog_search` and save it to `.startup/state.json`.")

    if len(sprints) >= 1:
        fi_score += 1.0
        fi_notes.append(f"[PASS] Weekly execution cadence active ({len(sprints)} sprints logged).")
    else:
        fi_notes.append("[GAP] No weekly sprints logged yet.")
        actions.append("Start Sprint #1 via `sprint_manage` and score weekly velocity.")

    fi_score = min(5.0, round(fi_score, 1))

    # --- Lens 2: VC Lab Partner (Fundability, Margin & Governance) ---
    vc_score = 1.5
    vc_notes: list[str] = []
    if gm >= 75.0:
        vc_score += 1.2
        vc_notes.append(f"[PASS] Gross margin ({gm:.0f}%) clears the >=75% software/AI margin floor.")
    else:
        vc_notes.append(f"[GAP] Gross margin ({gm:.0f}%) is below 75% or unverified.")
        actions.append("Audit COGS & pricing via `financial_calc` / `ai_x402_calc` to push gross margin >=75%.")

    if runway is None or runway >= 12.0:
        vc_score += 0.8
        vc_notes.append("[PASS] Healthy runway / Default-Alive discipline.")
    else:
        vc_notes.append(f"[WARN] Runway is {runway} months — tighten burn or accelerate Customer PACTs.")
        actions.append("Cut non-essential burn and close 2–3 Paid-Pilot PACTs before fundraising.")

    if data_room_exists:
        vc_score += 0.8
        vc_notes.append("[PASS] Investor Data Room compiled at `data-room/index.html`.")
    else:
        vc_notes.append("[GAP] Investor Data Room not compiled yet.")
        actions.append("Compile `data-room/index.html` via `data_room_build`.")

    if len(competitors) >= 2:
        vc_score += 0.7
        vc_notes.append(f"[PASS] Competitive landscape mapped ({len(competitors)} competitors tracked).")
    else:
        vc_notes.append("[GAP] Fewer than 2 competitors logged in `.startup/competitors.json`.")
        actions.append("Map top 3 competitors & your Secret Sauce via `competitor_manage`.")

    vc_score = min(5.0, round(vc_score, 1))

    # --- Lens 3: PMF Truth Auditor (Real Paying Demand) ---
    pmf_score = 1.0
    pmf_notes: list[str] = []
    if len(interviews) >= 3:
        pmf_score += 1.0
        pmf_notes.append(f"[PASS] {len(interviews)} Mom Test discovery interviews logged.")
    else:
        pmf_notes.append(f"[GAP] Only {len(interviews)} customer interviews logged (need >=3 minimum, 15+ target).")
        actions.append("Run 5 unbiased Mom Test interviews this week and ingest notes via `transcript_ingest`.")

    if len(paid_pacts) >= 1 or mrr > 0:
        pmf_score += 1.5
        pmf_notes.append(f"[PASS] Real financial pull verified (MRR=${mrr:,.0f}, {len(paid_pacts)} signed/paid Customer PACTs).")
    else:
        pmf_notes.append("[GAP] Zero paying customers or signed Paid-Pilot PACTs yet.")
        actions.append("Close your first paying Customer Pilot PACT within 7–14 days before writing heavy code.")

    if sean_ellis_pct is not None and sean_ellis_pct >= 40.0:
        pmf_score += 1.5
        pmf_notes.append(f"[PASS] Sean Ellis score ({sean_ellis_pct}%) clears the >=40% PMF threshold.")
    elif sean_ellis_pct is not None:
        pmf_score += 0.6
        pmf_notes.append(f"[WARN] Sean Ellis score is {sean_ellis_pct}% (<40%). Narrow ICP to your HXC segment before scaling.")
        actions.append("Segment PMF survey responses in `pmf_engine_manage` to isolate your High-Expectation Customer.")
    else:
        pmf_notes.append("[GAP] Sean Ellis PMF survey not yet logged.")
        actions.append("Log early user responses in `pmf_engine_manage` to measure real PMF.")

    pmf_score = min(5.0, round(pmf_score, 1))
    overall = round((fi_score + vc_score + pmf_score) / 3.0, 2)

    if overall >= 4.2:
        verdict = "READY_TO_ACCELERATE"
    elif overall >= 3.0:
        verdict = "PROMISING_CLOSE_GAPS_FIRST"
    else:
        verdict = "EARLY_VALIDATE_BEFORE_SCALING"

    top_3 = actions[:3] if actions else ["Maintain weekly sprint cadence and publish your Monthly Investor Update."]
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    memo_path: str | None = None
    if write_memo:
        docs_dir = ws / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        memo_file = docs_dir / "BOARD_REVIEW_MEMO.md"
        memo_lines = [
            f"# {company} — Partner & Mentor Board Review Memo",
            "",
            f"> Generated by Startup Antigravity (`board_review_run`) • {now_iso}",
            f"> **Stage:** `{stage}` • **Overall Readiness:** **{overall} / 5.0** • **Verdict:** `{verdict}`",
            "",
            "## Scorecard Summary",
            "| Advisory Lens | Score (1–5) | Key Signal |",
            "| :--- | :--- | :--- |",
            f"| **FI Mentor** (Clarity, Velocity & iKPI) | **{fi_score}** | {fi_notes[0]} |",
            f"| **VC Lab Partner** (Fundability & Margin) | **{vc_score}** | {vc_notes[0]} |",
            f"| **PMF Truth Auditor** (Paying Demand) | **{pmf_score}** | {pmf_notes[0]} |",
            "",
            "## Top 3 Prioritized 7-Day Actions",
            *[f"{i}. {a}" for i, a in enumerate(top_3, 1)],
            "",
            "## Detailed Audit Notes",
            "### 1. FI Mentor Notes",
            *[f"- {n}" for n in fi_notes],
            "",
            "### 2. VC Lab Partner Notes",
            *[f"- {n}" for n in vc_notes],
            "",
            "### 3. PMF Truth Auditor Notes",
            *[f"- {n}" for n in pmf_notes],
        ]
        memo_file.write_text("\n".join(memo_lines) + "\n", encoding="utf-8")
        memo_path = str(memo_file)

    return {
        "ok": True,
        "company": company,
        "stage": stage,
        "overallScore": overall,
        "verdict": verdict,
        "scores": {
            "fiMentor": fi_score,
            "vcLabPartner": vc_score,
            "pmfTruthAuditor": pmf_score,
        },
        "topActions": top_3,
        "memoPath": memo_path,
        "counts": {
            "assumptions": len(assumptions),
            "interviews": len(interviews),
            "paidCustomerPacts": len(paid_pacts),
            "competitors": len(competitors),
        },
    }
