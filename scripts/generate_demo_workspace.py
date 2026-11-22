#!/usr/bin/env python3
"""Generate a realistic, researched demo startup workspace (ClaimPulse) to preview
Startup Antigravity end-to-end:
  - .startup/state.json, assumptions.json, interviews.json, pacts.json, pmf.json, sprints.json, competitors.json
  - dashboard/index.html      (Startup Command Center)
  - pitch-deck/index.html     (13-Slide Visual Interactive FI Pitch Deck with SVG charts & 2x2 quadrant)
  - landing/index.html        (48-Hour Smoke-Test Landing Page)
  - data-room/index.html      (Investor Data Room Portal — 100% diligence ready)
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
from build_deck import build_deck, lint_deck  # noqa: E402
from build_landing_page import build_landing_page  # noqa: E402


def generate_demo_workspace(target_dir: Path) -> dict[str, Any]:
    ws = target_dir.resolve()
    startup = ws / ".startup"
    docs = ws / "docs"
    pitch_dir = ws / "pitch-deck"
    for d in (startup, docs, pitch_dir):
        d.mkdir(parents=True, exist_ok=True)

    fi_pitch = (
        "My company, ClaimPulse, is developing automated pre-submission claim scrubbing software "
        "to help independent multi-chair dental practices cut insurance denials below 3% "
        "with payer-specific CDT rule checks and clinical appeal narratives."
    )

    state = {
        "companyName": "ClaimPulse",
        "stage": "pre_seed_traction",
        "oneSentencePitch": fi_pitch,
        "secretSauce": "Payer-specific CDT code & radiograph rule graph built on 140K adjudicated dental claims, syncing directly with OpenDental, Dentrix, and QuickBooks Online.",
        "metrics": {
            "mrrUsd": 14400,
            "grossMarginPct": 84,
            "cashOnHandUsd": 215000,
            "monthlyBurnUsd": 14800,
            "payingCustomers": 16,
            "activePilots": 5,
        },
        "ikpi": {
            "sdg": "SDG 3 — Good Health and Well-Being",
            "metric": "Verified clinical revenue recovered for independent family dental practices ($K)",
            "current": 485,
            "target": 5000,
        },
    }
    (startup / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

    assumptions = [
        {
            "id": "A-01",
            "statement": "Independent 3-8 chair dental practices lose $42K-$68K/yr to 10-15% claim denials and unworked rejections.",
            "riskLevel": "high",
            "status": "validated",
            "evidence": "ADA HPI / RCM benchmarks + 19 of 24 Mom Test clinic audits confirmed 11-16% initial denial rates.",
        },
        {
            "id": "A-02",
            "statement": "Practice owners will sign a $900/mo flat-fee Paid-Pilot PACT over legacy 6-8% RCM collection fees.",
            "riskLevel": "high",
            "status": "validated",
            "evidence": "16 paying clinics ($14,400 MRR) converted from free 90-day denial leakage audits.",
        },
        {
            "id": "A-03",
            "statement": "Tiered LLM routing (85% fast model + prompt caching) keeps inference COGS under $0.04/claim (>82% margin).",
            "riskLevel": "medium",
            "status": "validated",
            "evidence": "Production audit across 28,400 scrubbed claims averaged $0.031/claim (84% gross margin).",
        },
        {
            "id": "A-04",
            "statement": "Dental CPA & fractional CFO partner channel can deliver 8+ warm clinic intros per month.",
            "riskLevel": "medium",
            "status": "testing",
            "evidence": "2 regional dental CPA firms signed co-marketing pilots; 5 referrals booked in Month 1.",
        },
    ]
    (startup / "assumptions.json").write_text(json.dumps(assumptions, indent=2), encoding="utf-8")

    interviews = [
        {
            "id": "INT-01",
            "persona": "Owner-Dentist, 5-Chair Family Practice (Austin, TX)",
            "painSeverity": 5,
            "willingnessToPayUsd": 950,
            "workaround": "Office manager spends 14 hrs/week calling Delta & Cigna; 60% of small denials written off.",
            "pilotIntent": True,
            "quote": "Your 90-day audit found $18,400 in recoverable crown and perio claims sitting unworked.",
        },
        {
            "id": "INT-02",
            "persona": "Regional Operations Director, 4-Location Independent Group (CA)",
            "painSeverity": 5,
            "willingnessToPayUsd": 1200,
            "workaround": "Paying outsourced RCM agency 7% of collections (~$5,200/mo) with zero pre-submission prevention.",
            "pilotIntent": True,
            "quote": "Flat $900/mo per clinic saves us $40K a year and cuts our AR days from 48 to 19.",
        },
        {
            "id": "INT-03",
            "persona": "Practice Manager, 4-Chair Pediatric & Ortho Clinic (OH)",
            "painSeverity": 4,
            "willingnessToPayUsd": 900,
            "workaround": "Manual sticky notes in Dentrix + copy-pasted Word appeal templates.",
            "pilotIntent": True,
            "quote": "Payers started using automated rejection bots this year—our denials jumped from 8% to 15%.",
        },
    ]
    (startup / "interviews.json").write_text(json.dumps(interviews, indent=2), encoding="utf-8")

    pacts = [
        {"id": "PACT-C1", "type": "customer", "company": "Oakridge Family Dental (5 chairs)", "segment": "Multi-Chair Independent (3-8 chairs)", "status": "paid", "amountUsd": 10800},
        {"id": "PACT-C2", "type": "customer", "company": "Bayview Dental Group (4 sites)", "segment": "Regional Independent Group", "status": "paid", "amountUsd": 38400},
        {"id": "PACT-C3", "type": "customer", "company": "Summit Pediatric Dental", "segment": "Multi-Chair Independent (3-8 chairs)", "status": "signed", "amountUsd": 10800},
        {"id": "PACT-I1", "type": "investor", "company": "HealthOps Pre-Seed Syndicate", "segment": "Vertical SaaS Angels", "status": "soft_circled", "amountUsd": 175000},
        {"id": "PACT-I2", "type": "investor", "company": "Pacific Founders Fund", "segment": "Pre-Seed VC", "status": "soft_circled", "amountUsd": 150000},
    ]
    (startup / "pacts.json").write_text(json.dumps(pacts, indent=2), encoding="utf-8")

    competitors = [
        {
            "id": "COMP-01",
            "name": "Outsourced RCM Agencies",
            "pricing": "6%-8% of collections ($4K-$8K/mo)",
            "icp": "Independent dental clinics",
            "strengths": "Done-for-you human phone follow-up",
            "weaknesses": "Reactive post-denial work; opaque percentage-of-revenue tax",
            "ourEdge": "Pre-submission AI scrubbing + flat $900/mo SaaS pricing",
            "xScore": 24,
            "yScore": 28,
        },
        {
            "id": "COMP-02",
            "name": "Legacy Clearinghouse Add-Ons",
            "pricing": "$350/mo + per-claim fees",
            "icp": "General practices",
            "strengths": "Bundled with EDI claim routing",
            "weaknesses": "Basic syntax checks only; misses payer clinical-necessity rules",
            "ourEdge": "Payer-specific CDT/radiograph rule graph & auto-narratives",
            "xScore": 52,
            "yScore": 44,
        },
        {
            "id": "COMP-03",
            "name": "In-House Staff & Spreadsheets",
            "pricing": "$25-$181 labor rework per claim",
            "icp": "Solo & small clinics",
            "strengths": "Zero software fee",
            "weaknesses": "60%-65% of denied claims abandoned due to staff overload",
            "ourEdge": "90-second automated scrubbing & 1-click clinical appeals",
            "xScore": 18,
            "yScore": 58,
        },
    ]
    (startup / "competitors.json").write_text(json.dumps(competitors, indent=2), encoding="utf-8")

    pmf = {
        "responses": [
            *[{"segment": "Multi-Chair Independent (3-8 chairs)", "disappointment": "very_disappointed", "mainBenefit": "Catches missing narratives before submission"} for _ in range(11)],
            *[{"segment": "Multi-Chair Independent (3-8 chairs)", "disappointment": "somewhat_disappointed", "mainBenefit": "Saves billing coordinator 8 hrs/wk"} for _ in range(5)],
            *[{"segment": "Solo 1-Chair Practice", "disappointment": "somewhat_disappointed", "mainBenefit": "Helpful reports"} for _ in range(3)],
            *[{"segment": "Solo 1-Chair Practice", "disappointment": "not_disappointed", "mainBenefit": "Low monthly claim volume"} for _ in range(3)],
        ],
        "cohorts": [
            {"cohort": "2026-06", "m1": 100, "m2": 95, "m3": 92, "m4": 92},
            {"cohort": "2026-07", "m1": 100, "m2": 96, "m3": 94, "m4": 94},
        ],
    }
    (startup / "pmf.json").write_text(json.dumps(pmf, indent=2), encoding="utf-8")

    sprints = [
        {
            "id": "SPR-01",
            "goal": "Ship automated Dentrix + OpenDental pre-submission scrubber and close 4 clinics",
            "status": "completed",
            "fiVelocityScore": 4.6,
            "completedTasks": 7,
            "totalTasks": 7,
        },
        {
            "id": "SPR-02",
            "goal": "Launch dental CPA partner audit portal and grow MRR from $14.4K to $20K",
            "status": "active",
            "fiVelocityScore": 4.4,
            "completedTasks": 5,
            "totalTasks": 6,
        },
    ]
    (startup / "sprints.json").write_text(json.dumps(sprints, indent=2), encoding="utf-8")

    (docs / "INVESTOR_UPDATE.md").write_text(
        "# ClaimPulse — Monthly Investor Update\n\n"
        "- **MRR:** $14,400 (+28% MoM across 16 paying clinics) `[VALIDATED]`\n"
        "- **Gross Margin:** 84% ($0.031 AI scrubbing COGS per claim) `[VALIDATED]`\n"
        "- **Sean Ellis PMF:** 50.0% Very Disappointed overall (**68.8%** in Multi-Chair HXC segment) `[VALIDATED]`\n"
        "- **Pre-Seed Round:** $325K / $750K soft-circled via VC Lab PACTs `[VALIDATED]`\n"
        "- **Top Ask:** Intros to regional dental CPA firms or 3–10 location independent dental groups.\n",
        encoding="utf-8",
    )

    # Rich 13-slide Founder Institute / VC Lab Investor Deck using ALL visual slide engines
    deck_json = {
        "meta": {
            "companyName": "ClaimPulse",
            "website": "https://claimpulse.io",
            "contactName": "Elena Vance, CEO & Co-Founder",
            "contactEmail": "founders@claimpulse.io",
            "deckMode": "traction",
            "fiOneSentencePitch": fi_pitch,
            "stage": "pre_seed_traction",
            "impactThesis": "Keep independent family dental practices financially thriving by eliminating $4B+ in preventable insurance claim denials.",
            "targetPitchMinutes": 3,
        },
        "theme": {
            "preset": "obsidian-gold",
            "bg": "#090D16",
            "surface": "#131B2E",
            "text": "#F8FAFC",
            "muted": "#94A3B8",
            "accent": "#10B981",
            "accent2": "#F59E0B",
            "border": "#1F2A44",
        },
        "slides": [
            {
                "id": "cover",
                "type": "cover",
                "kicker": "PRE-SEED TRACTION & INVESTOR DECK • DEMO CASE STUDY",
                "headline": "Cut Dental Insurance Claim Denials Below 3% Automatically",
                "subheadline": fi_pitch,
                "footer": "Elena Vance, CEO • founders@claimpulse.io • claimpulse.io • Built with Startup Antigravity",
                "notes": "15 seconds. Open with immediate clarity: ClaimPulse prevents insurance denials before submission for independent multi-chair dental clinics.",
            },
            {
                "id": "traction",
                "type": "metrics",
                "kicker": "01 / TRACTION & VELOCITY",
                "headline": "$14.4K MRR Growing 28% Monthly With 84% Gross Margin",
                "metrics": [
                    {"value": "$14,400", "label": "Monthly Recurring Revenue (16 Clinics) [VALIDATED]"},
                    {"value": "+28%", "label": "Avg MoM Revenue Growth (Last 6 Mos) [VALIDATED]"},
                    {"value": "84%", "label": "Gross Profit Margin ($0.03/claim COGS) [VALIDATED]"},
                    {"value": "68.8%", "label": "Sean Ellis Very Disappointed (HXC) [VALIDATED]"},
                ],
                "callout": "$485K in clinical revenue already recovered across 28,400 scrubbed claims — zero paid ads spent [VALIDATED].",
                "notes": "20 seconds. Lead with proof: 16 paying clinics, 84% gross margin, and 68.8% Sean Ellis PMF in our core 3-8 chair ICP.",
            },
            {
                "id": "mrr-chart",
                "type": "chart-line",
                "kicker": "02 / REVENUE MOMENTUM",
                "headline": "8x MRR Growth In Six Months Via Audit-Led Onboarding",
                "chartTitle": "Verified Monthly Recurring Revenue (USD) — Last 6 Months [VALIDATED]",
                "unitPrefix": "$",
                "series": [
                    {"label": "Jun", "value": 1800},
                    {"label": "Jul", "value": 3600},
                    {"label": "Aug", "value": 5400},
                    {"label": "Sep", "value": 8100},
                    {"label": "Oct", "value": 10800},
                    {"label": "Nov", "value": 14400},
                ],
                "callout": "94% 4-month logo retention; 5 additional multi-chair practices in paid onboarding queue [VALIDATED].",
                "notes": "15 seconds. Point to the consistent compounding curve driven by our free 90-day Denial Leakage Audit.",
            },
            {
                "id": "problem",
                "type": "bullets",
                "kicker": "03 / THE PROBLEM",
                "headline": "Independent Dental Clinics Lose $50K+ Yearly To Preventable Denials",
                "bullets": [
                    {"label": "10–15% Denial Rate", "text": "Automated payer bots reject 1 in 8 first-submission dental claims over missing narratives or X-ray attachments [VALIDATED]"},
                    {"label": "60–65% Abandoned", "text": "Overloaded front-desk teams never resubmit most denied claims—turning billing friction into permanent revenue loss [VALIDATED]"},
                    {"label": "$25–$181 Rework Tax", "text": "Manual appeals burn 14+ staff hours/week, while legacy RCM agencies skim 6–8% of total collections [VALIDATED]"},
                ],
                "callout": "Industry data: ADA Health Policy Institute, US Census Bureau & national dental RCM benchmarks [VALIDATED].",
                "notes": "15 seconds. Quantify the exact pain every independent dentist feels every Friday.",
            },
            {
                "id": "solution",
                "type": "bullets",
                "kicker": "04 / THE SOLUTION & SECRET SAUCE",
                "headline": "Pre-Submission AI Scrubbing Stops Denials Before Claims Leave",
                "bullets": [
                    {"label": "Under 3% Denials", "text": "Payer-specific CDT & radiograph checks flag missing clinical proof in 90 seconds before EDI submission [VALIDATED]"},
                    {"label": "1-Click Appeals", "text": "Auto-generates payer-compliant clinical narratives and recovers aging unworked denials automatically [VALIDATED]"},
                    {"label": "Flat $900/mo SaaS", "text": "Replaces 6–8% collection agencies with transparent flat-fee software saving clinics $35K–$50K/year [VALIDATED]"},
                ],
                "callout": "Secret Sauce: Proprietary payer-rule graph trained on 140K adjudicated dental claims—compounds with every clinic.",
                "notes": "15 seconds. Mirror the 3 problem bullets 1-to-1 and highlight the compounding payer-rule graph moat.",
            },
            {
                "id": "product",
                "type": "product-frame",
                "kicker": "05 / LIVE PRODUCT IN PRODUCTION",
                "headline": "Zero-Friction Sync With OpenDental, Dentrix & QuickBooks",
                "appUrl": "app.claimpulse.io/claims-queue",
                "imagePath": "",
                "caption": "Live HIPAA-compliant pre-submission queue • Zero-data-retention AI inference",
                "mockupSteps": [
                    "1. Connect OpenDental or Dentrix read-only sync in under 10 minutes",
                    "2. Engine scores every claim against payer-specific CDT & X-ray rules",
                    "3. Auto-drafts missing narratives & reconciles ERA deposits in QuickBooks",
                ],
                "highlightsTitle": "Measured Customer Outcomes",
                "highlights": [
                    "First-pass denial rate dropped from 13.4% to 2.7% across 16 live clinics [VALIDATED]",
                    "Average $18,400 in forgotten 90-day claims recovered in Week 1 audit [VALIDATED]",
                    "Billing coordinators save 11.5 hours/week on payer phone holds [VALIDATED]",
                ],
                "notes": "20 seconds. Emphasize 10-minute onboarding and immediate Week-1 cash recovery.",
            },
            {
                "id": "why-now",
                "type": "bullets",
                "kicker": "06 / WHY NOW",
                "headline": "Payer AI Rejection Bots Created An Urgent Arms Race",
                "bullets": [
                    {"label": "Payer Automation", "text": "78% of US dental practices report surging claim denials after insurers deployed automated review bots [VALIDATED]"},
                    {"label": "Staffing Crunch", "text": "Experienced dental billing coordinators are scarce and costly—clinics cannot hire their way out [VALIDATED]"},
                    {"label": "84% AI Margins", "text": "Tiered model routing (85% fast models + caching) drops claim scrubbing cost to $0.031/claim [VALIDATED]"},
                ],
                "notes": "15 seconds. Explain why 2026 is the exact inflection point for automated clinic-side defense.",
            },
            {
                "id": "market",
                "type": "chart-bar",
                "kicker": "07 / BOTTOM-UP MARKET SIZE",
                "headline": "$1.47B Bottom-Up US Dental Market Across 135,665 Clinics",
                "chartTitle": "Bottom-Up Annual Market Opportunity (USD Millions) — ADA & US Census Data",
                "unitPrefix": "$",
                "unitSuffix": "M",
                "series": [
                    {"label": "US TAM (135.7K Clinics)", "value": 1465},
                    {"label": "Multi-Chair SAM (55K)", "value": 594},
                    {"label": "5-Yr SOM (3.5K Clinics)", "value": 37.8},
                ],
                "callout": "Pure bottom-up math: 135,665 US dental establishments (Census/ADA) × $10,800/yr ACV = $1.47B TAM [VALIDATED].",
                "notes": "15 seconds. Show disciplined bottom-up arithmetic—just 6.4% of multi-chair clinics yields $37.8M ARR.",
            },
            {
                "id": "unit-economics",
                "type": "metrics",
                "kicker": "08 / UNIT ECONOMICS & PROFIT OS",
                "headline": "1.5-Month CAC Payback & 16.4:1 LTV-To-CAC Ratio",
                "metrics": [
                    {"value": "$900", "label": "Flat Monthly ARPA ($10.8K ACV) [VALIDATED]"},
                    {"value": "$1,150", "label": "Blended Customer Acquisition Cost [VALIDATED]"},
                    {"value": "$18,900", "label": "Net Customer Lifetime Value (LTV) [VALIDATED]"},
                    {"value": "1.5 mo", "label": "Gross-Margin CAC Payback Period [VALIDATED]"},
                ],
                "callout": "Default-Alive unlocked at 38 paying clinics (~$34K MRR); zero ad-burn dependency [VALIDATED].",
                "notes": "15 seconds. VC Lab partners love <3 month payback and clear Default-Alive math.",
            },
            {
                "id": "competition",
                "type": "quadrant-2x2",
                "kicker": "09 / COMPETITION & DEFENSIBLE MOAT",
                "headline": "Only Flat-Fee AI Platform Preventing Denials Pre-Submission",
                "xAxisLeft": "Reactive Post-Denial Rework",
                "xAxisRight": "Pre-Submission AI Prevention",
                "yAxisBottom": "Opaque % Of Collections Tax",
                "yAxisTop": "Transparent Flat-Fee SaaS",
                "points": [
                    {"name": "ClaimPulse", "x": 88, "y": 88, "highlight": True},
                    {"name": "Outsourced RCM Agencies", "x": 24, "y": 28, "highlight": False},
                    {"name": "Clearinghouse Add-Ons", "x": 52, "y": 44, "highlight": False},
                    {"name": "In-House Staff / DIY", "x": 18, "y": 58, "highlight": False},
                ],
                "callout": "Incumbent RCM agencies cannot adopt flat-fee prevention without cannibalizing 6–8% collection fees.",
                "notes": "15 seconds. Highlight structural business-model lock-in preventing incumbents from copying us.",
            },
            {
                "id": "gtm",
                "type": "bullets",
                "kicker": "10 / REPEATABLE GO-TO-MARKET",
                "headline": "Audit-Led Wedge Converts 42% Of Multi-Chair Clinics In 14 Days",
                "bullets": [
                    {"label": "Free 90-Day Audit", "text": "Read-only EHR scan surfaces $12K–$25K in unworked claims in 15 minutes—selling the product on proof [VALIDATED]"},
                    {"label": "Dental CPA Channel", "text": "Co-distribution with regional dental CPAs & fractional CFOs managing 40–120 practices each [TARGET]"},
                    {"label": "Study Club Referrals", "text": "Peer-driven referrals inside Seattle Study Clubs & state ADA chapters with 1.5-mo payback [VALIDATED]"},
                ],
                "notes": "15 seconds. Our free 90-day audit turns cold clinics into signed Paid-Pilot PACTs in under two weeks.",
            },
            {
                "id": "team-impact",
                "type": "two-column",
                "kicker": "11 / TEAM, ADVISORS & FOR-PROGRESS IMPACT",
                "headline": "Domain-Native Builders Committed To Ethical Healthcare Ops",
                "leftTitle": "Founding Team & FI FAST Advisors",
                "leftItems": [
                    "Elena Vance (CEO) — 9 yrs leading Dental RCM Ops across 42 multi-chair clinics",
                    "Marcus Chen (CTO) — Ex-Staff ML & FHIR Integration Engineer (HIPAA scale)",
                    "Dr. Priya Nair, DDS (FAST Advisor) — Former State Dental Association President",
                ],
                "rightTitle": "For-Progress Impact & Mensarius Code",
                "rightItems": [
                    "UN SDG 3 iKPI: $485K recovered for family clinics ($5M 18-mo target) [VALIDATED]",
                    "HIPAA BAA & zero-data-retention AI inference — never sells patient data",
                    "Transparent flat pricing, zero lock-in contracts, fair stakeholder equity",
                ],
                "notes": "15 seconds. Show unfair domain access plus ironclad HIPAA & Mensarius ethics.",
            },
            {
                "id": "ask",
                "type": "ask",
                "kicker": "12 / THE ASK & 18-MONTH MILESTONES",
                "headline": "Raising $750K Pre-Seed To Reach $100K MRR In 18 Months",
                "askAmount": "$750K",
                "instrument": "Post-Money SAFE ($6M Cap) • $325K Soft-Circled via VC Lab PACTs",
                "allocations": [
                    {"label": "Dental CPA & Study-Club GTM", "percent": "45%"},
                    {"label": "Payer Rule Graph & EHR Sync", "percent": "40%"},
                    {"label": "HIPAA SOC2 Type II & Buffer", "percent": "15%"},
                ],
                "milestones": [
                    "Month 6: 40 paying clinics ($36K MRR) & Default-Alive option unlocked [TARGET]",
                    "Month 12: 75 paying clinics ($67.5K MRR) across 5 states + Dentrix/Eaglesoft live [TARGET]",
                    "Month 18: 112+ paying clinics ($100K+ MRR / $1.2M ARR) — Series A ready [TARGET]",
                ],
                "impactMetric": "For-Progress Target: $5.0M+ clinical revenue recovered for independent family practices",
                "notes": "20 seconds. $325K already soft-circled via Investor PACTs. Invite clear next steps to review the Data Room.",
            },
        ],
    }
    deck_path = pitch_dir / "deck.json"
    deck_path.write_text(json.dumps(deck_json, indent=2), encoding="utf-8")

    # Lint & compile all 4 live visual outputs
    lint_res = lint_deck(deck_json)
    deck_res = build_deck(deck_path)
    dash_res = build_dashboard(ws)
    landing_res = build_landing_page(ws)
    dr_res = build_data_room(ws)

    return {
        "ok": True,
        "companyName": "ClaimPulse",
        "workspace": str(ws),
        "slideCount": len(deck_json["slides"]),
        "deckLintPassed": lint_res["passed"],
        "deckReadinessScore": lint_res["readinessScore"],
        "dashboardHtml": dash_res.get("htmlPath") or str(ws / "dashboard" / "index.html"),
        "pitchDeckHtml": deck_res.get("htmlPath") or str(ws / "pitch-deck" / "index.html"),
        "landingHtml": landing_res.get("htmlPath") or str(ws / "landing" / "index.html"),
        "dataRoomHtml": dr_res["portalHtml"],
        "dataRoomReadinessPct": dr_res["readinessPct"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the realistic ClaimPulse demo workspace.")
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
