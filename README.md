# Startup Antigravity — Ethical Venture OS

> **Install one Antigravity plugin, open an empty folder, and build a high-margin, ethically grounded, fundable company from scratch.**

> **Independence & Attribution Notice:** **Startup Antigravity** is an **independent, community-built plugin** created by a **Previous Founder Institute Director and Current Mentor & Advisor**. It is **not** an official product, endorsement, or release of Founder Institute (`fi.co`), VC Lab, or Decile Group (`govclab.com`). All references to Founder Institute and VC Lab / Decile Group methodologies (such as the One-Sentence Pitch, FAST Agreement benchmarks, For-Progress iKPIs, Mensarius Oath, and PACT frameworks) are educational adaptations inspired by those ecosystems.

**Startup Antigravity** (`startup-antigravity`) is a turnkey Founder Operating System for **Google Antigravity** (Antigravity 2.0 App, Antigravity IDE, and `agy` CLI) that fuses three battle-tested venture frameworks into one zero-dependency bundle:

1. **Founder Institute (`fi.co`) Execution Engine** — FI One-Sentence Madlibs Pitch (+ Secret Sauce) linter, triple-mode FI Pitch Deck compiler (*Problem-Solution*, *Traction*, and *3-Slide Teaser*), FI Funding Readiness milestones (`$1K–$10K` -> `$10K–$25K` -> `$25K–$200K+` MRR), **FAST Agreement** advisor equity math, Weekly Sprint accountability, and **For-Progress** UN SDG 1–17 Impact KPIs (`iKPIs`).
2. **VC Lab / Decile Group (`govclab.com`) Capital & Ethics Engine** — **Mensarius Oath** founder operating code baked into always-on guardrails, VC fund thesis reverse-engineering, **PACT-style** written commitment pipelines (for both Customer Paid Pilots and Investor Soft-Circles), and 60-second Monthly Investor Updates.
3. **Rapid Ethical Profit Velocity** — *First Dollar in 7–14 Days*, 48-hour deploy-ready smoke-test landing pages with interactive ROI calculators, value-based pricing, `>= 75%` gross margin architecture, and Default-Alive discipline with **zero dark patterns**.

---

## Table of Contents

- [Prerequisites (All Operating Systems)](#prerequisites-all-operating-systems)
- [Install Location Quick Reference](#install-location-quick-reference)
- [Installing on macOS (Apple Silicon & Intel)](#installing-on-macos-apple-silicon--intel)
- [Installing on Linux (Ubuntu, Pop!_OS, Fedora, Arch)](#installing-on-linux-ubuntu-pop_os-fedora-arch)
- [Installing on Windows 10 & 11 (PowerShell, CMD, ZIP & WSL2)](#installing-on-windows-10--11-powershell-cmd-zip--wsl2)
- [Team / Workspace-Scoped Install (Share via Git)](#team--workspace-scoped-install-share-via-git)
- [Verifying Your Installation](#verifying-your-installation)
- [Updating & Uninstalling](#updating--uninstalling)
- [Quickstart: Your First 30 Minutes](#quickstart-your-first-30-minutes)
- [What's Inside the Plugin](#whats-inside-the-plugin)
  - [1. Visual Interactive FI Pitch Deck 2.0](#1-visual-interactive-fi-pitch-deck-20)
  - [2. Companion Design, Cloud & Ops Stack (Canva, Figma, Replit, QuickBooks & Zapier)](#2-companion-design-cloud--ops-stack-canva-figma-replit-quickbooks--zapier)
  - [3. Eighteen Progressive-Disclosure Startup Skills](#3-eighteen-progressive-disclosure-startup-skills)
  - [4. Seven Founding Advisory Subagents](#4-seven-founding-advisory-subagents)
  - [5. Eighteen-Tool Local MCP Server (`startup-antigravity-os`)](#5-eighteen-tool-local-mcp-server-startup-antigravity-os)
  - [6. Optional BYO-AI Addon Connectors (Claude, OpenAI, xAI Grok, Gemini CLI & Ollama)](#6-optional-byo-ai-addon-connectors-claude-openai-xai-grok-gemini-cli--ollama)
  - [7. Always-On Guardrails & Four Lifecycle Hooks](#7-always-on-guardrails--four-lifecycle-hooks)
- [Creator's Recommended Founder Stack (Personal Endorsements)](#creators-recommended-founder-stack-personal-endorsements)
- [Troubleshooting (Windows, macOS & Linux)](#troubleshooting-windows-macos--linux)
- [License & Legal Notice](#license--legal-notice)

---

## Prerequisites (All Operating Systems)

Startup Antigravity is engineered for **zero external dependencies** — no `npm install`, no `pip install`, no virtual environments, and no paid API keys required to run the full operating system.

| Requirement | Minimum Version | Why It's Needed |
| :--- | :--- | :--- |
| **Google Antigravity** | Antigravity 2.0 App, Antigravity IDE, or `agy` CLI | Hosts the plugin, skills, subagents, rules, hooks, and MCP server |
| **Python 3** | **3.10+** (standard library only) | Powers the local `startup-antigravity-os` MCP server, lifecycle hooks, pitch deck compiler, and landing page builder |
| **Git** *(optional)* | Any modern version | Recommended for 1-command install and `git pull` updates (ZIP download also supported) |

> **Optional PowerPoint Export:** If you also want native `.pptx` exports alongside interactive HTML5 & 1-click PDF decks, install `python-pptx` once via `pip install python-pptx`. Everything else works out of the box without it.

---

## Install Location Quick Reference

Antigravity automatically discovers any plugin folder containing a valid `plugin.json` placed in either your **Global** or **Workspace** plugins directory:

| OS | Global Install Path *(Recommended — Active in All Projects)* | Workspace Install Path *(Single Repo / Team Shared)* |
| :--- | :--- | :--- |
| **macOS** | `~/.gemini/config/plugins/startup-antigravity` | `<your-project>/.agents/plugins/startup-antigravity` |
| **Linux** | `~/.gemini/config/plugins/startup-antigravity` | `<your-project>/.agents/plugins/startup-antigravity` |
| **Windows (PowerShell)** | `$env:USERPROFILE\.gemini\config\plugins\startup-antigravity` | `<your-project>\.agents\plugins\startup-antigravity` |
| **Windows (CMD)** | `%USERPROFILE%\.gemini\config\plugins\startup-antigravity` | `<your-project>\.agents\plugins\startup-antigravity` |

> **Important Directory Check:** Make sure `plugin.json` sits **directly inside** `startup-antigravity/plugin.json` — NOT nested inside a double folder like `startup-antigravity/StartupAntigravity-main/plugin.json`.

---

## Installing on macOS (Apple Silicon & Intel)

### Step 1: Verify Python 3 and Git
Open **Terminal** (`Cmd + Space` -> type `Terminal`) and run:

```bash
python3 --version
git --version
```

- You should see `Python 3.10.x` or higher.
- If macOS prompts to install **Command Line Developer Tools**, click **Install** (or install Python 3 via [Homebrew](https://brew.sh): `brew install python git`).

### Step 2: Install the Plugin Globally

#### Method A — Clone via Git (Recommended)
```bash
mkdir -p ~/.gemini/config/plugins
git clone https://github.com/petebiggam357/StartupAntigravity.git ~/.gemini/config/plugins/startup-antigravity
```

*(If this repository is private, authenticate once via `gh auth login` or clone using SSH: `git clone git@github.com:petebiggam357/StartupAntigravity.git ~/.gemini/config/plugins/startup-antigravity`.)*

#### Method B — Download ZIP (No Git Needed)
1. Download the repository ZIP from GitHub and unzip it.
2. Rename the extracted folder to `startup-antigravity`.
3. Move it into `~/.gemini/config/plugins/` via Terminal:
   ```bash
   mkdir -p ~/.gemini/config/plugins
   mv ~/Downloads/startup-antigravity ~/.gemini/config/plugins/startup-antigravity
   ```

#### Method C — Developer Symlink (If Editing the Repo Locally)
```bash
mkdir -p ~/.gemini/config/plugins
ln -sfn /path/to/your/StartupAntigravity ~/.gemini/config/plugins/startup-antigravity
```

### Step 3: Activate in Antigravity
1. Open Antigravity (no full app restart needed).
2. Open **Customizations > Plugins** and confirm **Startup Antigravity — Ethical Venture OS** is listed and toggled **On**.
3. Open **Additional Options (`...`) > MCP Servers** and click **Refresh** (or open a **new conversation**) so all 12 `startup-antigravity-os` MCP tools bind cleanly.

---

## Installing on Linux (Ubuntu, Pop!_OS, Fedora, Arch)

### Step 1: Verify Python 3 and Git
Open your terminal and run:

```bash
python3 --version
git --version
```

If either is missing:
- **Ubuntu / Pop!_OS / Debian:** `sudo apt update && sudo apt install -y python3 git`
- **Fedora:** `sudo dnf install -y python3 git`
- **Arch / Manjaro:** `sudo pacman -S python git`

### Step 2: Install the Plugin Globally

#### Method A — Clone via Git (Recommended)
```bash
mkdir -p ~/.gemini/config/plugins
git clone https://github.com/petebiggam357/StartupAntigravity.git ~/.gemini/config/plugins/startup-antigravity
```

#### Method B — Developer Symlink (Live Reload While Editing)
```bash
mkdir -p ~/.gemini/config/plugins
ln -sfn "$HOME/Documents/StartupAntigravity" ~/.gemini/config/plugins/startup-antigravity
```

#### Method C — Download ZIP (No Git Needed)
```bash
mkdir -p ~/.gemini/config/plugins
unzip ~/Downloads/StartupAntigravity-main.zip -d /tmp/sa_unpack
mv /tmp/sa_unpack/StartupAntigravity-main ~/.gemini/config/plugins/startup-antigravity
```

### Step 3: Ensure Scripts Are Executable (Optional Safety Step)
```bash
chmod +x ~/.gemini/config/plugins/startup-antigravity/mcp_server/server.py \
         ~/.gemini/config/plugins/startup-antigravity/hooks/*.py \
         ~/.gemini/config/plugins/startup-antigravity/skills/pitch-deck-builder/scripts/build_deck.py \
         ~/.gemini/config/plugins/startup-antigravity/skills/startup-kickstart/scripts/scaffold_startup.py \
         ~/.gemini/config/plugins/startup-antigravity/skills/revenue-first-validation/scripts/build_landing_page.py
```

### Step 4: Activate in Antigravity
Open **Customizations > Plugins** to confirm **Startup Antigravity — Ethical Venture OS** is enabled, then start a **new conversation** (or click **Refresh** under **MCP Servers**).

---

## Installing on Windows 10 & 11 (PowerShell, CMD, ZIP & WSL2)

### Step 1: Install Python 3 and Ensure `python3` Works (Critical Windows Step!)

Because this plugin's `mcp_config.json` and `hooks.json` invoke `python3`, verify that `python3` runs real Python rather than opening the Microsoft Store:

1. Open **PowerShell** and run:
   ```powershell
   python3 --version
   ```
2. **If `Python 3.10+` prints:** You are ready for Step 2!
3. **If Microsoft Store pops up or `python3` is not recognized:**
   - Install Python 3.12 via `winget` (or from [python.org/downloads](https://www.python.org/downloads/) — check **"Add python.exe to PATH"** during setup):
     ```powershell
     winget install --id Python.Python.3.12 -e --source winget
     ```
   - Open **Windows Settings > Apps > Advanced app settings > App execution aliases** and toggle **OFF** both `python.exe` and `python3.exe` (App Installer stubs).
   - Open a **new** PowerShell window, find where `python.exe` is installed, and create a `python3.exe` copy right beside it if `python3 --version` still isn't found:
     ```powershell
     $pyPath = (Get-Command python).Source
     $pyDir = Split-Path $pyPath
     if (-not (Test-Path "$pyDir\python3.exe")) {
       Copy-Item $pyPath "$pyDir\python3.exe"
     }
     python3 --version
     ```

### Step 2: Install the Plugin Globally

#### Method A — PowerShell + Git (Recommended)
```powershell
$pluginRoot = "$env:USERPROFILE\.gemini\config\plugins"
New-Item -ItemType Directory -Force -Path $pluginRoot | Out-Null
git clone https://github.com/petebiggam357/StartupAntigravity.git "$pluginRoot\startup-antigravity"
```

#### Method B — Command Prompt (CMD)
```cmd
mkdir "%USERPROFILE%\.gemini\config\plugins"
git clone https://github.com/petebiggam357/StartupAntigravity.git "%USERPROFILE%\.gemini\config\plugins\startup-antigravity"
```

#### Method C — ZIP Download (Zero Git Needed)
1. Download the repository ZIP from GitHub and extract it.
2. Press `Win + R`, paste `%USERPROFILE%\.gemini\config`, and press **Enter** (create the `plugins` folder inside if it does not exist).
3. Move the extracted folder into `%USERPROFILE%\.gemini\config\plugins\` and rename it to `startup-antigravity`.
4. Open the folder and verify you see `plugin.json` right at the top level (`%USERPROFILE%\.gemini\config\plugins\startup-antigravity\plugin.json`).

#### Method D — Windows Developer Junction (No Admin Privileges Required!)
If you cloned the repo into `C:\Users\<You>\Documents\StartupAntigravity` and want live updates without copying files:
```cmd
mkdir "%USERPROFILE%\.gemini\config\plugins"
mklink /J "%USERPROFILE%\.gemini\config\plugins\startup-antigravity" "%USERPROFILE%\Documents\StartupAntigravity"
```

#### Method E — WSL2 Users
- If **Antigravity runs natively on Windows**, install into Windows' `%USERPROFILE%\.gemini\config\plugins\startup-antigravity` (Methods A–D above).
- If you run **Antigravity CLI (`agy`) inside WSL2 Linux**, install inside your Linux home directory (`~/.gemini/config/plugins/startup-antigravity`) using the [Linux steps](#installing-on-linux-ubuntu-pop_os-fedora-arch).

### Step 3: Activate in Antigravity
1. Open Antigravity and go to **Customizations > Plugins**.
2. Confirm **Startup Antigravity — Ethical Venture OS** is **On**.
3. Open **Additional Options (`...`) > MCP Servers** -> click **Refresh** (or open a **new conversation**).

---

## Team / Workspace-Scoped Install (Share via Git)

Want every co-founder or cohort member who clones your company repo to automatically get Startup Antigravity?

Add it directly inside your project's `.agents/plugins/` folder:

**macOS / Linux:**
```bash
mkdir -p .agents/plugins
git clone https://github.com/petebiggam357/StartupAntigravity.git .agents/plugins/startup-antigravity
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path ".agents\plugins" | Out-Null
git clone https://github.com/petebiggam357/StartupAntigravity.git ".agents\plugins\startup-antigravity"
```

---

## Verifying Your Installation

### 1. Run the Built-In Automated Self-Test (All 29 Checks)

**macOS / Linux:**
```bash
cd ~/.gemini/config/plugins/startup-antigravity
python3 -m unittest discover -s tests -v
```

**Windows (PowerShell):**
```powershell
cd "$env:USERPROFILE\.gemini\config\plugins\startup-antigravity"
python3 -m unittest discover -s tests -v
```

Expected result: **`Ran 29 tests ... OK`** (under 1 second).

### 2. Verify Inside Antigravity
1. **Customizations > Plugins:** You should see **Startup Antigravity — Ethical Venture OS (`v0.0.1-alpha`)** enabled with **18 skills**, **7 agents**, **1 rule file**, **4 hooks**, and **1 MCP server**.
2. **Additional Options (`...`) > MCP Servers:** Confirm `startup-antigravity_startup-antigravity-os` shows as connected with **18 tools**.
3. **Antigravity CLI (optional):**
   ```bash
   agy plugin enable startup-antigravity
   ```

---

## Updating & Uninstalling

### Update to the Latest Version
- **macOS / Linux:**
  ```bash
  git -C ~/.gemini/config/plugins/startup-antigravity pull origin main
  ```
- **Windows (PowerShell):**
  ```powershell
  git -C "$env:USERPROFILE\.gemini\config\plugins\startup-antigravity" pull origin main
  ```
  Then click **Refresh** under **MCP Servers** (or start a new conversation) to pick up any newly added MCP tools.

### Temporarily Disable
Toggle **Startup Antigravity — Ethical Venture OS** off in **Customizations > Plugins** (or run `agy plugin disable startup-antigravity`). Takes effect live with no restart.

### Completely Uninstall
- **macOS / Linux:** `rm -rf ~/.gemini/config/plugins/startup-antigravity`
- **Windows (PowerShell):** `Remove-Item -Recurse -Force "$env:USERPROFILE\.gemini\config\plugins\startup-antigravity"`

---

## Quickstart: Your First 30 Minutes

1. **Create a brand-new empty folder** for your company (e.g., `MyStartup`) and open it in Antigravity.
2. **Start a new chat** — the `SessionStart` hook automatically detects an uninitialized workspace and cues `startup-kickstart`.
3. **Try these starter prompts in order:**
   - **Minute 1 (Kickstart):**
     > *"Kickstart my new startup idea with an FI One-Sentence Pitch, UN SDG For-Progress iKPI, 14-day first-dollar plan, and pitch deck."*
   - **Minute 10 (48-Hour Revenue Smoke Test):**
     > *"Build our 48-hour ethical smoke-test landing page with interactive ROI calculator and Paid-Pilot PACT intake."*
   - **Minute 15 (Mentor & VC Stress Test):**
     > *"Have the FI Mentor and VC Lab Partner critique my pitch deck, then add an MRR line chart and 2x2 competitive quadrant and rebuild the slides."*
   - **Minute 20 (Deterministic Economics & Equity):**
     > *"Model our bottom-up TAM, Default-Alive runway, a Strategic Idea-stage FI FAST advisor grant, and a full multi-round cap table through Seed."*
   - **Every Friday (Accountability):**
     > *"Close this week's FI sprint, score our velocity, start next week's sprint, and generate our VC Lab monthly investor update."*
     *(Pairs cleanly with Antigravity's `/schedule` command!)*

### What Gets Created Inside Your Startup Workspace
```text
MyStartup/
├── .startup/
│   ├── state.json            # FI stage, linted pitch, MRR, burn, cash, gross margin, iKPI
│   ├── assumptions.json      # Riskiest Assumptions ranked by Impact x Uncertainty
│   ├── experiments.json      # Pre-committed pass/fail validation experiments
│   ├── interviews.json       # Structured Mom Test discovery notes & WTP signals
│   ├── pacts.json            # Customer Paid-Pilot PACTs & Investor Soft-Circle PACTs
│   └── sprints.json          # Weekly FI execution sprints & 1.0–5.0 velocity scores
├── docs/
│   ├── ONE_PAGER.md          # Lean Canvas + FI Pitch + 14-Day First-Dollar Plan
│   ├── ETHICS_AND_IKPI.md    # Mensarius Ethical Charter & For-Progress iKPI
│   ├── DISCOVERY_SCRIPT.md   # Unbiased Mom Test buyer interview script
│   ├── MVP_SPEC.md           # 7-day vertical slice + NOT-Building-Yet Cut-List
│   └── INVESTOR_UPDATE.md    # Auto-compiled VC Lab / FI monthly update
├── pitch-deck/
│   ├── deck.json             # Editable single source of truth
│   ├── index.html            # Self-contained 16:9 interactive web deck + 1-click PDF
│   └── DECK.md               # Marp / Notion compatible Markdown export
└── landing/
    ├── landing.json          # Editable pricing, ROI defaults & copy
    └── index.html            # Deploy-ready single-file smoke-test landing page
```

---

## What's Inside the Plugin

### 1. Visual Interactive FI Pitch Deck 2.0
- **Three Built-In Modes:**
  1. `problem-solution` (`deck.problem-solution.json`) — FI 12-slide Problem↔Solution 1-to-1 mirror deck.
  2. `traction` (`deck.traction.json`) — Investor Traction deck leading with revenue velocity, `product-frame` mockup, and `quadrant-2x2` moat map.
  3. `teaser` (`deck.teaser.json`) — 3-slide VC Lab cold-intro teaser with inline SVG MRR chart.
- **Ten Supported Slide Types:** `cover`, `bullets`, `metrics`, `two-column`, `comparison`, `ask`, plus zero-dependency SVG/HTML visual types `chart-line`, `chart-bar`, `quadrant-2x2`, and `product-frame`.
- **Four Built-In Theme Presets:** `midnight-emerald`, `obsidian-gold`, `editorial-light`, `cobalt-velocity` (or custom hex colors).
- **Interactive Browser Controls (`pitch-deck/index.html`):**
  - `←` / `→` or `Space` — Navigate slides
  - `T` — Start/reset the built-in **3-minute FI Pitch Countdown Timer**
  - `S` — Toggle Speaker Notes drawer
  - `G` — Open Slide Overview Grid
  - `B` — Toggle `[VALIDATED]` / `[HYPOTHESIS]` / `[TARGET]` badges (hide for clean investor mode)
  - **Export PDF** (`Ctrl+P` / `Cmd+P`) — Crisp 16:9 slide-per-page PDF export

### 2. Companion Design, Cloud & Ops Stack (Canva, Figma, Replit, QuickBooks & Zapier)
Startup Antigravity works 100% offline with zero dependencies, and pairs seamlessly with five powerhouse companion platforms:
- **Replit Free-Tier Launchpad (Zero Double-Token Burn — https://replit.com/refer/peterbiggam):** Start visually in **Replit Design Mode** to shape your living design system, do heavy coding locally in **Antigravity** (avoiding duplicate AI token charges), and sync via private GitHub (`replit_workspace_prepare`) to run full-stack **Web Platforms** (`web-node`, `web-python`), **Expo / React Native Mobile Apps** (instant QR testing via Expo Go), managed DB/Secrets, 1-click hosting, and one-shot **Replit Slides** (`REPLIT_SLIDES_BRIEF.md`) all in one place.
- **Canva (`antigravity-plugins-partners/plugin/canva`):** Run `pitch_deck_design_brief(target="canva")` to export `CANVA_DECK_BRIEF.md`, then let `design-studio-canva-figma` generate, edit, brand-check (`canva-brand-check`), resize launch visuals (`canva-resize-for-social-media`), and export investor-ready PDF/PPTX decks directly in Canva.
- **Figma (`antigravity-plugins-partners/plugin/figma`):** Run `pitch_deck_design_brief(target="figma")` to export `FIGMA_SLIDES_BRIEF.md` + W3C `FIGMA_TOKENS.json`, build native 1920x1080 variable-bound **Figma Slides** (`figma-use-slides`), push `landing/index.html` into editable Figma frames (`figma-generate-design`), or convert Figma wireframes straight into your 7-day MVP (`figma-design-to-code`).
- **Zapier (`antigravity-plugins-partners/plugin/zapier`) & QuickBooks Online (`intuit/quickbooks-online-mcp-server` / `intuit` CLI):** Connect **QuickBooks Online + 9,000+ apps** (Stripe, Gmail, Slack, HubSpot, Notion, Google Sheets) via 1-click Zapier OAuth or Intuit's official read-first MCP/CLI so Antigravity's `cfo-bookkeeper-copilot` answers plain-English P&L/cash/invoice questions, syncs verified numbers into `.startup/state.json` & `docs/INVESTOR_UPDATE.md`, and previews draft invoices before posting.

### 3. Eighteen Progressive-Disclosure Startup Skills
| Skill | Purpose |
| :--- | :--- |
| `startup-kickstart` | Day-0 5-question intake, FI One-Sentence Pitch linting, UN SDG iKPI selection, and full workspace scaffold |
| `revenue-first-validation` | Mom Test discovery, RAT experiments, Customer Paid-Pilot PACTs, and 48-hour deploy-ready landing page generator |
| `product-market-fit-engine` | Scientific PMF measurement: Sean Ellis 40% Very Disappointed rule, Superhuman HXC segmentation & 50/50 roadmap, retention flattening, and Pivot vs. Scale proof |
| `pitch-deck-builder` | Author, edit, re-theme, switch modes (`problem-solution` / `traction` / `teaser`), lint, and compile pitch decks |
| `design-studio-canva-figma` | Bridge FI-linted decks, landing pages, and launch kits directly into official Canva & Figma Slides MCP workflows |
| `replit-launchpad` | Zero-double-token Antigravity ↔ Replit Free-Tier bridge: Replit Design System, Web & Expo Mobile apps, and one-shot Replit Slides |
| `product-hunt-launch` | End-to-end ethical Product Hunt launch kit: linted <=60-char tagline, Maker Comment, `1270x760` Canva/Figma gallery storyboard, and T-14 -> 12:01 AM PT runbook |
| `multi-ai-connectors` | Optional BYO-AI addon hub: detect CLIs/env vars (`claude`, `codex`, `xai/grok`, `gemini`, `ollama`, `intuit`, `shelled`, `dipity`), sync context files, and run second-opinion critiques |
| `quickbooks-cfo-and-zapier` | Connect QuickBooks Online & 9,000+ apps via Zapier MCP, Intuit QBO MCP, or Intuit CLI with read-first accounting safety & preview-before-write invoicing |
| `fi-alumni-scale-stack` | Scale founder content with **Dipity Studio / Sera** (`docs/DIPITY_BRAND_BRAIN.md`) and multi-agent engineering PR pods with **Shelled AI** (`docs/SHELLED_HANDOFF.md`) |
| `founder-resources-library` | On-demand, stage-aware curated library of 32+ FI.co, VC Lab, PMF, legal, accounting, growth & AI founder resources + custom team/cohort bookmarks |
| `mvp-and-profit-architecture` | 7-day vertical slice MVP spec, explicit *NOT-Building-Yet* Cut-List, and `>= 75%` gross margin COGS audit |
| `market-and-unfair-moat` | Bottom-up TAM/SAM/SOM calculation, competitive teardowns, Why-Now analysis, and Secret Sauce audit |
| `gtm-and-cash-velocity` | Value-based pricing (10x ROI), ethical cold outbound, Show HN / Product Hunt launches, and first-100-customers loops |
| `unit-economics-and-profit-os` | Default-Alive runway modeling, CAC/LTV/Payback, QuickBooks Online bookkeeping hygiene, and FI Funding Readiness scoring |
| `advisors-equity-and-fast` | Founder Institute **FAST Agreement** advisor equity calculator, 3-month trial cliffs, and co-founder vesting hygiene |
| `vc-lab-fundraising-os` | VC fund thesis mapping, PACT soft-circle pipeline, multi-round cap table & SAFE math, Stripe Atlas + QuickBooks Data Room, and partner drills |
| `weekly-sprint-review` | FI weekly sprint accountability (`.startup/sprints.json`, 1.0–5.0 velocity) and VC Lab `docs/INVESTOR_UPDATE.md` generator |

### 4. Seven Founding Advisory Subagents
- **`fi-mentor-pitch-critic`** — Veteran FI Mentor who shreds buzzwords, grades slides 1.0–5.0, and sets 7-day homework sprints.
- **`vc-lab-partner-skeptic`** — Mensarius-bound VC Lab General Partner who audits fundability, math, moat, and runs 10-question partner drills.
- **`pmf-truth-auditor`** — Brutally honest Product-Market Fit investigator who answers *"Is there a REAL paying customer for this?"*, exposes leaky buckets, discovers your highest-PMF HXC segment, and builds your 50/50 PMF roadmap.
- **`cfo-bookkeeper-copilot`** — Read-first AI Fractional CFO & QuickBooks Online bookkeeper copilot (via Zapier MCP, Intuit QBO MCP, or `intuit` CLI) with strict preview-before-write accounting safety.
- **`customer-revenue-coach`** — *Mom Test* & paid-pilot coach who role-plays skeptical ICP buyers and turns pain into signed Customer PACTs.
- **`lean-cto-margin-architect`** — Pragmatic founding CTO who cuts engineering scope 50–70% and protects `>= 75%` gross margins.
- **`ethical-growth-strategist`** — Value-pricing, positioning, and ethical acquisition strategist (zero dark patterns).

### 5. Eighteen-Tool Local MCP Server (`startup-antigravity-os`)
Runs locally via Python 3 stdio (zero external API keys):
1. `startup_get_state` — Live telemetry, FI stage benchmark, interviews, PACT totals, and deck score
2. `startup_update_stage` — Persist stage, FI pitch, MRR, burn, cash, gross margin, and iKPI
3. `fi_pitch_lint` — Automated FI Madlibs, buzzword, vague-audience, 10-word headline, and 1-to-1 mirror linter
4. `assumption_manage` — Riskiest Assumption Board ranked by `Impact x Uncertainty`
5. `experiment_manage` — Pre-committed hypothesis + pass/fail threshold tracker
6. `interview_manage` — Mom Test discovery log + aggregate pain & willingness-to-pay stats
7. `pact_pipeline_manage` — Customer Paid-Pilot & Investor Soft-Circle PACT pipeline with weighted totals
8. `financial_calc` — Deterministic math for `runway`, `unit_economics`, `tam_bottom_up`, `safe_dilution`, `fast_advisor_equity`, and `cap_table_model`
9. `pitch_deck_build` — Lint + compile interactive SVG `index.html` and Marp `DECK.md`
10. `pitch_deck_design_brief` — Export Canva (`CANVA_DECK_BRIEF.md`), Figma Slides (`FIGMA_SLIDES_BRIEF.md` + W3C `FIGMA_TOKENS.json`), and one-shot Replit Slides (`REPLIT_SLIDES_BRIEF.md`) production handoffs
11. `landing_page_build` — Generate deploy-ready `landing/index.html` with interactive ROI calculator & PACT intake
12. `ikpi_catalog_search` — Offline search across all 17 UN SDGs (34 concrete FI *For-Progress* iKPIs)
13. `sprint_manage` — Weekly FI sprint tracker (`start`, `close`, `list`) + `docs/INVESTOR_UPDATE.md` compiler
14. `replit_workspace_prepare` — Scaffold `.replit`, `replit.md` (zero-double-token rules), `.env.example`, and `docs/REPLIT_HANDOFF.md` for `web-node`, `web-python`, or `mobile-expo`
15. `product_hunt_kit_build` — Lint Product Hunt character limits & buzzwords and generate `launch/product-hunt/PH_LAUNCH_KIT.md` + `launch-plan.json`
16. `ai_connectors_manage` — Detect optional BYO-AI CLIs/env vars, sync `CLAUDE.md`/`GROK_CONTEXT.md`/`AI_CONTEXT_PACK.md`/`DIPITY_BRAND_BRAIN.md`/`SHELLED_HANDOFF.md`, and run multi-model second opinions
17. `pmf_engine_manage` — Track Sean Ellis 40% Very Disappointed surveys, per-segment HXC PMF scores, cohort retention flattening, Superhuman 50/50 roadmaps, and `docs/PMF_SCORECARD.md`
18. `founder_resources_hub` — Search 32+ curated FI.co, VC Lab, PMF, legal, accounting, growth & AI founder resources, pull stage-matched Action Kits, or save custom team/cohort bookmarks

### 6. Optional BYO-AI Addon Connectors (Claude, OpenAI, xAI Grok, Gemini CLI & Ollama)
**Startup Antigravity is built for Google Antigravity first** — zero external AI keys are required. However, if a novice or technical founder already loves another AI platform, the `multi-ai-connectors` skill lets them plug it in cleanly without losing company context:
- **Auto-Detect (`ai_connectors_manage(action="detect")`):** Detects installed CLIs (`claude`, `codex`, `gemini`, `ollama`, `aider`) and API env vars (`XAI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`) — **never prints or saves key values**.
- **Universal Context Sync (`action="sync_context"`):** Exports your live `.startup/` state, FI pitch, 7-day Cut-List, and Mensarius rules into `CLAUDE.md`, `docs/GROK_CONTEXT.md`, and `docs/AI_CONTEXT_PACK.md` so secondary tools stay 100% aligned.
- **Multi-Model Second Opinion (`action="second_opinion"`):** Ask **xAI / Grok**, **Claude**, **OpenAI / Codex**, or **\$0 local Ollama** for a red-team pitch critique, market gut-check, or code review (falls back cleanly to a copy-pasteable prompt if no key/CLI is set!).

### 7. Always-On Guardrails & Four Lifecycle Hooks
- **Always-On Rules (`rules/AGENTS.md`):** Enforces Revenue-First velocity, FI buzzword-free clarity, `[VALIDATED]` vs `[HYPOTHESIS]` radical honesty, Mensarius Oath zero-dark-pattern ethics, and legal/secret hygiene.
- **`SessionStart` (`session_bootstrap.py`):** Cues `startup-kickstart` in empty folders or injects a concise 5-line Founder Pulse (Stage, MRR, PACTs, Active Sprint, Top Risk, iKPI).
- **`PreToolUse` (`pre_tool_guard.py`):** Blocks accidental Git commits of `.env`/keys/PII (`deny`) and nudges before heavy cluster infra (`terraform`/`kubectl`/`helm`) during `idea`/`validation` stages (`ask`).
- **`PostToolUse` (`post_deck_rebuild.py`):** Auto-recompiles `pitch-deck/index.html` and `pitch-deck/DECK.md` every time `pitch-deck/deck.json` is edited.
- **`Stop` (`stop_integrity_check.py`):** Verifies `.startup/state.json` and `pitch-deck/deck.json` remain valid JSON before ending a turn.

---

## Creator's Recommended Founder Stack (Personal Endorsements)

> *These are personal endorsements from a founder, Previous Founder Institute Director, and Current Mentor & Advisor who has used every one of these platforms across real companies for years. None of these recommendations are sponsored placements—and in the spirit of Mensarius Oath transparency, the Replit link below is my personal referral link.*

| Ecosystem / Tool | Why I Personally Recommend It | Link |
| :--- | :--- | :--- |
| **Founder Institute (`FI.co`)** | Nothing replaces real weekly mentor accountability, brutally honest pitch grading, and a global founder network. I **highly recommend** visiting [fi.co](https://fi.co) to find your **local chapter**—or applying directly to the flagship **Silicon Valley** or **San Francisco** chapters. | [fi.co](https://fi.co) |
| **Replit** | You can genuinely run your whole early startup on Replit: **Replit Design Mode** for your Design System, full-stack **Web Platforms**, **Expo Mobile Apps** with instant QR previews, built-in DB/Secrets, 1-click hosting, and **Replit Slides**—paired locally with Antigravity via GitHub so you stay on the Free tier without double token burn. | [replit.com/refer/peterbiggam](https://replit.com/refer/peterbiggam) *(referral link)* |
| **Stripe Atlas** | When Customer PACTs or revenue prove it's time to incorporate, **Stripe Atlas** gives founders a clean, investor-standard Delaware C-Corp, EIN, founder stock issuance with guided **83(b) election** filing, and instant Stripe payments readiness—zero messy DIY legal headaches. | [stripe.com/atlas](https://stripe.com/atlas) |
| **QuickBooks Online** | Don't wait until tax season or Seed due diligence to organize your finances. **QuickBooks Online** makes bookkeeping, expense tracking, real-time P&L / cash-flow visibility, and CPA handoffs effortless from Dollar #1. | [quickbooks.intuit.com/online](https://quickbooks.intuit.com/online/) |
| **Dipity Studio / Sera** *(FI Mentor & Grad)* | Built by fellow FI Mentor & Graduate [Morgan Von Druitt](https://x.com/MorganVonDruitt). Turns weekly founder voice notes and company docs into an AI executive "second brain" and on-brand content engine (LinkedIn, X, newsletters, blogs & Gen Studio visuals) with API & MCP support—synced directly from `docs/DIPITY_BRAND_BRAIN.md`. | [dipity.studio](https://www.dipity.studio/) · [Dev Docs](https://www.dipity.studio/dev-pages/documentation) |
| **Shelled AI** *(FI Silicon Valley AI Grad)* | Built by FI Graduate [Jacob Wellinghoff](https://x.com/binaryreality). Coordinates specialist AI engineering agents (architects, coders, testers, reviewers) over shared repo context—local, cloud, or private/on-prem—to scale tested PR velocity once PMF is validated, synced directly via `docs/SHELLED_HANDOFF.md`. | [shelled.ai](https://www.shelled.ai/) |

---

## Troubleshooting (Windows, macOS & Linux)

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| **Windows:** MCP server fails to start or `python3` opens Microsoft Store | Windows ships with a fake Microsoft Store `python3.exe` alias | Follow **Windows Step 1** above: disable the App Execution Alias in Windows Settings, ensure real Python 3.10+ is on `PATH`, and copy `python.exe` to `python3.exe` in your Python install folder. |
| **Plugin doesn't show up in Customizations > Plugins** | ZIP extraction created a double nested folder | Verify `plugin.json` is directly at `.../plugins/startup-antigravity/plugin.json` (not `.../startup-antigravity/StartupAntigravity-main/plugin.json`). |
| **Skills load, but MCP tools (`financial_calc`, etc.) don't appear yet** | An already-running conversation hasn't bound the new MCP server | Click **Additional Options (`...`) > MCP Servers > Refresh**, then open a **new conversation**. |
| **`git clone` asks for login or returns "Repository not found"** | Repo is currently set to private | Authenticate first with `gh auth login` (GitHub CLI) or configure SSH keys (`git@github.com:petebiggam357/StartupAntigravity.git`). |
| **`--pptx` export says `python-pptx` not installed** | Native `.pptx` export is optional so core install stays zero-dependency | Run `pip install python-pptx` (or open `pitch-deck/index.html` and click **Export PDF** for zero-install 16:9 slides). |

---

## License & Legal Notice

Licensed under the [MIT License](./LICENSE).

- **Independent Creator Notice:** Created independently by a **Previous Founder Institute Director and Current Mentor & Advisor**. This project is **not** affiliated with, sponsored by, or an official release of Founder Institute (`fi.co`), VC Lab, or Decile Group (`govclab.com`). Trademarks belong to their respective owners.
- **Not Legal or Tax Advice:** Operational templates and calculators included in this plugin (FI **FAST Agreement** equity splits, SAFE dilution models, multi-round cap tables, Customer/Investor PACTs, and entity checklists) are **educational business frameworks, not legal or tax advice**. Always have qualified startup counsel review binding agreements and tax filings (including 83(b) elections).
