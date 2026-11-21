---
name: pitch-deck-builder
description: >-
  Create, edit, lint, and compile a modifiable Founder Institute (FI.co) startup pitch
  deck (`pitch-deck/deck.json` -> interactive 16:9 `index.html` with 3-minute FI pitch
  timer, speaker notes, and 1-click PDF export + Marp `DECK.md`). Use whenever the
  founder wants to generate, update, re-theme, switch between Problem-Solution and
  Traction deck modes, or audit their pitch deck.
---

# Pitch Deck Builder (Founder Institute Edition)

This skill manages the startup's single-source-of-truth pitch deck in `pitch-deck/deck.json` and compiles it into a zero-dependency interactive 16:9 web presentation (`pitch-deck/index.html`) and Markdown export (`pitch-deck/DECK.md`).

## Three Built-In FI & VC Lab Deck Modes

1. **Problem-Solution Deck** (`./resources/deck.problem-solution.json`) — Default for `idea`, `validation`, and early `mvp` stages. Follows FI's strict Problem -> Solution 1-to-1 mirror structure.
2. **Traction / Investor Deck** (`./resources/deck.traction.json`) — Switch to this once you have paying customers / recurring revenue (`pre_seed_traction` or `seed_scale`). Leads immediately with Traction & Revenue Velocity, includes a browser mockup `product-frame`, and plots a `quadrant-2x2` moat map.
3. **3-Slide Investor Teaser Deck** (`./resources/deck.teaser.json`) — Crisp Cover -> Inline SVG Traction Chart (`chart-line`) -> Why Now & Ask teaser recommended by VC Lab to send *before* the first investor call.

## Supported Visual Slide Types (`slide.type`)

- `cover`, `bullets`, `metrics`, `two-column`, `comparison`, `ask`
- `chart-line` / `chart-bar`: Zero-dependency inline SVG MRR / retention / unit-economics charts (`series: [{label, value}]`, `unitPrefix`, `unitSuffix`).
- `quadrant-2x2`: Inline SVG competitive positioning matrix (`xAxisLeft`, `xAxisRight`, `yAxisBottom`, `yAxisTop`, `points: [{name, x, y, highlight}]`).
- `product-frame`: Clean browser mockup embedding a screenshot (`imagePath`, e.g., `assets/screenshot.png`) or crisp wireframe steps (`mockupSteps`) paired with outcome `highlights`.

## Workflow

1. **Inspect Existing Deck & Company State**:
   - Call `startup_get_state` (MCP) to pull verified MRR, interviews, PACTs, FI One-Sentence Pitch, and For-Progress iKPIs.
   - Check if `pitch-deck/deck.json` exists. If not, copy the appropriate starter template from `./resources/` into `pitch-deck/deck.json`.

2. **Apply FI Pitch Deck Standards Before Editing**:
   - **Cover**: Company name, website, CEO contact, and the **FI One-Sentence Madlibs Pitch (+ Secret Sauce)** with zero buzzwords or superlatives.
   - **10-Word Headline Rule**: Every slide headline must be **10 words or fewer** and express a concrete takeaway (e.g., *"Clinics Lose \$4,200/Month To Unbilled Insurance Rejections"* instead of *"The Problem"*).
   - **Max 3 Bullets + 1-to-1 Mirror**: Problem and Solution slides each have at most 3 concise bullets, matched item-for-item in the exact same order.
   - **Radical Evidence Honesty**: Tag every real customer/revenue stat `[VALIDATED]` and every assumption `[HYPOTHESIS]` or `[TARGET]`. Never fabricate metrics.
   - **Bottom-Up Market Math**: Run `financial_calc(mode="tam_bottom_up")` before editing the Market slide.

3. **Customize Theme & Branding (Optional)**:
   Set `theme.preset` in `pitch-deck/deck.json` to one of `midnight-emerald`, `obsidian-gold`, `editorial-light`, or `cobalt-velocity`, or override any individual hex token (`bg`, `surface`, `text`, `muted`, `accent`, `accent2`, `border`).

4. **Lint & Compile**:
   - Call the `pitch_deck_build` MCP tool (or run `python3 ./scripts/build_deck.py pitch-deck/deck.json`).
   - Note: Editing `pitch-deck/deck.json` also triggers the `pitch-deck-auto-rebuild` PostToolUse hook automatically.
   - Review all `lint.issues` returned and fix every `error` and FI `warning` before handing back.

5. **Stress-Test & Rehearse**:
   - Delegate to the `fi-mentor-pitch-critic` subagent for a buzzword & clarity teardown, or `vc-lab-partner-skeptic` for an institutional due-diligence Q&A drill.
   - Remind the founder they can open `pitch-deck/index.html` in any browser and press:
     - `T` for the **3-minute FI Pitch Countdown Timer**
     - `S` for Speaker Notes
     - `G` for Slide Overview Grid
     - `B` to hide `[VALIDATED]`/`[HYPOTHESIS]` tags for clean investor mode
     - **Export PDF** (`Ctrl+P`) for a crisp 16:9 PDF deck

6. **Optional Designer-Grade Export (Canva, Figma Slides, or Replit Slides)**:
   - Call `pitch_deck_design_brief(target="all")` to generate `CANVA_DECK_BRIEF.md`, `FIGMA_SLIDES_BRIEF.md` + W3C `FIGMA_TOKENS.json`, and one-shot `REPLIT_SLIDES_BRIEF.md`.
   - Activate `design-studio-canva-figma` for **Canva** or **Figma Slides**, or `replit-launchpad` for **Replit Slides** (ideal if the founder is already building their Design System, Web/Mobile App, and Hosting all on Replit: https://replit.com/refer/peterbiggam).
