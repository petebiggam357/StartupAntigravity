---
name: market-and-unfair-moat
description: >-
  Conduct rigorous bottom-up TAM/SAM/SOM market sizing, competitive landscape teardowns,
  Why-Now macro analysis, and Founder Institute Secret Sauce defensibility audits. Use
  whenever building market slides, sizing an opportunity, analyzing competitors, or
  defining a startup's unfair advantage.
---

# Market Sizing & Unfair Moat Analysis

Investors and Founder Institute mentors immediately dismiss top-down fantasy math (*"1% of a \$1T market"*) and *"we have no competitors."* Use this runbook to prove a real, defensible, profitable market.

See [bottom-up-sizing.md](./references/bottom-up-sizing.md) for segment sources and moat archetypes.

## Step 1: Compute Bottom-Up TAM / SAM / SOM Deterministically

1. Identify the exact buyer unit (e.g., independent US dental clinics, Series A–B SaaS finance teams, independent freight brokers).
2. Estimate realistic **Total Addressable Buyers** from verifiable registries/industry counts (mark `[HYPOTHESIS]` until cited, then `[VALIDATED]`).
3. Estimate realistic **Annual Contract Value (ACV)** anchored to customer discovery WTP.
4. Call `financial_calc(mode="tam_bottom_up", total_buyers=..., annual_acv_usd=..., sam_pct=..., som_buyers=...)` — never do market math by hand.
5. Check whether the market is:
   - **Venture-scale (`TAM >= $1B`)**: Suitable for VC Lab / institutional fundraising.
   - **High-profit niche (`TAM < $1B`)**: Often an incredible bootstrap/cash-cow business — advise the founder honestly on capital strategy rather than forcing VC where it doesn't fit!

## Step 2: Honest Competitive Teardown

Map at least 4 real alternatives (always include **Status Quo / Manual Spreadsheets / Do Nothing**):
- Compare on buyer-relevant axes: Time to Value, Total Cost, Secret Sauce, Switching Friction, and Ethical Data Ownership.
- Update the `competition` slide in `pitch-deck/deck.json` using clear facts (zero buzzwords).

## Step 3: Stress-Test Your "Secret Sauce" & "Why Now?"

Answer both brutally:
1. **Why Now?**: What changed in technology, regulation, or buyer behavior in the last 24 months that makes this possible *today*?
2. **Secret Sauce / Moat**: If a well-funded competitor copies your UI next month, why do customers still stay with you? (Proprietary workflow data, distribution lock-in, switching cost, network effect, regulatory speed, or structural cost advantage.)
