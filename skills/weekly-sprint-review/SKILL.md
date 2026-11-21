---
name: weekly-sprint-review
description: >-
  Founder Institute weekly sprint accountability and VC Lab monthly investor/mentor
  update generator. Use every week to start or close an execution sprint in
  `.startup/sprints.json`, score velocity (1.0–5.0 FI scale), audit MRR & iKPI
  progress, and compile a crisp `docs/INVESTOR_UPDATE.md`. Pairs cleanly with `/schedule`.
---

# Weekly Sprint Review & Investor Update Engine

Founder Institute cohorts win through relentless weekly execution cadence, and VC Lab investors fund founders who ship transparent, metric-first updates like clockwork.

See [investor-update-template.md](./resources/investor-update-template.md) for the exact VC Lab / FI update structure.

## Step 1: Close Last Week's Sprint (or Start Sprint 1)

1. Call `startup_get_state` and `sprint_manage(action="list")` to inspect live telemetry and prior sprints.
2. If an active sprint is open, close it honestly via `sprint_manage(action="close", ...)`:
   - Record real observed counts: `interviews_completed`, `pacts_sent`, `pacts_signed`, `mrr_delta_usd`, `ikpi_delta`, `fi_velocity_score` (1.0–5.0), `highlights`, `lowlights`, and `blockers`.
   - Never inflate scores: missed commitments are diagnostic gold, not something to hide.

## Step 2: Lock Next Week's Top 3 Commitments

Start the new sprint via `sprint_manage(action="start", ...)`:
- Set **1 Primary Revenue/Validation Goal** (e.g., *"Close 2 paid pilot PACTs worth \$1,000 total"*).
- Set explicit numeric weekly targets for `target_interviews`, `target_pacts`, and `target_mrr_delta_usd`.

## Step 3: Generate the VC Lab / FI Monthly Update

When sharing progress with mentors, advisors (FI FAST), or prospective investors, call:
`sprint_manage(action="investor_update", workspace_path=..., asks=[...])`

This compiles **`docs/INVESTOR_UPDATE.md`** automatically from live `.startup/` state (MRR, Burn, Runway, Gross Margin, Customer/Investor PACTs, Interviews, For-Progress iKPI, Highlights, Lowlights, and Specific Asks).

> [!TIP]
> Recommend the user run `/schedule` if they want Antigravity to trigger an automated Friday afternoon Weekly Sprint Accountability Check.
