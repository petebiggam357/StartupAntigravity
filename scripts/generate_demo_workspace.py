#!/usr/bin/env python3
"""Generate a complete, realistic demo startup workspace (SolarLedger) to preview
Startup Antigravity end-to-end:
  - .startup/state.json, assumptions.json, interviews.json, pacts.json, pmf.json, sprints.json
  - dashboard/index.html      (Live Founder Command Center)
  - pitch-deck/index.html     (Interactive 16:9 FI Pitch Deck)
  - landing/index.html        (48-Hour Smoke-Test Landing Page)
  - data-room/index.html      (Investor Data Room Portal)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
for _sub in (
    ROOT / "skills" / "pitch-deck-builder" / "scripts",
    ROOT / "skills" / "revenue-first-validation" / "scripts",
    ROOT / "skills" / "unit-economics-and-profit-os" / "scripts",
    ROOT / "skills" / "vc-lab-fundraising-os" / "scripts",
):
    if str(_sub) not in sys.path:
        sys.path.insert(0, str(_sub))

from build_dashboard import build_dashboard  # noqa: E402
from build_data_room import build_data_room  # noqa: E402
from build_deck import build_deck  # noqa: E402
from build_landing_page import build_landing_page  # noqa: E402


def generate_demo_workspace(target_dir: Path) -> dict[str, Any]:
    ws = target_dir.resolve()
    startup = ws / ".startup"
    docs = ws / "docs"
    pitch_dir = ws / "pitch-deck"
    for d in (startup, docs, pitch_dir):
        d.mkdir(parents=True, exist_ok=True)

    state = {
        "companyName": "SolarLedger",
        "stage": "mvp",
        "oneSentencePitch": (
            "My company, SolarLedger, is developing automated O&M invoice and REC reconciliation software "
            "to help regional commercial solar EPCs eliminate 18 hours per week of manual billing leakage "
            "with direct inverter-telemetry-to-QuickBooks matching."
        ),
        "secretSauce": "Direct API reconciliation between commercial inverter telemetry, utility tariffs, and QuickBooks Online with 99.4% invoice accuracy.",
        "metrics": {
            "mrrUsd": 6400,
            "grossMarginPct": 84,
            "cashOnHandUsd": 145000,
            "monthlyBurnUsd": 11200,
            "payingCustomers": 8,
            "activePilots": 4,
        },
        "ikpi": {
            "sdg": "SDG 7 — Affordable and Clean Energy",
            "metric": "Megawatt-hours of commercial solar uptime verified without billing disputes",
            "current": 1420,
            "target": 10000,
        },
    }
    (startup / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

    assumptions = [
        {
            "id": "A-01",
            "statement": "Regional solar EPCs lose >$2,500/mo in unbilled O&M and REC reconciliation errors.",
            "riskLevel": "high",
            "status": "validated",
            "evidence": "9 of 12 Mom Test interviews cited $3K-$8K/mo leakage across 40+ commercial sites.",
        },
        {
            "id": "A-02",
            "statement": "Operations managers will sign a $800/mo Paid-Pilot PACT before full ERP integration.",
            "riskLevel": "high",
            "status": "validated",
            "evidence": "8 paying accounts ($6,400 MRR) live on CSV + QuickBooks sync.",
        },
        {
            "id": "A-03",
            "statement": "Automated SolarEdge + Enphase telemetry pulls cut onboarding time under 45 minutes.",
            "riskLevel": "medium",
            "status": "testing",
            "evidence": "Pilot cohort #2 averaging 52 minutes; automating token refresh.",
        },
        {
            "id": "A-04",
            "statement": "Regional EPC associations will co-market SolarLedger for 15% rev-share.",
            "riskLevel": "medium",
            "status": "untested",
            "evidence": "[HYPOTHESIS] Two partner calls scheduled next sprint.",
        },
    ]
    (startup / "assumptions.json").write_text(json.dumps(assumptions, indent=2), encoding="utf-8")

    interviews = [
        {
            "id": "INT-01",
            "persona": "Director of O&M, Mid-Atlantic Solar EPC (65 sites)",
            "painSeverity": 5,
            "willingnessToPayUsd": 950,
            "workaround": "Two ops analysts reconciling Excel exports against QuickBooks every Friday.",
            "pilotIntent": True,
            "quote": "We found $14,000 in missed inverter warranty credits last quarter alone.",
        },
        {
            "id": "INT-02",
            "persona": "CFO, California Commercial Solar Installer (42 sites)",
            "painSeverity": 4,
            "willingnessToPayUsd": 800,
            "workaround": "Monthly manual audit by external bookkeeper costing $2,200/mo.",
            "pilotIntent": True,
            "quote": "If it pushes clean line items into QuickBooks Online, I will pay tomorrow.",
        },
        {
            "id": "INT-03",
            "persona": "Asset Manager, Community Solar Portfolio (110 sites)",
            "painSeverity": 5,
            "willingnessToPayUsd": 1200,
            "workaround": "Custom fragile Airtable scripts breaking on utility tariff updates.",
            "pilotIntent": True,
            "quote": "Our investors ask for monthly yield-to-cash proof and it takes 4 days to assemble.",
        },
    ]
    (startup / "interviews.json").write_text(json.dumps(interviews, indent=2), encoding="utf-8")

    pacts = [
        {"id": "PACT-C1", "type": "customer", "company": "SunCrest Commercial EPC", "segment": "Regional EPC (50+ sites)", "status": "paid", "amountUsd": 2400},
        {"id": "PACT-C2", "type": "customer", "company": "Pacific Grid O&M", "segment": "Regional EPC (40+ sites)", "status": "signed", "amountUsd": 2400},
        {"id": "PACT-C3", "type": "customer", "company": "Keystone Solar Assets", "segment": "Community Solar Portfolio", "status": "signed", "amountUsd": 3600},
        {"id": "PACT-I1", "type": "investor", "company": "CleanGrid Angels", "segment": "Climate Pre-Seed Syndicate", "status": "soft_circled", "amountUsd": 75000},
        {"id": "PACT-I2", "type": "investor", "company": "Sierra Impact Ventures", "segment": "Pre-Seed Fund", "status": "soft_circled", "amountUsd": 150000},
    ]
    (startup / "pacts.json").write_text(json.dumps(pacts, indent=2), encoding="utf-8")

    pmf = {
        "responses": [
            *[{"segment": "Regional EPC (40+ sites)", "disappointment": "very_disappointed", "mainBenefit": "Eliminates Friday billing audits"} for _ in range(8)],
            *[{"segment": "Regional EPC (40+ sites)", "disappointment": "somewhat_disappointed", "mainBenefit": "Helpful QuickBooks export"} for _ in range(4)],
            *[{"segment": "Small Residential Installer", "disappointment": "somewhat_disappointed", "mainBenefit": "Nice dashboard"} for _ in range(3)],
            *[{"segment": "Small Residential Installer", "disappointment": "not_disappointed", "mainBenefit": "Too complex for 5 sites"} for _ in range(3)],
        ],
        "cohorts": [
            {"cohort": "2026-08", "m1": 100, "m2": 88, "m3": 80, "m4": 78},
            {"cohort": "2026-09", "m1": 100, "m2": 90, "m3": 82, "m4": 80},
        ],
    }
    (startup / "pmf.json").write_text(json.dumps(pmf, indent=2), encoding="utf-8")

    sprints = [
        {
            "id": "SPR-01",
            "goal": "Close 3 Paid-Pilot PACTs and ship automated QuickBooks Online invoice sync",
            "status": "completed",
            "fiVelocityScore": 4.4,
            "completedTasks": 6,
            "totalTasks": 7,
        },
        {
            "id": "SPR-02",
            "goal": "Onboard 4 signed EPC pilots and push MRR from $6.4K to $10K",
            "status": "active",
            "fiVelocityScore": 4.2,
            "completedTasks": 4,
            "totalTasks": 6,
        },
    ]
    (startup / "sprints.json").write_text(json.dumps(sprints, indent=2), encoding="utf-8")

    (docs / "INVESTOR_UPDATE.md").write_text(
        "# SolarLedger — Monthly Investor Update\n\n"
        "- **MRR:** $6,400 (+32% MoM) `[VALIDATED]`\n"
        "- **Gross Margin:** 84% `[VALIDATED]`\n"
        "- **Sean Ellis PMF:** 44.4% Very Disappointed overall (66.7% in Regional EPC HXC segment) `[VALIDATED]`\n"
        "- **Top Ask:** Intros to commercial solar EPC operations directors managing 30–150 sites.\n",
        encoding="utf-8",
    )

    deck_json = {
        "meta": {
            "companyName": "SolarLedger",
            "tagline": "Automated O&M Billing & REC Reconciliation for Commercial Solar EPCs",
            "theme": "emerald-slate",
            "mode": "traction",
        },
        "slides": [
            {
                "type": "title",
                "headline": "SolarLedger: Zero-Leakage Commercial Solar Billing",
                "subtitle": "Direct inverter-telemetry-to-QuickBooks reconciliation for regional EPCs",
                "badge": "VALIDATED",
            },
            {
                "type": "problem",
                "headline": "Regional solar EPCs lose $4K/mo to manual billing errors",
                "bullets": [
                    "Ops teams spend 18 hours/week matching inverter logs to spreadsheets [VALIDATED]",
                    "Missed warranty claims and REC discrepancies leak 6-9% of O&M margin [VALIDATED]",
                    "External bookkeepers take 4 days/month to close site-level P&L [VALIDATED]",
                ],
            },
            {
                "type": "solution",
                "headline": "Direct telemetry-to-QuickBooks matching cuts close time 90%",
                "bullets": [
                    "Automated SolarEdge & Enphase telemetry pulls replace manual spreadsheets [VALIDATED]",
                    "Real-time anomaly alerts capture missed warranty & REC credits automatically [VALIDATED]",
                    "1-click QuickBooks Online sync closes site-level books in 15 minutes [VALIDATED]",
                ],
            },
            {
                "type": "traction",
                "headline": "$6.4K MRR across 8 paying EPCs with 84% gross margin",
                "bullets": [
                    "8 paying regional EPCs ($800/mo ACV) + 4 signed Paid-Pilot PACTs [VALIDATED]",
                    "66.7% Sean Ellis Very Disappointed score in Regional EPC HXC segment [VALIDATED]",
                    "1,420 MWh of commercial solar uptime verified (UN SDG 7 iKPI) [VALIDATED]",
                ],
            },
            {
                "type": "ask",
                "headline": "Raising $500K Pre-Seed to reach $30K MRR in 12 months",
                "bullets": [
                    "$225K soft-circled via VC Lab PACTs from climate angels & pre-seed funds [VALIDATED]",
                    "Funds direct utility tariff integrations and 35 new regional EPC accounts [TARGET]",
                    "Default-Alive trajectory at 22 paying EPCs with >80% gross margin [HYPOTHESIS]",
                ],
            },
        ],
    }
    deck_path = pitch_dir / "deck.json"
    deck_path.write_text(json.dumps(deck_json, indent=2), encoding="utf-8")

    # Compile all 4 live visual outputs
    deck_res = build_deck(deck_path)
    dash_res = build_dashboard(ws)
    landing_res = build_landing_page(ws)
    dr_res = build_data_room(ws)

    return {
        "ok": True,
        "workspace": str(ws),
        "dashboardHtml": dash_res.get("htmlPath") or str(ws / "dashboard" / "index.html"),
        "pitchDeckHtml": deck_res.get("htmlPath") or str(ws / "pitch-deck" / "index.html"),
        "landingHtml": landing_res.get("htmlPath") or str(ws / "landing" / "index.html"),
        "dataRoomHtml": dr_res["portalHtml"],
        "dataRoomReadinessPct": dr_res["readinessPct"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a realistic SolarLedger demo workspace.")
    parser.add_argument(
        "--output",
        default=str(Path.home() / ".cache" / "startup-antigravity-demo"),
        help="Destination directory for the sample startup workspace",
    )
    args = parser.parse_args(argv)
    res = generate_demo_workspace(Path(args.output))
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
