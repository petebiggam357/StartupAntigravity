# Startup Antigravity — Ethical Venture OS

> **Build a high-margin, ethically grounded, fundable company from scratch inside Antigravity.**

**Startup Antigravity** (`startup-antigravity`) is a turnkey Antigravity plugin that fuses three proven startup engines into one cohesive bundle:

1. **Founder Institute (`fi.co`) Execution Engine** — FI One-Sentence Madlibs Pitch (+ Secret Sauce) linter, dual-mode FI Pitch Deck compiler (*Problem-Solution* & *Traction*), FI Funding Readiness milestones (`$1K–$10K` -> `$10K–$25K` -> `$25K–$200K+` MRR), **FAST Agreement** advisor equity math, and **For-Progress** Impact Thesis & iKPIs.
2. **VC Lab / Decile Group (`govclab.com`) Capital & Ethics Engine** — **Mensarius Oath** founder operating code baked into always-on guardrails, VC fund thesis reverse-engineering, and **PACT-style** written commitment pipelines (for both Customer Paid Pilots and Investor Soft-Circles).
3. **Rapid Ethical Profit Velocity** — *First Dollar in 7–14 Days*, value-based pricing, `>= 75%` gross margin architecture, and Default-Alive discipline with zero dark patterns.

---

## What's Inside the Bundle

### 1. Visual Interactive FI Pitch Deck 2.0 (`pitch-deck/`)
- Single source of truth in `pitch-deck/deck.json` (editable directly or via natural language).
- Supports zero-dependency **inline SVG charts** (`chart-line`, `chart-bar`), **2x2 competitive positioning quadrants** (`quadrant-2x2`), and **browser product mockups** (`product-frame`) alongside `cover`, `bullets`, `metrics`, `two-column`, `comparison`, and `ask`.
- Automatically compiles on every edit into:
  - **`pitch-deck/index.html`** — Zero-dependency 16:9 interactive web presentation with keyboard controls, Speaker Notes (`S`), Slide Grid (`G`), **3-Minute FI Pitch Countdown Timer (`T`)**, Evidence Badge Toggle (`B`), and **1-click Print-to-PDF**.
  - **`pitch-deck/DECK.md`** — Marp / Notion compatible Markdown export.
  - Optional `DECK.pptx` export when `python-pptx` is installed.
- Ships with **three FI & VC Lab templates**: `deck.problem-solution.json`, `deck.traction.json`, and 3-slide `deck.teaser.json`.

### 2. Ten Progressive-Disclosure Startup Skills (`skills/`)
| Skill | What It Does |
| :--- | :--- |
| `startup-kickstart` | 5-question Day-0 intake that drafts & lints your FI One-Sentence Pitch, picks an UN SDG iKPI, and scaffolds `.startup/`, `docs/`, and `pitch-deck/` |
| `revenue-first-validation` | Mom Test discovery scripts, RAT experiments, 1-page Customer Paid-Pilot PACTs, and a **48-hour deploy-ready smoke-test landing page generator** (`landing/index.html`) |
| `pitch-deck-builder` | Create, edit, re-theme, switch modes (`problem-solution` / `traction` / `teaser`), add SVG charts & 2x2 quadrants, lint against FI rules, and compile |
| `mvp-and-profit-architecture` | 7-day vertical slice MVP spec, explicit *NOT-Building-Yet* Cut-List, and `>= 75%` gross margin architecture |
| `market-and-unfair-moat` | Deterministic bottom-up TAM/SAM/SOM sizing, competitive teardowns, Why-Now analysis, and Secret Sauce audit |
| `gtm-and-cash-velocity` | Value-based pricing (10x ROI), ethical cold outreach, Show HN / Product Hunt launches, and first-100-customers loops |
| `unit-economics-and-profit-os` | Default-Alive runway modeling, CAC/LTV/Payback, North Star metrics, and FI Funding Readiness stage scoring |
| `advisors-equity-and-fast` | Founder Institute **FAST Agreement** advisor equity calculator, trial cliffs, and co-founder vesting hygiene |
| `vc-lab-fundraising-os` | VC fund thesis mapping, PACT soft-circle pipeline, multi-round cap table & SAFE dilution modeling, Data Room checklist, and partner Q&A |
| `weekly-sprint-review` | FI weekly sprint accountability (`.startup/sprints.json`, 1.0–5.0 velocity scoring) and 1-click **VC Lab Monthly Investor Update** generator (`docs/INVESTOR_UPDATE.md`) |

### 3. Five Specialist Advisory Subagents (`agents/`)
- **`fi-mentor-pitch-critic`** — Tough FI Mentor who shreds buzzwords, grades slides 1.0–5.0, and sets 7-day sprints.
- **`vc-lab-partner-skeptic`** — Mensarius-bound VC Lab GP who audits fundability, math, moat, and runs 10-question partner drills.
- **`customer-revenue-coach`** — *Mom Test* & paid-pilot coach who role-plays skeptical buyers and logs discovery proof.
- **`lean-cto-margin-architect`** — Pragmatic founding CTO who cuts scope 50–70% and protects `>= 75%` gross margins.
- **`ethical-growth-strategist`** — Value-pricing and ethical acquisition strategist (zero dark patterns).

### 4. Zero-Dependency Local MCP Server (`startup-antigravity-os` — 12 Tools)
Pure Python 3 standard library (no `npm install`, no `pip install`, no external API keys required):
- `startup_get_state` / `startup_update_stage`
- `fi_pitch_lint` (Madlibs + Secret Sauce + FI slide linter)
- `assumption_manage` (Impact x Uncertainty risk board)
- `experiment_manage` (Pre-committed pass/fail experiments)
- `interview_manage` (Structured discovery proof & WTP stats)
- `pact_pipeline_manage` (Customer Pilot & Investor Soft-Circle PACTs)
- `financial_calc` (`runway`, `unit_economics`, `tam_bottom_up`, `safe_dilution`, `fast_advisor_equity`, **`cap_table_model`**)
- `pitch_deck_build` (Lint + compile interactive SVG HTML & Markdown deck)
- `landing_page_build` (Compile 48-hour ethical smoke-test landing page with interactive ROI calculator & PACT intake)
- `ikpi_catalog_search` (Offline FI *For-Progress* UN SDG 1–17 iKPI catalog with 34 concrete metrics)
- `sprint_manage` (FI weekly sprint accountability + VC Lab `docs/INVESTOR_UPDATE.md` generator)

### 5. Always-On Guardrails (`rules/AGENTS.md`) & 4 Lifecycle Hooks (`hooks.json`)
- **`SessionStart`**: Detects uninitialized folders (offers `startup-kickstart`) or injects a 4-line live Founder Pulse (FI stage, MRR, PACTs, top untested risk, For-Progress iKPI).
- **`PreToolUse`**: Blocks accidental Git commits of `.env`/keys/PII (`deny`) and nudges before heavy cluster infra (`terraform`/`kubectl`/`helm`) during `idea`/`validation` stages (`ask`).
- **`PostToolUse`**: Automatically recompiles `pitch-deck/index.html` and `pitch-deck/DECK.md` whenever `pitch-deck/deck.json` is edited.
- **`Stop`**: Verifies `.startup/state.json` and `pitch-deck/deck.json` remain valid JSON before ending a turn.

---

## Installation (Antigravity)

### Option A: Global Plugin Install (Recommended)
Clone or symlink this repository into Antigravity's global plugins directory:

```bash
git clone https://github.com/petebiggam357/StartupAntigravity.git ~/.gemini/config/plugins/startup-antigravity
```

Antigravity automatically discovers the plugin on the next turn — no restart required.

### Option B: Workspace-Scoped Plugin
Place this folder under `.agents/plugins/startup-antigravity` inside any repository.

---

## Starter Prompts

Once installed, open any new folder in Antigravity and try:

1. *"Kickstart my new startup idea with an FI One-Sentence Pitch, 14-day first-dollar plan, and pitch deck"*
2. *"Critique my pitch deck like a Founder Institute Mentor and VC Lab Partner and rebuild the slides"*
3. *"Model our unit economics, runway, FAST advisor equity, and bottom-up TAM"*

---

## Running Tests

Requires only Python 3.10+:

```bash
python3 -m unittest discover -s tests -v
```

---

## License

MIT — see [LICENSE](./LICENSE). Legal, equity (FAST/SAFE), and tax templates included in this plugin are educational operational frameworks; always confirm binding documents with qualified startup counsel.
