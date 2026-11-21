---
name: advisors-equity-and-fast
description: >-
  Structure fair, fast startup advisor agreements using Founder Institute's FAST
  Agreement (Founder/Advisor Standard Template) matrix, evaluate co-founder equity
  splits, and protect cap table hygiene. Use when bringing on strategic advisors,
  mentors, or structuring early team equity.
---

# Advisors, Equity & Founder Institute FAST Agreement

World-class advisors unlock customer introductions, domain credibility, and investor access — but bad advisor deals clutter cap tables for years. Use Founder Institute's **FAST Agreement** benchmarks for fast, fair, milestone-bound advisor equity.

See [fast-agreement-guide.md](./resources/fast-agreement-guide.md) for the complete FI FAST checklist and co-founder vesting rules.

## Step 1: Compute Fair FAST Advisory Equity Deterministically

Call `financial_calc(mode="fast_advisor_equity", stage=..., tier=...)` where:
- `stage`: `idea` | `startup` | `growth`
- `tier`:
  - `standard` (~2 hrs/mo: monthly check-in + email feedback)
  - `strategic` (~5 hrs/mo: bi-weekly sessions + warm customer/investor intros)
  - `expert` (~10 hrs/mo: weekly hands-on help in sales, recruiting, or tech)

## Step 2: Enforce Non-Negotiable Equity Hygiene

1. **24-Month Vesting + 3-Month Trial Cliff**: Never grant fully vested advisor equity up front. A 3-month cliff lets both sides verify real chemistry and output.
2. **Concrete Deliverables**: Write 3 measurable 90-day outcomes (e.g., *"5 warm intros to target ICP buyers"*, *"Review enterprise security architecture"*) before signing.
3. **Total Advisory Pool Cap**: Keep total advisor grants combined under **2–5%** of the cap table. Use `financial_calc(mode="cap_table_model", ...)` to simulate how advisor grants + SAFE + Seed rounds dilute founders over time.
4. **Co-Founder Hygiene**: Always use 4-year vesting with a 1-year cliff for every founder, and remind founders about the strict **30-day IRS 83(b) election** deadline (verify with startup legal counsel!).

> [!IMPORTANT]
> Always remind the founder that FAST templates and equity calculators are educational business frameworks — have qualified startup counsel review final legal agreements and tax filings.
