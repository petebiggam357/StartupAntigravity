---
name: mvp-and-profit-architecture
description: >-
  Scope a 7-day shippable Vertical Slice MVP with an explicit NOT-Building-Yet Cut-List
  and a high-margin (>75% gross margin) technical architecture. Use once problem and
  willingness-to-pay are validated, or whenever a founder needs to cut scope, pick a
  fast lean stack, or audit cloud/AI COGS before writing code.
---

# MVP & High-Margin Profit Architecture

Build the smallest possible product that delivers the **#1 paid customer outcome** within 7 days while protecting **>= 75% gross margins** from day one.

See [lean-stack-defaults.md](./references/lean-stack-defaults.md) for recommended boring, zero-ops stacks and COGS guardrails.

## Step 1: Verify Validation Gate

Call `startup_get_state`. If `stage` is still `idea` with zero interviews and zero Customer PACTs, warn the founder and confirm whether they want to run a 48-hour smoke test (`revenue-first-validation`) before writing code.

## Step 2: Define the 7-Day Vertical Slice (`docs/MVP_SPEC.md`)

1. **Single Core Job**: Identify the ONE end-to-end user flow that justifies the invoice.
2. **Concierge Over Automation**: Manually execute anything that happens fewer than 20 times a week (onboarding, custom reports, billing adjustments).
3. **Mandatory "NOT Building Yet" Cut-List**: Explicitly list every tempting feature deferred until $10K MRR (microservices, Kubernetes, custom RBAC/SSO, multi-region replication, custom billing logic, mobile apps, public blogs).

## Step 3: Margin & COGS Stress Test

Before finalizing the architecture, calculate variable cost per customer per month (LLM API tokens, GPU minutes, SMS/email APIs, storage, bandwidth):
- Compute Gross Margin: `(ARPA - Variable COGS) / ARPA`.
- If Gross Margin < **75%**, either optimize caching/model routing, move to value-based higher pricing, or eliminate unprofitable usage tiers.
- Run `financial_calc(mode="unit_economics", ...)` to verify payback and LTV:CAC.

## Step 4: Architecture Review

Delegate the drafted `docs/MVP_SPEC.md` to the `lean-cto-margin-architect` subagent to cut another 30% of unnecessary complexity before coding starts.

- **Figma UI & Code Sync (Optional Companion):** If the official Figma plugin (`figma_figma`) is active, activate `design-studio-canva-figma` to push your 48-hour landing page into Figma frames (`figma-generate-design`) or turn approved Figma wireframes directly into your 7-day vertical slice (`figma-design-to-code`).
- **Zero-Double-Token Cloud & Mobile Shipping (`replit-launchpad`):** Want to ship a Web Platform or Expo/React Native Mobile App on a free tier without DevOps overhead? Activate `replit-launchpad` and call `replit_workspace_prepare` to sync your local Antigravity Git repo straight into Replit (`https://replit.com/refer/peterbiggam`)—starting from the Replit Design System without wasting duplicate AI tokens.
- **Post-PMF Multi-Agent Engineering Scale (`fi-alumni-scale-stack`):** Once real customer demand / PMF is verified, sync `docs/SHELLED_HANDOFF.md` (`ai_connectors_manage(action="sync_context", targets=["shelled"])`) to coordinate specialist architect, coder, tester, and reviewer PR pods via **Shelled AI** (`https://www.shelled.ai/`, built by FI Graduate Jacob Wellinghoff).
