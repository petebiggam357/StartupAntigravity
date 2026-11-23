# Changelog

All notable changes to **Startup Antigravity — Ethical Venture OS** are documented in this file.

This project adheres to [Semantic Versioning](https://semver.org/).

## [0.4.2-beta] - 2026-11-22

Founder Studio & Mentor Portfolio UX polish release for **Startup Antigravity — Ethical Venture OS**.

### Added & Improved in 0.4.2-beta
- **Slide Reordering (`↑`/`↓`) & Quick Live Preview (`launcher/studio_server.py`)**: Reorder slides directly in the browser Visual Slide Editor and jump straight to the compiled deck with **View Live Deck**.
- **Weekly Rhythm Tab in Local Web Studio (`POST /api/weekly-rhythm`)**: Run **Monday Top-3 Focus** or **Friday Mentor Digest** right in the browser with 1-click **Copy Text** and **Download .md**.
- **1-Click "Cohort Portfolio" Button in Desktop Launcher GUI (`launcher/app.py`)**: FI Mentors, Directors, and Startup Grind Chapter leaders can pick a folder of mentee startups in the desktop app to generate & open `cohort-portfolio.html` with zero CLI commands.
- **1-Click Workspace Snapshot Export (`GET /api/export-snapshot`)**: Download a clean JSON backup of `.startup/*.json` + `pitch-deck/deck.json` straight from the Web Studio header.

## [0.4.1-beta] - 2026-11-22

Studio Wizard & Visual Slide Editor polish release for **Startup Antigravity — Ethical Venture OS**.

### Added & Improved in 0.4.1-beta
- **Live FI Madlibs Pitch Preview & Buzzword Detector (`launcher/studio_server.py`)**: Real-time one-sentence pitch preview inside the 90-Second Setup Wizard highlighting banned buzzwords (`revolutionary`, `disruptive`, `world-class`, `synergy`, etc.) as you type.
- **Inline Bullet Editing & + Add / Remove Slide (`launcher/studio_server.py`)**: Upgraded the Visual Pitch Deck Slide Editor so founders can edit bullets, add new slides, and remove slides right in the browser without touching JSON.
- **Complete 30-Tool `README.md` Sync & `/schedule` Recipe**: Listed `#29 weekly_rhythm_run` and `#30 publish_bundle_build` plus a copy-paste `/schedule` recipe for automated Monday Focus & Friday Investor Digests.

## [0.4.0-beta] - 2026-11-22

Zero-JSON Founder Studio, Mentor Cohort Portfolio Mode, Automated Weekly Rhythm, and 1-Click Publish Live milestone for **Startup Antigravity — Ethical Venture OS** (**20 skills · 9 subagents · 30 zero-dependency local MCP tools · 54+ resources · 10 global languages · 4 safety hooks**).

### Added in 0.4.0-beta
- **90-Second Zero-JSON Onboarding Wizard & Visual Pitch Deck Slide Editor (`launcher/studio_server.py`)**: Added **Setup Wizard** (`POST /api/onboard`) to generate a complete company OS from 5 plain-English inputs, plus a **Slide Editor** tab (`GET/POST /api/deck`) to edit headlines, speaker notes, and themes (`obsidian-gold`, `emerald-slate`, `paper-light`) with live FI linter scoring and 1-click recompilation.
- **Mentor & Accelerator Cohort Portfolio Mode (`launcher/portfolio.py` + `startup-antigravity --portfolio <DIR>`)**: Scans any folder of multiple startup workspaces, runs the 3-lens Board Review on each company, and compiles a single-file **Cohort Command Center (`cohort-portfolio.html`)** ranking every startup by FI stage, MRR, margin, PMF %, Board Score, ExO Quotient, and #1 bottleneck.
- **Automated Weekly Founder Rhythm (`weekly_rhythm_run` — 29th MCP Tool)**: Generates `docs/MONDAY_FOCUS.md` (Top 3 Revenue/PMF needle-movers) and `docs/FRIDAY_DIGEST.md` (`<150-word` mentor/investor update) — built to pair cleanly with `/schedule`.
- **1-Click Static Publish Live Packager (`publish_bundle_build` — 30th MCP Tool + Web Studio Button)**: Compiles a zero-config `publish/` bundle combining `landing/index.html`, `/deck/index.html`, optional `/data-room/`, `netlify.toml`, Cloudflare `_headers`, and `DEPLOY_NOW.md` for Netlify Drop, Cloudflare Pages, or GitHub Pages.

## [0.3.1-beta] - 2026-11-22

Pre-launch UX polish & documentation sync release for **Startup Antigravity — Ethical Venture OS**.

### Added & Improved in 0.3.1-beta
- **Interactive "What-If" Runway & Default-Alive Sliders (`build_dashboard.py`)**: Client-side sliders right inside the **Startup Command Center** (`dashboard/index.html`) for MoM Revenue Growth %, Extra Monthly Burn / Hiring, and Gross Margin % — recalculating Projected Month-12 MRR, Runway Months, and Default-Alive Month live.
- **10-Language Switcher in Investor Data Room (`build_data_room.py`)**: Added the synced 🌐 10-language switcher (+ automatic Arabic RTL) to `data-room/index.html`, completing 100% multilingual coverage across the Command Center, Web Studio, Data Room, and Public Showcase.
- **1-Click `.md` Report Downloads in Local Web Studio (`launcher/studio_server.py`)**: Added **Download .md** export buttons in the **Voice Coach**, **War Room**, and **Board Review** tabs.
- **Complete `README.md` Architecture Sync**: Updated all skill, subagent, and MCP tool tables to list all **20 skills**, **9 subagents**, **28 MCP tools**, **54+ resources**, and **10 global languages**.

## [0.3.0-beta] - 2026-11-22

Major feature leap for **Startup Antigravity — Ethical Venture OS** (**20 skills · 9 subagents · 28 zero-dependency local MCP tools · 54+ resources · 10 global languages · 4 hardened safety hooks**).

### Added in 0.3.0-beta
- **Live Voice Pitch Coach & VC Lab Partner Q&A Simulator (`voice_pitch_coach` — 26th MCP Tool + Web Studio Tab)**: Browser Web Speech API live microphone + 3-minute FI countdown timer (plus transcript fallback) scoring delivery pace (WPM), filler words, FI banned buzzwords, quantified proof, and clear Ask (`0–100`) alongside 5 tailored VC Lab / FI Partner grilling questions.
- **Autonomous 4-Executive Startup War Room (`war_room_run` — 27th MCP Tool + Web Studio Tab)**: Convenes 4 distinct executive lenses (**Lean CTO**, **Fractional CFO**, **PMF Truth Auditor**, **Exponential Growth Strategist**) on any strategic founder question using live `.startup/*.json` telemetry, surfacing consensus, tradeoffs, a unified decision, and `docs/WAR_ROOM_DECISION_MEMO.md`.
- **Live Metered x402 (HTTP 402) Agent Storefront (`launcher/x402_storefront.py` + Web Studio Tab + Command Center KPI)**: Exposes a live metered `POST /api/x402/agent-call` endpoint on `base-sepolia` testnet returning genuine `HTTP 402 Payment Required` challenges when unpaid and logging settled USDC micropayments into `.startup/x402_ledger.json`, streaming live agent calls & USDC revenue straight into the **Startup Command Center**.
- **Full Multilingual Support — Top 10 Global Founder Languages (`i18n/locales.json` + `i18n_locale_manage` — 28th MCP Tool)**: Instant zero-dependency localization across **English (`en`), Spanish (`es`), Chinese (`zh`), Hindi (`hi`), Arabic (`ar` with automatic RTL layout), Portuguese (`pt`), French (`fr`), German (`de`), Japanese (`ja`), and Korean (`ko`)** across the Startup Command Center, Local Web Studio, Public Showcase Site, and always-on Antigravity agent rules.

## [0.2.1-beta] - 2026-11-22

UX & diagnostics polish release for **Startup Antigravity — Ethical Venture OS**.

### Added & Improved in 0.2.1-beta
- **Interactive Web Studio Controls (`launcher/studio_server.py`)**: Added a dark-mode **Edit Metrics** modal (updates MRR, gross margin, cash, burn, and stage live), **Switch Workspace** control, and a live **3-Lens Board Review** tab (`GET /api/board-review`).
- **One-Command Preflight Diagnostics (`startup-antigravity --doctor`)**: Verifies Python 3.10+, plugin manifest, hooks, runs a live stdio JSON-RPC handshake confirming all **25 MCP tools**, and detects companion CLIs (`agy`, `git`, `gh`, `node`, `ollama`, `claude`, `codex`).
- **Startup Command Center ExO & 6Ds Card (`build_dashboard.py`)**: Surfaces the startup's **Massive Transformative Purpose (MTP)**, **ExO Quotient (`0–100`)**, and **6Ds Stage** directly inside `dashboard/index.html` alongside live MRR, PMF, and iKPI metrics (and unified flat/nested `state.json` + `pmf.json` loading).
- **Documentation Sync (`README.md`)**: Synced all Table of Contents, verification, and architecture counts to **20 skills, 9 subagents, 25 MCP tools, 54+ resources, and 4 safety hooks**.

## [0.2.0-beta] - 2026-11-22

Singularity & Exponential Thinking expansion for **Startup Antigravity — Ethical Venture OS** (**20 skills, 9 advisory subagents, 25 zero-dependency local MCP tools, 54 curated resources, 4 hardened safety hooks**, plus the researched **13-slide ClaimPulse Pre-Seed Demo Deck** scoring **100/100** on the FI linter and **Startup Command Center** branding).

### Added in 0.2.0-beta
- **20th Skill — `exponential-thinking-and-singularity`**: Adapts Singularity University (`su.org`) frameworks, Peter Diamandis's **6Ds of Exponentials**, Salim Ismail's **Exponential Organizations (ExO: MTP + SCALE + IDEAS)**, and Ray Kurzweil's **Law of Accelerating Returns** for revenue-first founders under Mensarius Oath ethics.
- **9th Advisory Subagent — `exponential-moonshot-strategist`**: Helps founders turn linear ideas into 10x ExO blueprints, sharpen *Why Now* inflection timing, and spot converging exponential curves without skipping customer proof.
- **25th MCP Tool — `exponential_audit`**: Deterministic engine supporting `exo_scorecard` (scores MTP + SCALE + IDEAS `0–100` and writes `docs/EXPONENTIAL_BLUEPRINT.md`), `six_ds_map` (maps industry on the 6Ds curve), and `accelerating_returns_sim` (models 12/24/36-month gross-margin expansion as AI inference costs fall).
- **6 New Curated Resources (`48 -> 54` in `mcp_server/founder_resources.json`)**: New **`exponential-singularity`** category covering Singularity University, 6Ds of Exponentials, Exponential Organizations (OpenExO), Ray Kurzweil's Law of Accelerating Returns, Abundance & Bold, and Converging Technologies Matrix.
- **Startup Command Center & Researched 13-Slide Demo Deck (`ClaimPulse`)**: Renamed dashboard branding to **Startup Command Center** and upgraded the live demo to a researched 13-slide Pre-Seed Traction deck with inline SVG line/bar charts, 2×2 competitive quadrant, and 100/100 FI linter readiness.

## [0.1.0-beta] - 2026-11-21

First Public Beta milestone of **Startup Antigravity — Ethical Venture OS** (**19 skills, 8 advisory subagents, 24 zero-dependency local MCP tools, 48 curated resources, 4 hardened safety hooks, unified local Web Studio, and native Linux/macOS/Windows desktop packages**).

### Added in 0.1.0-beta
- **23rd MCP Tool — Partner & Mentor Board Review Simulator (`board_review_run`)**: Deterministically audits `.startup/*.json` & `pitch-deck/` across 3 lenses (**FI Mentor**, **VC Lab Partner**, **PMF Truth Auditor**), scores each `1.0–5.0`, and writes `docs/BOARD_REVIEW_MEMO.md` with your top 3 prioritized 7-day fixes.
- **24th MCP Tool — Competitor Battlecard Engine (`competitor_manage`)**: Tracks structured competitors (pricing, ICP, strengths, weaknesses, 2x2 coordinates, FI Secret Sauce) in `.startup/competitors.json` and exports `docs/COMPETITOR_BATTLECARD.md`.
- **Live Metric Editor & Workspace Switcher in Local Web Studio (`launcher/studio_server.py`)**: Added `POST /api/metrics` (live updates `.startup/state.json` and instantly rebuilds Dashboard & Data Room) and `POST /api/workspace` (switch between multiple startup workspaces cleanly for mentors & serial founders).
- **1-Click SHA-256 Verified Self-Updater (`launcher/app.py --update`)**: Downloads the latest public GitHub Release `.zip`, verifies its SHA-256 digest against `SHA256SUMS.txt`, and installs in place.
- **Public Live Showcase & Badges**: Enabled live GitHub Pages (`https://petebiggam357.github.io/StartupAntigravity/`) with the interactive **SolarLedger** demo and added CI / Release / Live Demo badges to `README.md`.

## [0.0.5-alpha] - 2026-11-21

Public-launch & developer-experience milestone for **Startup Antigravity — Ethical Venture OS**, adding a unified local Web Studio, public GitHub Pages showcase + live interactive demo, runnable `x402` pay-per-call starter scaffolding, 1-click launcher update checks, and open-source community docs.

### Added in 0.0.5-alpha
- **Unified Local Web Studio (`launcher/studio_server.py` + `startup-antigravity --serve`)**: Zero-dependency local HTTP server (`127.0.0.1:4020`, path-traversal protected) uniting the **Founder Command Center**, **Interactive Pitch Deck**, **Investor Data Room**, **Smoke-Test Landing Page**, and **Live 48-Resource Search** in one auto-reloading dark-mode browser workspace.
- **Public GitHub Pages Showcase & Live Interactive Demo (`scripts/build_site.py` + `.github/workflows/pages.yml`)**: Automatically builds and deploys an OS-aware download page (`https://petebiggam357.github.io/StartupAntigravity/`) alongside a live hosted **SolarLedger** demo (Dashboard, Pitch Deck, Data Room & Landing Page).
- **Runnable x402 Pay-Per-Call Starter Scaffold (`ai_x402_calc(action="x402_starter_scaffold")`)**: Generates a zero-dependency runnable HTTP `402 Payment Required` starter (`x402-starter/` in `python-fastapi` or `node-express` flavors, defaulting safely to `base-sepolia` testnet with `.env.example` and a local handshake test client).
- **1-Click Update Checker in Desktop Launcher (`launcher/app.py` + `--check-update`)**: Read-only check against public GitHub Releases with graceful offline fallback and 1-click link to the latest release.
- **Open-Source Community & Trust Kit**: Added `CONTRIBUTING.md`, `SECURITY.md`, and `.github/ISSUE_TEMPLATE/` (`bug_report.md`, `feature_request.md`, `resource_submission.md`).

## [0.0.4-alpha] - 2026-11-21

AI-Forward & Programmable Finance expansion for **Startup Antigravity — Ethical Venture OS** (**19 skills, 8 founding advisory subagents, 22 zero-dependency local MCP tools, 48 curated founder resources, 4 lifecycle hooks**), equipping founders of every level for AI-native execution, `x402` agent micropayments, stablecoin rails, and compliant tokenization under Mensarius Oath ethics.

### Added in 0.0.4-alpha
- **19th Skill — `ai-native-and-x402-finance`**: All-level AI-forward playbook (Level 1 Non-Technical context engineering -> Level 2 Builder MCP/A2A, eval-driven shipping & `>=75%` AI gross-margin routing -> Level 3 Growth GEO/AEO search optimization) paired with `x402` HTTP 402 USDC micropayments, stablecoin treasury rails, and a ruthless "Do You Even Need a Token?" compliance gate.
- **8th Advisory Subagent — `ai-x402-finance-architect`**: Specialist architect for auditing LLM token COGS, designing MCP/A2A & `x402` pay-per-call endpoints, and stress-testing blockchain/RWA tokenization ideas against real utility and regulatory reality.
- **22nd MCP Tool — `ai_x402_calc`**: Deterministic engine supporting `ai_cogs_margin` (token routing + prompt caching vs 75% margin floor), `x402_micropayment_model` (legacy card `2.9% + $0.30` vs x402 USDC settlement + auto-generating `docs/X402_AGENT_MONETIZATION_SPEC.md`), and `tokenization_readiness` (ethical & Howey-awareness scorecard).
- **12 New Curated Founder Resources (`36 -> 48` in `mcp_server/founder_resources.json`)**: Added **`ai-native`** (6 all-level AI resources) and **`blockchain-x402`** (6 x402, USDC, Base, ERC-3643 RWA, and Mensarius token-ethics resources).
- **1-Click Starter Prompt Palette in Desktop Launcher (`launcher/app.py`)**: Pick any of 6 battle-tested Antigravity starter prompts (Day-0 Kickstart, AI Margin & x402 Audit, PMF Audit, Call Transcript Extractor, Pitch Deck Roast, Investor Data Room) and copy to clipboard in 1 click (or `--prompts` via CLI).
- **Hardened AI, x402 & Privacy Rules + Hooks (`rules/AGENTS.md`, `hooks/pre_tool_guard.py`, `hooks/post_deck_rebuild.py`, `hooks/stop_integrity_check.py`)**: Added Section 6 (AI `>=75%` margin floor, eval-before-ship, x402/token ethics, human-in-the-loop financial writes), blocked hardcoded wallet private keys & live API keys on `write_file`/`edit_file`, added mainnet broadcast confirmation & Data Room PII email guard, auto-synced `data-room/` on `.startup/` or `deck.json` edits, and added stale-artifact drift detection on `Stop`.

## [0.0.3-alpha] - 2026-11-21

Native desktop & compiled app package release for **Startup Antigravity — Ethical Venture OS**, making installation and launching your Founder Command Center & Pitch Deck a double-click experience on Linux, macOS, and Windows.

### Added in 0.0.3-alpha
- **Cross-Platform Desktop Launcher & Offline Installer (`launcher/app.py`)**: Zero-dependency dark-mode GUI (Tkinter) + full headless CLI (`--install`, `--uninstall`, `--status`, `--dashboard`, `--deck`, `--data-room`, `--demo`, `--version`) that bundles the complete Startup Antigravity plugin payload for 100% offline installation into `~/.gemini/config/plugins/startup-antigravity` and 1-click launching of `dashboard/index.html`, `pitch-deck/index.html`, `data-room/index.html`, or a live **Sample Startup Preview**.
- **1-Click Realistic Demo Startup Preview (`scripts/generate_demo_workspace.py`)**: Generates a complete FI-linted sample startup (**SolarLedger**) with `.startup/*.json` telemetry and compiles all 4 live visual artifacts (`dashboard/index.html`, `pitch-deck/index.html`, `landing/index.html`, and `data-room/index.html`) so founders can experience the full OS in 3 seconds.
- **One-Click Investor Data Room Builder (`data_room_build` MCP tool + `build_data_room.py`)**: 21st local MCP tool compiling `data-room/index.html`, `DATA_ROOM_INDEX.md`, an FI Executive One-Pager, Pitch Deck, Live Metrics Dashboard, PII-redacted Customer Proof, and a VC Lab / FI Diligence Readiness Checklist.
- **Native App Icon Pipeline (`scripts/generate_app_icons.py`)**: Generates multi-resolution Windows `.ico` and macOS `.icns` icons matching `assets/logo.svg` and embeds them into the compiled `.exe` and `.app`/`.dmg` bundles in GitHub Actions.
- **Native App Package Builder (`scripts/build_packages.py`)**: Builds universal `.zip` plugin bundles, native Debian / Ubuntu / Pop!_OS `.deb` packages (`startup-antigravity_0.0.3-alpha_all.deb` with desktop entry & SVG app icon), Freedesktop `StartupAntigravity.AppDir` / Linux x86_64 `.AppImage` bundles, and `SHA256SUMS.txt` integrity checksums.
- **Automated Multi-OS Release Pipeline (`.github/workflows/release.yml`)**: On every `v*` tag push, GitHub Actions compiles and publishes native packages across all 3 desktop platforms directly to the GitHub Release:
  - **Linux**: `StartupAntigravity-v0.0.3-alpha-x86_64.AppImage` (PyInstaller + `appimagetool`) + `startup-antigravity_0.0.3-alpha_all.deb`
  - **macOS**: `StartupAntigravity-v0.0.3-alpha-macos-arm64.dmg` (PyInstaller `.app` bundle + `hdiutil`)
  - **Windows**: `StartupAntigravity-v0.0.3-alpha-win64.exe` (PyInstaller single-file executable)
  - **Universal**: `startup-antigravity-v0.0.3-alpha.zip` + `SHA256SUMS.txt`

## [0.0.2-alpha] - 2026-11-21

Major Alpha expansion of **Startup Antigravity — Ethical Venture OS** (18 skills, 7 founding advisory subagents, 20 zero-dependency local MCP tools, 4 lifecycle hooks, live local Founder Command Center dashboard, one-command cross-platform installers, cross-platform GitHub Actions CI, and 36 curated founder resources).

### Added in 0.0.2-alpha
- **Live Local Founder Command Center (`founder_dashboard_build` + `build_dashboard.py`)**: Zero-dependency single-file executive browser dashboard (`dashboard/index.html`) visualizing FI stage progress, MRR/gross margin/Default-Alive runway, Sean Ellis 40% PMF SVG gauge + HXC segment table, Customer/Investor PACT pipeline, Riskiest Assumptions board, weekly sprints, and For-Progress iKPI progress—with automatic refresh in `hooks/post_deck_rebuild.py` whenever `.startup/*.json` changes.
- **One-Command Cross-Platform Installers (`install.sh` & `install.ps1`)**: Single-command setup for macOS, Linux, and Windows 10/11 (auto-checks Python 3.10+, auto-fixes Windows `python3.exe` alias gaps, supports `--symlink` / `-Junction`, and runs the full automated self-test suite).
- **Cross-Platform GitHub Actions CI (`.github/workflows/ci.yml`)**: Automatically runs the full test suite and release ZIP packager on `ubuntu-latest`, `macos-latest`, and `windows-latest` on every push and PR.
- **Raw Call-Transcript Mom Test Auto-Extractor (`transcript_ingest`)**: Parses pasted Zoom/Loom/Otter customer discovery transcripts to extract pain severity (1–5), dollar WTP mentions, current workarounds, pilot intent, top verbatim quotes, and Mom Test bias warnings—auto-logging directly into `.startup/interviews.json`.
- **Startup Grind & Founders Guild Community Integration**: Added **Startup Grind** (300+ global chapters, Startup Grind Global Conference pitch/exhibition floor, Startup Program & software perks — endorsed by the creator, former Startup Grind Monterey Bay Chapter Director) and **Founders Guild** (`foundersguild.org` — anti-gatekeeping builder community & founder durability hub) across `mcp_server/founder_resources.json`, `vc-lab-fundraising-os`, `founder-resources-library` (including Conference & Demo Day Event Battle Cards), and `README.md`.
- **On-Demand Founder Resources Library (`founder-resources-library` + `founder_resources_hub`)**: Offline catalog of 36 curated resources across 11 categories & all 5 FI stages, stage-matched Action Kits, and custom team/cohort bookmarks in `.startup/custom_resources.json`.
- **FI Alumni Scale Stack (`fi-alumni-scale-stack`)**: Integrated **Dipity Studio / Sera** (`docs/DIPITY_BRAND_BRAIN.md`, by FI Mentor & Grad Morgan Von Druitt) and **Shelled AI** (`docs/SHELLED_HANDOFF.md`, by FI Silicon Valley AI Grad Jacob Wellinghoff).
- **QuickBooks Online CFO Copilot & Zapier Hub (`quickbooks-cfo-and-zapier` + `cfo-bookkeeper-copilot`)**: Read-first accounting copilot supporting 1-click Zapier OAuth (9,000+ apps), Intuit's official QBO MCP Server, and `intuit-cli-for-quickbooks`.
- **Product-Market Fit Engine & Truth Auditor (`product-market-fit-engine` + `pmf-truth-auditor` + `pmf_engine_manage`)**: Sean Ellis 40% Very Disappointed rule, Superhuman HXC segmentation & 50/50 roadmap, cohort retention flattening, `docs/PMF_SCORECARD.md`, PMF rule guardrail, and live `SessionStart` telemetry.
- **Optional BYO-AI Connectors (`multi-ai-connectors` + `ai_connectors_manage`)**: Auto-detect CLIs & env vars (`claude`, `codex`, `xai/grok`, `gemini`, `ollama`, `intuit`, `shelled`, `dipity`), sync context files, and run multi-model second opinions.
- **Ethical Product Hunt Launch Engine (`product-hunt-launch` + `product_hunt_kit_build`)** & **Replit Free-Tier Launchpad (`replit-launchpad` + `replit_workspace_prepare`)** + **Canva/Figma/Replit Slides Design Studio (`design-studio-canva-figma` + `pitch_deck_design_brief`)**.

## [0.0.1-alpha] - 2026-11-20

Initial Alpha release of **Startup Antigravity — Ethical Venture OS**, an **independent community plugin** created by a **Previous Founder Institute Director and Current Mentor & Advisor**. *(Note: This is not an official release of Founder Institute (`fi.co`), VC Lab, or Decile Group (`govclab.com`); it adapts proven frameworks inspired by those ecosystems for founders.)*

### Added
- **Plugin Bundle & Guardrails**: `plugin.json`, vector `assets/logo.svg`, and always-on Mensarius Oath + FI clarity + Revenue-First rules in `rules/AGENTS.md`.
- **Visual Interactive FI Pitch Deck 2.0**: Single-source-of-truth `deck.json` compiler (`build_deck.py`) producing zero-dependency 16:9 `index.html` (with 3-minute FI pitch timer `T`, speaker notes `S`, slide grid `G`, badge toggle `B`, 1-click PDF export) + Marp `DECK.md` + optional `.pptx`. Includes 3 templates (`problem-solution`, `traction`, 3-slide `teaser`) and inline SVG `chart-line`, `chart-bar`, `quadrant-2x2`, and `product-frame` slide types.
- **48-Hour Ethical Smoke-Test Landing Page Generator**: Zero-dependency `build_landing_page.py` + `landing_page_build` MCP tool generating a deploy-ready `landing/index.html` with interactive ROI calculator, transparent 3-tier pricing, For-Progress iKPI charter, and 1-page Paid-Pilot PACT intake.
- **18 Progressive-Disclosure Startup Skills**: `startup-kickstart`, `revenue-first-validation`, `product-market-fit-engine`, `pitch-deck-builder`, `design-studio-canva-figma`, `replit-launchpad`, `product-hunt-launch`, `multi-ai-connectors`, `quickbooks-cfo-and-zapier`, `fi-alumni-scale-stack`, `founder-resources-library`, `mvp-and-profit-architecture`, `market-and-unfair-moat`, `gtm-and-cash-velocity`, `unit-economics-and-profit-os`, `advisors-equity-and-fast`, `vc-lab-fundraising-os`, and `weekly-sprint-review`.
- **On-Demand Founder Resources Library (`founder-resources-library`)**: Bundled offline catalog (`mcp_server/founder_resources.json` — 36 curated playbooks, templates, frameworks, books, communities & tools across 11 categories and all 5 FI stages, including **Startup Grind** global chapters / Global Conference / Startup Program and **Founders Guild** `foundersguild.org`) + `founder_resources_hub` MCP tool (`search`, stage-aware `stage_kit`, `categories`, and `save_custom` for team/cohort bookmarks in `.startup/custom_resources.json`) + Conference/Demo Day Event Battle Card workflow.
- **FI Alumni Scale Stack (`fi-alumni-scale-stack`)**: Integrated two Founder Institute alumni-built scaling platforms — **Dipity Studio / Sera** (`https://www.dipity.studio/dev-pages/documentation`, by FI Mentor & Grad Morgan Von Druitt) exporting `docs/DIPITY_BRAND_BRAIN.md` + `DIPITY_API_KEY` detection for authentic founder content distribution, and **Shelled AI** (`https://www.shelled.ai/`, by FI Silicon Valley AI Grad Jacob Wellinghoff) exporting `docs/SHELLED_HANDOFF.md` + `shelled` CLI / `SHELLED_API_KEY` detection for multi-agent engineering PR pods.
- **QuickBooks Online CFO Copilot & Zapier Automation Hub**: Dedicated `quickbooks-cfo-and-zapier` skill, 7th specialist subagent (`cfo-bookkeeper-copilot`), and `intuit` CLI auto-detection — supporting 1-click OAuth via the official **Zapier** Antigravity plugin (9,000+ apps), Intuit's official **QuickBooks Online MCP Server** (read-first default, 140+ tools), and `intuit-cli-for-quickbooks` with strict preview-before-write accounting guardrails.
- **Product-Market Fit (PMF) Engine & Truth Auditor**: Dedicated `product-market-fit-engine` skill, 6th specialist subagent (`pmf-truth-auditor`), `pmf_engine_manage` MCP tool (`.startup/pmf.json` tracking Sean Ellis's 40% Very Disappointed rule, per-segment Superhuman HXC discovery, 50/50 roadmap, cohort retention flattening, and `docs/PMF_SCORECARD.md`), PMF Guardrail in `rules/AGENTS.md`, and live PMF telemetry in `SessionStart` Founder Pulse.
- **Optional BYO-AI Addon Connectors (`multi-ai-connectors`)**: Antigravity-first hub (`ai_connectors_manage` MCP tool + zero-dependency `ai_connector.py`) detecting installed AI CLIs (`claude`, `codex`, `gemini`, `ollama`, `aider`, `intuit`) and API env vars (`XAI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY` without ever exposing key values), syncing universal workspace context files (`CLAUDE.md`, `docs/GROK_CONTEXT.md`, `docs/AI_CONTEXT_PACK.md`), and running optional multi-model second opinions.
- **Ethical Product Hunt Launch Engine**: Dedicated `product-hunt-launch` skill + `product_hunt_kit_build` MCP tool linting Product Hunt hard limits (`name<=40`, buzzword-free `tagline<=60`, `description<=260`, `topics<=3`) and generating `launch/product-hunt/PH_LAUNCH_KIT.md` (First Maker Comment, `1270x760` Canva/Figma gallery storyboard, ethical T-14 -> 12:01 AM PT launch runbook, zero upvote rings).
- **Replit Free-Tier Launchpad (Zero Double-Token Burn)**: Dedicated `replit-launchpad` skill + `replit_workspace_prepare` MCP tool scaffolding `.replit`, `replit.md` (no-double-token rules), `.env.example`, and `docs/REPLIT_HANDOFF.md` for starting in Replit Design Mode and launching Web (`web-node`, `web-python`) or Expo Mobile (`mobile-expo`) apps via GitHub sync without burning duplicate AI credits.
- **Canva, Figma Slides & Replit Slides Design Studio**: Zero-dependency `pitch_deck_design_brief` generator producing `CANVA_DECK_BRIEF.md`, `FIGMA_SLIDES_BRIEF.md`, W3C `FIGMA_TOKENS.json`, and one-shot `REPLIT_SLIDES_BRIEF.md` handoffs.
- **Creator's Recommended Founder Stack**: Personal founder endorsements integrated across skills & docs for **Founder Institute** (`fi.co` local, Silicon Valley & San Francisco chapters), **Replit** (`https://replit.com/refer/peterbiggam`), **Stripe Atlas** (Delaware C-Corp & 83(b) hygiene), and **QuickBooks Online** (investor-ready bookkeeping).
- **7 Founding Advisory Subagents**: `fi-mentor-pitch-critic`, `vc-lab-partner-skeptic`, `pmf-truth-auditor`, `cfo-bookkeeper-copilot`, `customer-revenue-coach`, `lean-cto-margin-architect`, and `ethical-growth-strategist`.
- **18-Tool Bundled Local MCP Server (`startup-antigravity-os`)**: Pure Python 3 standard library stdio JSON-RPC server covering state management, FI Madlibs & slide linting, Riskiest Assumption board, experiments, Mom Test interviews, Product-Market Fit engine (`pmf_engine_manage`), Customer/Investor PACT pipeline, deterministic financial calculators (`runway`, `unit_economics`, `tam_bottom_up`, `safe_dilution`, `fast_advisor_equity`, `cap_table_model`), offline UN SDG 1–17 `ikpi_catalog_search` (34 metrics), on-demand `founder_resources_hub` (32+ curated resources + custom bookmarks), weekly `sprint_manage` + `docs/INVESTOR_UPDATE.md` generator, `pitch_deck_build`, `pitch_deck_design_brief`, `landing_page_build`, `replit_workspace_prepare`, `product_hunt_kit_build`, and `ai_connectors_manage`.
- **4 Lifecycle Hooks (`hooks.json`)**: `SessionStart` bootstrap/Founder Pulse, `PreToolUse` secret-leak blocker & early-stage infra guard, `PostToolUse` automatic pitch deck rebuild, and `Stop` JSON integrity check.
- **Cross-Platform Documentation & Test Suite**: Complete Windows (PowerShell/CMD/ZIP/Junction/WSL2), macOS, and Linux installation guide in `README.md`, release packager (`scripts/package_release.py`), and 22 automated unit/integration/contract tests.
