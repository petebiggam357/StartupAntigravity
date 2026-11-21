---
name: product-market-fit-engine
description: >-
  Scientific Product-Market Fit (PMF) measurement and customer-reality engine
  combining Sean Ellis's 40% Very Disappointed rule, Superhuman's HXC segmentation
  and 50/50 roadmap framework, cohort retention flattening checks, and Founder
  Institute real-customer demand proof. Use to test whether a real paying customer
  exists, measure PMF quantitatively in `.startup/pmf.json`, narrow ICP to your
  highest-PMF segment, or decide honestly whether to scale, iterate, or pivot.
---

# Product-Market Fit (PMF) Engine — Proving a Real Customer Exists

The #1 killer of startups is building something nobody desperately needs. Never guess whether you have Product-Market Fit—**measure it deterministically** with `pmf_engine_manage` and never pour growth spend into a leaky bucket.

See [pmf-playbook.md](./references/pmf-playbook.md) for the exact 4-question Sean Ellis / Superhuman survey script, segment-narrowing tactics, and Pivot vs. Scale thresholds.

## Step 1: Run the Real-Customer Reality Check (Pre-PMF Gate)

Call `startup_get_state` and `interview_manage(action="summary")`. Before claiming demand exists, verify:
1. **Unprompted Pain:** Buyers already spend real money or hours on ugly workarounds (`avgPainSeverity >= 4.0/5`).
2. **Pull Over Push:** Real prospects commit cash via Paid Pilot PACTs (`pact_pipeline_manage`) without heavy discounting or favors from friends/family.

## Step 2: Run the 4-Question Sean Ellis / Superhuman PMF Survey

Once active users or pilot customers have experienced the core product at least twice, send the exact 4-question survey from [pmf-playbook.md](./references/pmf-playbook.md) and log every response via:

`pmf_engine_manage(action="log_survey", workspace_path=..., user_segment=..., disappointment="very_disappointed"|"somewhat_disappointed"|"not_disappointed", main_benefit=..., requested_improvement=..., paying=true|false, referred_someone=true|false)`

- Minimum trustworthy sample: **15–40 real users** (never include co-founders, relatives, or unpaid favor signups).

## Step 3: Track Retention Curves (`record_retention`)

Log real cohort retention via `pmf_engine_manage(action="record_retention", cohort_label=..., cohort_size=..., day7_pct=..., day30_pct=..., day90_pct=..., net_dollar_retention_pct=...)`.
- **True PMF:** Retention curve **flattens** above 0% (e.g., B2B SaaS D30 >= 75% / D90 >= 65%; consumer D30 >= 25%+), and customers organically refer peers.
- **Leaky Bucket:** Retention trends steadily toward 0% — **STOP paid acquisition immediately** and fix core value first.

## Step 4: Score PMF, Narrow ICP & Generate Investor Proof (`scorecard` & `generate_report`)

1. Call `pmf_engine_manage(action="scorecard", workspace_path=...)`:
   - Inspect **Overall % Very Disappointed** AND **Per-Segment % Very Disappointed**.
   - **Superhuman Secret:** Even if your overall score is 22%, one narrow `user_segment` (your High-Expectation Customer / HXC) may already be at **55%+** — cut the wrong segments and double down on that exact ICP!
   - Follow the auto-generated **50/50 PMF Roadmap**: spend 50% of sprint time doubling down on what `very_disappointed` users love, 50% removing the top blockers of `somewhat_disappointed` users, and **0%** chasing `not_disappointed` users.
2. Call `pmf_engine_manage(action="generate_report", workspace_path=...)` to compile **`docs/PMF_SCORECARD.md`** and sync `[VALIDATED]` PMF proof into `pitch-deck/deck.json` and your VC Lab Data Room!
