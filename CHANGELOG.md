# Changelog

All notable changes to **Startup Antigravity — Ethical Venture OS** are documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

## [0.0.1-alpha] - 2026-11-20

Initial Alpha release of **Startup Antigravity — Ethical Venture OS**, an **independent community plugin** created by a **Previous Founder Institute Director and Current Mentor & Advisor**. *(Note: This is not an official release of Founder Institute (`fi.co`), VC Lab, or Decile Group (`govclab.com`); it adapts proven frameworks inspired by those ecosystems for founders.)*

### Added
- **Plugin Bundle & Guardrails**: `plugin.json`, vector `assets/logo.svg`, and always-on Mensarius Oath + FI clarity + Revenue-First rules in `rules/AGENTS.md`.
- **Visual Interactive FI Pitch Deck 2.0**: Single-source-of-truth `deck.json` compiler (`build_deck.py`) producing zero-dependency 16:9 `index.html` (with 3-minute FI pitch timer `T`, speaker notes `S`, slide grid `G`, badge toggle `B`, 1-click PDF export) + Marp `DECK.md` + optional `.pptx`. Includes 3 templates (`problem-solution`, `traction`, 3-slide `teaser`) and inline SVG `chart-line`, `chart-bar`, `quadrant-2x2`, and `product-frame` slide types.
- **48-Hour Ethical Smoke-Test Landing Page Generator**: Zero-dependency `build_landing_page.py` + `landing_page_build` MCP tool generating a deploy-ready `landing/index.html` with interactive ROI calculator, transparent 3-tier pricing, For-Progress iKPI charter, and 1-page Paid-Pilot PACT intake.
- **12 Progressive-Disclosure Startup Skills**: `startup-kickstart`, `revenue-first-validation`, `pitch-deck-builder`, `design-studio-canva-figma`, `replit-launchpad`, `mvp-and-profit-architecture`, `market-and-unfair-moat`, `gtm-and-cash-velocity`, `unit-economics-and-profit-os`, `advisors-equity-and-fast`, `vc-lab-fundraising-os`, and `weekly-sprint-review`.
- **Replit Free-Tier Launchpad (Zero Double-Token Burn)**: Dedicated `replit-launchpad` skill + `replit_workspace_prepare` MCP tool scaffolding `.replit`, `replit.md` (no-double-token rules), `.env.example`, and `docs/REPLIT_HANDOFF.md` for starting in Replit Design Mode and launching Web (`web-node`, `web-python`) or Expo Mobile (`mobile-expo`) apps via GitHub sync without burning duplicate AI credits.
- **Canva, Figma Slides & Replit Slides Design Studio**: Zero-dependency `pitch_deck_design_brief` generator producing `CANVA_DECK_BRIEF.md`, `FIGMA_SLIDES_BRIEF.md`, W3C `FIGMA_TOKENS.json`, and one-shot `REPLIT_SLIDES_BRIEF.md` handoffs.
- **Creator's Recommended Founder Stack**: Personal founder endorsements integrated across skills & docs for **Founder Institute** (`fi.co` local, Silicon Valley & San Francisco chapters), **Replit** (`https://replit.com/refer/peterbiggam`), **Stripe Atlas** (Delaware C-Corp & 83(b) hygiene), and **QuickBooks Online** (investor-ready bookkeeping).
- **5 Founding Advisory Subagents**: `fi-mentor-pitch-critic`, `vc-lab-partner-skeptic`, `customer-revenue-coach`, `lean-cto-margin-architect`, and `ethical-growth-strategist`.
- **14-Tool Bundled Local MCP Server (`startup-antigravity-os`)**: Pure Python 3 standard library stdio JSON-RPC server covering state management, FI Madlibs & slide linting, Riskiest Assumption board, experiments, Mom Test interviews, Customer/Investor PACT pipeline, deterministic financial calculators (`runway`, `unit_economics`, `tam_bottom_up`, `safe_dilution`, `fast_advisor_equity`, `cap_table_model`), offline UN SDG 1–17 `ikpi_catalog_search` (34 metrics), weekly `sprint_manage` + `docs/INVESTOR_UPDATE.md` generator, `pitch_deck_build`, `pitch_deck_design_brief`, `landing_page_build`, and `replit_workspace_prepare`.
- **4 Lifecycle Hooks (`hooks.json`)**: `SessionStart` bootstrap/Founder Pulse, `PreToolUse` secret-leak blocker & early-stage infra guard, `PostToolUse` automatic pitch deck rebuild, and `Stop` JSON integrity check.
- **Cross-Platform Documentation & Test Suite**: Complete Windows (PowerShell/CMD/ZIP/Junction/WSL2), macOS, and Linux installation guide in `README.md`, release packager (`scripts/package_release.py`), and 22 automated unit/integration/contract tests.
