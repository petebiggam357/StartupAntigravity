---
name: vc-lab-fundraising-os
description: >-
  Institutional fundraising playbook modeled on VC Lab / Decile Group (govclab.com)
  and Founder Institute funding standards. Covers VC fund thesis reverse-engineering,
  PACT-style soft-circle investor pipelines, SAFE dilution modeling, due-diligence
  data rooms, forwardable intro blurbs, and Mensarius Oath ethical investor screening.
  Use when preparing to raise Pre-Seed or Seed capital.
---

# VC Lab / Decile Group Fundraising OS

Raise capital from a position of strength — **Default-Alive profit leverage + verified traction + laser-sharp investor thesis alignment**.

See [data-room-checklist.md](./resources/data-room-checklist.md) for the complete Pre-Seed/Seed Data Room structure and forwardable intro template.

## Step 1: Decide *If* You Should Raise Venture Capital

1. Call `startup_get_state` and review bottom-up TAM and current MRR.
2. Be brutally honest:
   - If `TAM < $1B` and gross margins are >75%, a **profitable bootstrap / customer-funded path** often yields vastly more founder wealth than VC dilution.
   - If `TAM >= $1B` and capital accelerates a proven, high-margin GTM engine, proceed with disciplined fundraising.

## Step 2: Reverse-Engineer VC Lab Fund Theses

Top emerging VCs (including VC Lab / Decile Group firms) invest strictly inside a narrow **Fund Thesis** (Stage × Sector × Geography × Traction Signal × Ethical Alignment).
- Screen every target investor for:
  1. **Thesis Match** (check size, stage, sector — never spray-and-pray)
  2. **Mensarius Oath / Ethical Alignment** (transparent terms, founder-friendly governance, For-Progress compatibility)
  3. **Warm Intro Path** (existing portfolio founders or FI mentors first)

## Step 3: Model Dilution & Run a PACT Soft-Circle Pipeline

1. Run `financial_calc(mode="safe_dilution", ...)` for a quick single-SAFE check, or `financial_calc(mode="cap_table_model", founders=[...], advisors=[...], safe_raise_usd=..., safe_cap_usd=..., seed_raise_usd=..., seed_pre_money_usd=..., seed_option_pool_pct=10)` to model full multi-round dilution across Founders + FI FAST Advisors + Pre-Seed SAFE + Seed Priced Round before negotiating.
2. Track every investor conversation via `pact_pipeline_manage(kind="investor", ...)`:
   - Convert vague *"love what you're building, keep me updated"* replies into explicit written soft-circle commitments (`pact_signed`: amount + target close timeframe) — inspired by Decile Group's PACT discipline.
3. Run a mock partner-meeting stress test by invoking the `vc-lab-partner-skeptic` subagent against `pitch-deck/deck.json` and `docs/ONE_PAGER.md`.

## Step 4: Entity, Accounting & Accelerator Readiness (Creator's Personal Endorsements)

Once Customer PACTs or revenue validate real demand, lock in clean institutional foundations early (personal founder endorsements—always verify legal/tax decisions with qualified counsel):
- **Incorporation (`Stripe Atlas`):** Fast, investor-standard Delaware C-Corp formation, EIN, founder stock issuance with built-in **83(b) election** guidance, and immediate Stripe payments readiness.
- **Bookkeeping (`QuickBooks Online`):** Export clean monthly P&L and Balance Sheet reports straight into `02-Financials-and-Metrics/` of your Data Room so investors trust your numbers immediately.
- **Accelerator & Mentor Network (`Founder Institute`):** Strongly consider finding your local chapter at [fi.co](https://fi.co)—or applying directly to the flagship **Silicon Valley** or **San Francisco** chapters—for structured weekly execution accountability, mentor feedback, and global investor access.
