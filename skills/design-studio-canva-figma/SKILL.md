---
name: design-studio-canva-figma
description: >-
  Bridge Startup Antigravity's FI-linted pitch deck, landing page, and GTM launch kit
  directly into the official Canva (`canva_canva`) and Figma (`figma_figma`) companion
  plugins. Use whenever a founder wants to turn `pitch-deck/deck.json` into a designer-grade
  Canva presentation or native Figma Slides deck, generate Canva launch visuals, push
  `landing/index.html` into Figma, or convert Figma MVP wireframes into production code.
---

# Startup Design Studio (Canva & Figma Companion Bridge)

Startup Antigravity stays **100% zero-dependency** out of the box (generating instant interactive HTML5 SVG pitch decks and landing pages), and upgrades seamlessly into a full agency-grade design studio whenever the official **Canva** (`antigravity-plugins-partners/plugin/canva`) and/or **Figma** (`antigravity-plugins-partners/plugin/figma`) companion plugins are installed.

## Golden Rule: Strategy & FI Linting First, Visual Polish Second

Never polish weak, buzzword-filled copy in Canva or Figma. Always:
1. Run `fi_pitch_lint` on `pitch-deck/deck.json` first and resolve errors (<=10-word headlines, zero buzzwords, 1-to-1 Problem<->Solution mirror, `[VALIDATED]` vs `[HYPOTHESIS]` honesty).
2. Call `pitch_deck_design_brief(workspace_path=..., target="both")` to generate synchronized handoff files inside `pitch-deck/design-handoff/`:
   - `CANVA_DECK_BRIEF.md`
   - `FIGMA_SLIDES_BRIEF.md`
   - `FIGMA_TOKENS.json` (W3C color, typography, and 1920x1080 spacing tokens)

---

## Workflow A: Pitch Deck -> Designer-Grade Canva Presentation

*Requires the official **Canva** Marketplace plugin (`canva_canva` MCP tools).*

1. Generate the brief via `pitch_deck_design_brief(target="canva")` and read `pitch-deck/design-handoff/CANVA_DECK_BRIEF.md`.
2. Check existing founder branding via `canva_canva` -> `list-brand-kits` (use their Brand Kit colors/logo if available; otherwise apply the hex palette from `CANVA_DECK_BRIEF.md`).
3. Create the live 16:9 presentation using `canva_canva` -> `generate-design` or `create-design` with the exact linted slide structure and zero added fluff.
4. Load the `canva-edit-design` skill to refine individual slide headlines, KPI numbers, tables, and visual hierarchy cleanly.
5. Run `canva-brand-check` and `canva-design-feedback` to verify readability, whitespace, and brand consistency.
6. Export an investor-ready PDF or PowerPoint deck via `get-export-formats` + `export-design` (or share the live Canva edit URL).

---

## Workflow B: Pitch Deck -> Native Figma Slides Deck

*Requires the official **Figma** Marketplace plugin (`figma_figma` MCP tools).*

1. Generate the brief and tokens via `pitch_deck_design_brief(target="figma")` and read `FIGMA_SLIDES_BRIEF.md` + `FIGMA_TOKENS.json`.
2. **Mandatory prerequisite skills:** Load `figma-create-new-file`, `figma-use`, and `figma-use-slides` BEFORE calling `create_new_file` or `use_figma`.
3. Create a new **Figma Slides** file via `figma_figma` -> `create_new_file`.
4. Bind `FIGMA_TOKENS.json` into Figma Variables via `use_figma` so re-theming the entire deck takes one click.
5. Construct each 1920x1080 slide incrementally via `use_figma` using auto-layout frames, reusable KPI card components, and crisp vector paths for `chart-line`, `chart-bar`, and `quadrant-2x2` slides.
6. Verify visual fidelity with `figma_figma` -> `get_screenshot` to ensure zero clipping or overlapping text.

---

## Workflow C: GTM Launch Kit -> Canva Social & Product Hunt Assets

*Pairs `gtm-and-cash-velocity` with Canva MCP skills.*

1. Pull your linted FI One-Sentence Pitch, 3-tier value pricing, and For-Progress iKPI from `.startup/state.json`.
2. Build a master launch visual in Canva (`generate-design` / `create-design`) with zero dark patterns (no fake scarcity badges).
3. Load `canva-resize-for-social-media` to generate platform-ready variants for LinkedIn carousels, Product Hunt gallery slides, X/Twitter launch cards, and 1-page Customer Paid-Pilot PACT handouts.

---

## Workflow D: MVP & Landing Page <-> Figma Code Sync

*Pairs `mvp-and-profit-architecture` and `revenue-first-validation` with Figma MCP skills.*

- **Code -> Figma (Polish your 48-hour smoke-test landing page):** Generate `landing/index.html` via `landing_page_build`, then load `figma-generate-design` + `figma-use` to push the layout into editable Figma frames with `FIGMA_TOKENS.json` bindings.
- **Figma -> 7-Day Vertical Slice MVP Code:** When a founder already has Figma wireframes, load `figma-design-to-code` BEFORE calling `get_design_context`, then enforce our `mvp-and-profit-architecture` Cut-List so only the #1 paid vertical slice gets coded in Week 1.

---

## Graceful Fallback (When Canva / Figma Plugins Are Not Installed)

If `canva_canva` or `figma_figma` tools are not present in the session:
1. Still generate `pitch-deck/design-handoff/` (`CANVA_DECK_BRIEF.md`, `FIGMA_SLIDES_BRIEF.md`, `FIGMA_TOKENS.json`) so the founder can copy/paste or hand off immediately.
2. Keep using our zero-dependency interactive HTML5 SVG deck (`pitch-deck/index.html` with 1-click PDF export) and `landing/index.html`.
3. Suggest installing the official companion plugins from the Antigravity Marketplace (`antigravity-plugins-partners/plugin/canva` and `antigravity-plugins-partners/plugin/figma`) via `search_marketplace`.
