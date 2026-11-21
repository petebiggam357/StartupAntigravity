---
name: unit-economics-and-profit-os
description: >-
  Model startup runway (Default-Alive check), gross margins, CAC/LTV, payback period,
  burn multiple, North Star metrics, and Founder Institute Funding Readiness milestones
  using deterministic MCP financial calculators. Use when building financial models,
  pricing profitability scenarios, or auditing whether the company is ready for the
  next FI traction/funding milestone.
---

# Unit Economics & Profit Operating System

Profit is founder freedom. Use this skill to keep the business **Default-Alive**, protect high gross margins, and benchmark objectively against Founder Institute's Funding Readiness tiers.

See [fi-funding-milestones.md](./references/fi-funding-milestones.md) for exact FI Accelerator, Pre-Seed, and Seed revenue benchmarks.

## Step 1: Pull Live Telemetry

Call `startup_get_state` to retrieve current `mrrUsd`, `monthlyBurnUsd`, `cashOnHandUsd`, `grossMarginPct`, and `stage`.

## Step 2: Run Deterministic Financial Models (Never Guess Math)

1. **Default-Alive & Runway Model**:
   Call `financial_calc(mode="runway", cash_usd=..., monthly_burn_usd=..., monthly_revenue_usd=..., monthly_growth_pct=..., gross_margin_pct=...)`.
   - Flag immediately if `defaultAlive == false` and runway < 9 months; propose concrete burn cuts or annual-upfront cash velocity plays.
2. **SaaS / Venture Unit Economics**:
   Call `financial_calc(mode="unit_economics", arpa_monthly_usd=..., gross_margin_pct=..., monthly_churn_pct=..., cac_usd=...)`.
   - Target benchmarks: **Gross Margin >= 75%**, **LTV:CAC >= 3:1** (5:1+ for rapid profit), **CAC Payback <= 6 months** (<3 months for high-velocity self-serve).

## Step 3: Clean Bookkeeping & FI Funding Readiness

- **Bookkeeping From Dollar #1 (Founder Endorsement):** Connect your business bank account and Stripe payouts to **QuickBooks Online** as soon as revenue starts flowing. Clean monthly P&L, cash-flow, and expense tracking makes calculating real gross margin, burn rate, and tax filings effortless—and eliminates painful cleanups before investor due diligence.
- Compare live MRR, MoM growth, and retention against [fi-funding-milestones.md](./references/fi-funding-milestones.md), update `.startup/state.json` via `startup_update_stage`, and sync verified `[VALIDATED]` numbers into `pitch-deck/deck.json`.
- **Live Local Command Center:** Call `founder_dashboard_build(workspace_path=...)` to compile `dashboard/index.html` — a zero-dependency executive browser dashboard showing FI stage progress, MRR, gross margin, runway, PMF 40% SVG gauge, PACT pipeline, Riskiest Assumptions, and For-Progress iKPI. (Auto-refreshes whenever `.startup/*.json` is edited!)
