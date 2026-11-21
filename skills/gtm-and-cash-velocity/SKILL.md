---
name: gtm-and-cash-velocity
description: >-
  Design high-margin value-based pricing, ethical acquisition loops, cold outbound
  sequences, and launch playbooks (Show HN, Product Hunt, LinkedIn, partner channels)
  to win the first 100 paying customers quickly without dark patterns or ad burn. Use
  when setting pricing, crafting landing page copy, or planning a customer launch.
---

# Go-To-Market & Ethical Cash Velocity

Revenue speed comes from **sharp positioning + value-based pricing + direct distribution**, not burning cash on paid ads before Product-Market Fit.

See [first-100-customers.md](./resources/first-100-customers.md) for ethical cold outreach scripts and launch checklists.

## Step 1: Value-Based Pricing (Maximize Ethical Margin)

1. **Anchor to Customer ROI (10x Rule)**: If your product saves or generates \$10,000/month for a buyer, price at \$500–\$1,500/month — never \$19/month cost-plus.
2. **Design 3 Clean Tiers**:
   - *Starter / Core*: High-margin self-serve entry point.
   - *Growth / Pro* (Anchor): Core workflow + team/ROI features where 60%+ of profit sits.
   - *Founding Partner / Annual*: Annual upfront payment (15–20% discount) to pull cash forward and fund growth without dilution.
3. **Mensarius Pricing Ethics**: Transparent pricing page, 1-click cancellation, zero surprise renewals, zero fake urgency timers.

## Step 2: Pick 2 Primary Acquisition Channels (Ignore the Rest)

Select based on ACV:
- **ACV >= \$3,000/yr**: Founder-led hyper-targeted outbound (50 personalized messages/week) + warm advisor/partner intros + live ROI audits.
- **ACV \$300–\$3,000/yr**: Product-led free diagnostic/calculator + Show HN / Product Hunt / niche communities + customer case studies.

## Step 3: Instrument Cash Velocity

- Track every serious buyer conversation in `pact_pipeline_manage(kind="customer", ...)` — convert vague interest into written Paid Pilot PACTs or direct checkout links.
- Delegate copy, offer positioning, and outbound teardowns to the `ethical-growth-strategist` subagent.
- **Canva Launch Visuals (Optional Companion):** If the official Canva plugin (`canva_canva`) is active, activate `design-studio-canva-figma` to generate brand-checked Product Hunt gallery cards (`1270x760`), LinkedIn carousels, and social launch variants via `canva-resize-for-social-media`.
- **Product Hunt Launch Engine:** When ready for a public Product Hunt debut, activate `product-hunt-launch` and run `product_hunt_kit_build` to lint your <=60-char tagline, generate `launch/product-hunt/PH_LAUNCH_KIT.md` (Maker Comment, gallery storyboard, ethical outreach), and run a zero-upvote-ring launch day.
