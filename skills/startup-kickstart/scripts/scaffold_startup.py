#!/usr/bin/env python3
"""
Startup Antigravity — Day-0 Company Workspace Scaffolder.

Creates `.startup/`, `docs/`, and `pitch-deck/` initialized with the founder's
FI One-Sentence Pitch, For-Progress Impact Thesis, Mensarius Ethical Charter,
Mom Test Discovery Script, 7-Day MVP Spec, and compiled interactive Pitch Deck.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DECK_SCRIPTS = PLUGIN_ROOT / "skills" / "pitch-deck-builder" / "scripts"
DECK_RESOURCES = PLUGIN_ROOT / "skills" / "pitch-deck-builder" / "resources"

if str(DECK_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(DECK_SCRIPTS))

from build_deck import build_deck, lint_one_sentence_pitch  # noqa: E402


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def scaffold_workspace(
    workspace: str | Path,
    company: str,
    offering: str,
    audience: str,
    problem: str,
    secret_sauce: str,
    impact_thesis: str,
    ikpi: str,
    archetype: str = "b2b-saas",
    deck_mode: str = "problem-solution",
    founder_name: str = "Founder, CEO",
    founder_email: str = "founder@company.com",
    website: str = "https://company.com",
) -> dict:
    ws = Path(workspace).expanduser().resolve()
    ws.mkdir(parents=True, exist_ok=True)
    sdir = ws / ".startup"
    docs = ws / "docs"
    pdir = ws / "pitch-deck"
    for d in (sdir, docs, pdir):
        d.mkdir(parents=True, exist_ok=True)

    fi_pitch = (
        f"My company, {company}, is developing {offering} to help "
        f"{audience} {problem} with {secret_sauce}."
    )
    pitch_lint = lint_one_sentence_pitch(fi_pitch)
    target_date = (datetime.now(timezone.utc) + timedelta(days=14)).strftime("%Y-%m-%d")

    state = {
        "companyName": company,
        "archetype": archetype,
        "stage": "idea",
        "fiOneSentencePitch": fi_pitch,
        "offering": offering,
        "audience": audience,
        "problem": problem,
        "secretSauce": secret_sauce,
        "mrrUsd": 0,
        "monthlyBurnUsd": 0,
        "cashOnHandUsd": 0,
        "grossMarginPct": 80,
        "targetFirstDollarDate": target_date,
        "impactThesis": impact_thesis,
        "ikpi": {
            "name": ikpi,
            "current": 0,
            "target": 100,
            "sdg": "Select matching UN SDG (1–17)",
        },
        "activeSprintGoal": f"Log 15 discovery interviews with {audience} and close first paid pilot PACT by {target_date}.",
        "createdAt": _now_iso(),
        "updatedAt": _now_iso(),
    }
    (sdir / "state.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    # Seed the 4 Riskiest Assumptions
    assumptions = [
        {
            "id": "A-001",
            "statement": f"{audience} experience '{problem}' frequently enough to actively seek a fix.",
            "category": "desirability",
            "impact": 5,
            "uncertainty": 5,
            "riskScore": 25,
            "status": "untested",
            "evidence": "",
            "createdAt": _now_iso(),
        },
        {
            "id": "A-002",
            "statement": f"{audience} will sign a paid pilot or pre-order PACT before full product build.",
            "category": "viability",
            "impact": 5,
            "uncertainty": 5,
            "riskScore": 25,
            "status": "untested",
            "evidence": "",
            "createdAt": _now_iso(),
        },
        {
            "id": "A-003",
            "statement": f"We can reach 50 qualified {audience} buyers per week at low CAC without paid ads.",
            "category": "distribution",
            "impact": 4,
            "uncertainty": 4,
            "riskScore": 16,
            "status": "untested",
            "evidence": "",
            "createdAt": _now_iso(),
        },
        {
            "id": "A-004",
            "statement": f"We can deliver {offering} with {secret_sauce} at >75% gross margin.",
            "category": "feasibility",
            "impact": 4,
            "uncertainty": 3,
            "riskScore": 12,
            "status": "untested",
            "evidence": "",
            "createdAt": _now_iso(),
        },
    ]
    (sdir / "assumptions.json").write_text(json.dumps(assumptions, indent=2) + "\n", encoding="utf-8")
    for empty_name in ("experiments.json", "interviews.json", "pacts.json"):
        p = sdir / empty_name
        if not p.exists():
            p.write_text("[]\n", encoding="utf-8")

    # 1. ONE_PAGER.md
    (docs / "ONE_PAGER.md").write_text(
        f"""# {company} — Lean One-Pager & 14-Day First-Dollar Plan

## FI One-Sentence Pitch
> {fi_pitch}

- **Archetype:** `{archetype}`
- **Current FI Stage:** `idea`
- **Target First-Dollar Date:** `{target_date}`

## Lean Canvas Snapshot
| Block | Current Definition | Evidence Status |
| :--- | :--- | :--- |
| **Target Customer (ICP)** | {audience} | `[HYPOTHESIS]` |
| **Core Problem** | {problem} | `[HYPOTHESIS]` |
| **Offering** | {offering} | `[HYPOTHESIS]` |
| **Secret Sauce / Moat** | {secret_sauce} | `[HYPOTHESIS]` |
| **Revenue Model** | Value-based subscription + Paid Pilot PACT | `[TARGET]` |
| **Gross Margin Target** | >= 75% | `[TARGET]` |
| **For-Progress iKPI** | {ikpi} | `[TARGET]` |

## 14-Day First-Dollar Sprint
1. **Days 1–4:** Conduct 10–15 unbiased Customer Discovery interviews with `{audience}` (log via `interview_manage`).
2. **Days 5–8:** Present a 1-page Paid Pilot / Pre-Order **Customer PACT** to the top 5 highest-pain prospects.
3. **Days 9–14:** Close the first paying customer or paid deposit before building non-essential infrastructure.
""",
        encoding="utf-8",
    )

    # 2. ETHICS_AND_IKPI.md
    (docs / "ETHICS_AND_IKPI.md").write_text(
        f"""# {company} — Mensarius Ethical Charter & For-Progress iKPIs

Inspired by **VC Lab's Mensarius Oath** (`govclab.com`) and **Founder Institute's For-Progress Framework** (`fi.co`).

## Impact Thesis
> {impact_thesis}

## Primary Impact KPI (iKPI)
- **Metric:** {ikpi}
- **Current Baseline:** `0` `[HYPOTHESIS]`
- **12-Month Target:** Define alongside $25K MRR milestone `[TARGET]`
- **UN SDG Alignment:** Map to primary UN Sustainable Development Goal (1–17)

## Mensarius Founder Operating Code
1. **Radical Metric Honesty:** Never fabricate traction, market size, or customer quotes. Tag every claim `[VALIDATED]` or `[HYPOTHESIS]`.
2. **Zero Dark Patterns:** Profit must come from 10x customer value — no deceptive billing, hidden cancellations, fake scarcity, or unauthorized data monetization.
3. **Fair Stakeholder Alignment:** Use clear written terms with co-founders, FI **FAST Agreement** standards for advisors, and transparent pricing for buyers.
4. **Ethical Profit = Independence:** High margins and Default-Alive discipline protect our mission and prevent desperate compromises.
""",
        encoding="utf-8",
    )

    # 3. DISCOVERY_SCRIPT.md
    (docs / "DISCOVERY_SCRIPT.md").write_text(
        f"""# {company} — Mom Test Customer Discovery Script

**Target Buyer (ICP):** {audience}
**FI Validation Goal:** Complete 15+ unbiased interviews and log each via `interview_manage`.

## Rules Before Calling
- **Do NOT pitch your idea** during the first 15 minutes.
- Ask about **past behavior and actual money/time spent**, never hypothetical future promises ("Would you use...?").

## Core Questions
1. *"Walk me through the last time you dealt with {problem}. What actually happened?"*
2. *"What was the hardest or most expensive part of that process?"*
3. *"What are you using right now to handle it — spreadsheets, agencies, another tool? How much does that cost you in hours or dollars?"*
4. *"Have you already tried buying or building a fix? Why didn't it stick?"*
5. *"If that exact pain disappeared next week, what measurable financial impact would it have on your team?"*

## Transition to Paid Pilot PACT (Only If Pain Severity >= 4/5)
> *"We're building {offering} specifically for {audience}. We're onboarding 3 founding design partners this month at an early-partner rate with a 100% value guarantee. If we solve this in 14 days, would you sign a 1-page pilot PACT to kick off next week?"*
""",
        encoding="utf-8",
    )

    # 4. MVP_SPEC.md
    (docs / "MVP_SPEC.md").write_text(
        f"""# {company} — 7-Day Vertical Slice MVP Spec

## Core Hypothesis Being Tested
Delivering **{offering}** using **{secret_sauce}** creates immediate ROI for **{audience}** solving **{problem}**.

## In Scope (Ship in <= 7 Days)
- [ ] Single core workflow that produces the customer's #1 measurable output
- [ ] Simple onboarding (manual concierge onboarding is allowed for customers #1–#10!)
- [ ] Direct payment link / invoice / Customer PACT capture

## Explicit "NOT Building Yet" Cut-List
- ❌ Microservices, Kubernetes, Terraform, or multi-region clusters
- ❌ Custom enterprise RBAC, SSO, or complex multi-tenant admin portals
- ❌ Custom billing engines (use Stripe Checkout / simple invoicing)
- ❌ Dark-mode toggles, public blogs, or settings pages before 10 paying customers

## Gross Margin Guardrail
- Target Gross Margin: **>= 75%**
- Estimated Variable COGS per Customer / Month: `$[TBD]` `[HYPOTHESIS]`
""",
        encoding="utf-8",
    )

    # 5. Pitch Deck from template
    tpl_file = (
        DECK_RESOURCES / "deck.traction.json"
        if deck_mode == "traction"
        else DECK_RESOURCES / "deck.problem-solution.json"
    )
    deck = json.loads(tpl_file.read_text(encoding="utf-8"))
    deck["meta"]["companyName"] = company
    deck["meta"]["website"] = website
    deck["meta"]["contactName"] = founder_name
    deck["meta"]["contactEmail"] = founder_email
    deck["meta"]["fiOneSentencePitch"] = fi_pitch
    deck["meta"]["impactThesis"] = impact_thesis

    if deck.get("slides"):
        cover = deck["slides"][0]
        cover["headline"] = f"{company}: {offering[:55].strip().title()}"
        cover["subheadline"] = fi_pitch
        cover["footer"] = f"{founder_name} • {founder_email} • {website}"
        for s in deck["slides"]:
            if s.get("id") == "ask":
                s["impactMetric"] = f"For-Progress iKPI: {ikpi} [TARGET]"

    deck_json_path = pdir / "deck.json"
    deck_json_path.write_text(json.dumps(deck, indent=2) + "\n", encoding="utf-8")
    deck_build = build_deck(deck_json_path)

    return {
        "workspace": str(ws),
        "companyName": company,
        "fiOneSentencePitch": fi_pitch,
        "pitchLint": pitch_lint,
        "filesCreated": [
            str(sdir / "state.json"),
            str(sdir / "assumptions.json"),
            str(docs / "ONE_PAGER.md"),
            str(docs / "ETHICS_AND_IKPI.md"),
            str(docs / "DISCOVERY_SCRIPT.md"),
            str(docs / "MVP_SPEC.md"),
            deck_build["source"],
            deck_build["htmlPath"],
            deck_build["markdownPath"],
        ],
        "deckReadinessScore": deck_build["lint"]["readinessScore"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a Startup Antigravity workspace.")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--company", required=True)
    parser.add_argument("--offering", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--problem", required=True)
    parser.add_argument("--secret-sauce", required=True)
    parser.add_argument("--impact-thesis", required=True)
    parser.add_argument("--ikpi", required=True)
    parser.add_argument("--archetype", default="b2b-saas")
    parser.add_argument("--deck-mode", default="problem-solution", choices=["problem-solution", "traction"])
    parser.add_argument("--founder-name", default="Founder, CEO")
    parser.add_argument("--founder-email", default="founder@company.com")
    parser.add_argument("--website", default="https://company.com")
    args = parser.parse_args()

    res = scaffold_workspace(
        workspace=args.workspace,
        company=args.company,
        offering=args.offering,
        audience=args.audience,
        problem=args.problem,
        secret_sauce=args.secret_sauce,
        impact_thesis=args.impact_thesis,
        ikpi=args.ikpi,
        archetype=args.archetype,
        deck_mode=args.deck_mode,
        founder_name=args.founder_name,
        founder_email=args.founder_email,
        website=args.website,
    )
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
