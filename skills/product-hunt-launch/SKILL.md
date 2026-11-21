---
name: product-hunt-launch
description: >-
  End-to-end ethical Product Hunt launch engine. Enforces Product Hunt's exact
  character limits (name <=40, buzzword-free tagline <=60, description <=260),
  builds a complete `launch/product-hunt/PH_LAUNCH_KIT.md` (Maker Comment, 1270x760
  gallery storyboard for Canva/Figma, ethical T-14 to Launch Day runbook, and
  conversion funnel), and prohibits upvote rings or dark patterns. Use whenever a
  founder wants to launch their product on Product Hunt.
---

# Product Hunt Launch Engine (Ethical, High-Conversion Playbook)

A great Product Hunt launch isn't about vanity upvote rank — it's about turning 24 hours of focused attention into **paying customers, verified feedback, and compounding SEO/social proof** without violating Product Hunt's anti-spam rules or the Mensarius Oath.

See [ph-launch-playbook.md](./references/ph-launch-playbook.md) for the exact T-14 timeline, 12:01 AM PT Launch-Day runbook, and ethical community outreach rules.

## Step 1: Verify Launch Readiness (Don't Launch Vaporware)

Call `startup_get_state`. Confirm the founder has:
1. A live, self-serve or instant-demo URL (e.g., `landing/index.html` or live Replit preview via `replit-launchpad`).
2. Transparent pricing + a clear Product Hunt community offer (e.g., 30% off founding-partner rate or extended 14-day risk-free pilot).
3. Zero broken signup/checkout links and real activation tracking.

## Step 2: Generate & Lint the Product Hunt Launch Kit (`product_hunt_kit_build`)

Call the `product_hunt_kit_build` MCP tool:
- `workspace_path`: Startup workspace path
- Optional overrides: `tagline` (<= 60 chars, zero buzzwords!), `description` (<= 260 chars), `topics` (max 3), `ph_offer`, `launch_date`

This automatically lints Product Hunt's hard character limits AND FI buzzword rules, and writes:
- **`launch/product-hunt/PH_LAUNCH_KIT.md`** — Copy-paste submission fields, First Maker Comment (personal founder story + For-Progress iKPI + honest offer), 5-card `1270x760` gallery storyboard, ethical outreach messages, and launch-day checklist.
- **`launch/product-hunt/launch-plan.json`** — Structured submission spec and lint audit.

Fix every `error` or `warning` in the returned lint report before submitting.

## Step 3: Build `1270x760` Gallery Visuals & `240x240` Thumbnail

- If **Canva** (`canva_canva`) or **Figma** (`figma_figma`) companion plugins are active, activate `design-studio-canva-figma` and build the exact 5 gallery slides (`1270x760`) + square logo thumbnail (`240x240`) from the storyboard in `PH_LAUNCH_KIT.md`.
- Record a crisp **60–90 second Loom/demo video** showing the core paid workflow inside the first 10 seconds (no 30-second animated logo intros!).

## Step 4: Execute Launch Day Ethically (Zero Upvote Rings)

- **Strict Mensarius & PH Compliance:** NEVER buy upvotes, use automated bots, DM strangers asking "please upvote us", or join upvote-exchange pods (Product Hunt filters and penalizes coordinated upvote rings). Instead, ask genuine supporters (pilot customers, FI mentors, advisors, newsletter readers) to **check out the launch and leave honest questions or feedback**.
- Launch at **12:01 AM Pacific Time (PT)** (Tuesday–Thursday for max reach, or Friday–Sunday for a higher shot at top-3 badge with lower competition).
- Post the **First Maker Comment** within 2 minutes and reply thoughtfully to every single comment all day.
- Log every resulting buyer lead or Paid Pilot PACT into `pact_pipeline_manage(kind="customer", ...)` and summarize launch ROI in `sprint_manage`.
