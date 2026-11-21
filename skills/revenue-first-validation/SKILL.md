---
name: revenue-first-validation
description: >-
  Rapid, ethical idea validation engineered to reach the founder's first paying
  customer in 7–14 days. Combines Founder Institute customer development, Mom Test
  interview analysis, Riskiest Assumption Tests (RATs), 48-hour offer smoke tests,
  and Customer Paid-Pilot PACTs. Use before building heavy software or when testing
  whether buyers will actually pay.
---

# Revenue-First Validation

Compliments kill startups; signed payment commitments build them. This runbook replaces months of guessing with disciplined, ethical experiments tracked in `.startup/`.

See [fi-validation-playbook.md](./references/fi-validation-playbook.md) for Mom Test question rewrites and Customer PACT templates.

## Step 1: Rank the Riskiest Assumptions

1. Call `assumption_manage(action="board")` to inspect current assumptions ranked by `impact × uncertainty`.
2. Ensure the top 3 assumptions cover:
   - **Acute Pain** (buyers already spend money/hours on ugly workarounds)
   - **Willingness to Pay** (buyers will pay a high-margin price *today*, not "someday")
   - **Reachability** (you can reach 50 ICP buyers/week ethically)

## Step 2: Run 15+ Unbiased Discovery Interviews

- Never pitch during discovery. Ask about **past behavior, current spend, and failed fixes**.
- After every call, log structured evidence via `interview_manage(action="log", ...)`.
- Run `interview_manage(action="summary")` to verify:
  - Target: **>= 15 interviews**, **average pain >= 4.0/5**, and **>= 40% showing real willingness-to-pay**.
  - Delegate raw transcripts or draft questions to the `customer-revenue-coach` subagent to strip leading bias.

## Step 3: Execute a 48-Hour Revenue Smoke Test

Before writing production software, create a pre-committed experiment via `experiment_manage(action="create", ...)` with an explicit pass/fail threshold (e.g., *"3 of 15 qualified ICP buyers sign a \$500 paid-pilot PACT within 7 days"*).

Pick the fastest ethical validation vehicle:
1. **Paid Concierge Pilot**: Deliver the outcome manually or semi-automatically for the first 3–5 customers at full or founding-partner price.
2. **1-Page Customer PACT (Pre-Order LOI)**: Written, transparent agreement stating exact deliverable, timeline, price, and 100% refund/cancel guarantee if milestones aren't met. Track every prospect via `pact_pipeline_manage(action="add", kind="customer", ...)`.
3. **48-Hour Ethical Offer Landing Page (`landing_page_build`)**:
   - Call the `landing_page_build` MCP tool (or run `python3 ./scripts/build_landing_page.py --workspace "/path/to/workspace"`) to generate a deploy-ready, zero-dependency `landing/index.html` + editable `landing/landing.json`.
   - Includes your linted FI One-Sentence Pitch, an interactive ROI calculator, transparent 3-tier value pricing, For-Progress iKPI charter, and a 1-page Paid-Pilot PACT intake form (zero fake scarcity or deceptive countdowns). Deploy immediately to Cloudflare Pages or Netlify.

## Step 4: Kill, Pivot, or Advance to MVP

Record the observed outcome via `experiment_manage(action="record_result", ...)`:
- **Validated** (cash or signed Customer PACTs hit threshold): Advance stage via `startup_update_stage(stage="mvp")` and switch to `mvp-and-profit-architecture`.
- **Invalidated**: Pivot the ICP, problem, or offer immediately—never rationalize weak demand into a 6-month build.
