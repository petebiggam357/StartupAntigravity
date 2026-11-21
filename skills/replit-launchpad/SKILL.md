---
name: replit-launchpad
description: >-
  Zero-double-token-burn bridge between local Antigravity and Replit's Free/Starter
  tier. Starts with the Replit Design System (Design Mode), connects the local Git
  repo to Replit without wasting duplicate AI credits, launches either a full-stack
  Web Platform or Expo/React Native Mobile App, and generates one-shot Replit Slides
  pitch decks. Use when a founder wants an all-in-one cloud design, preview, mobile
  QR, hosting, and deck workflow on Replit.
---

# Replit Launchpad (Antigravity ↔ Replit Zero-Double-Token Bridge)

Build locally with full power in **Antigravity**, then sync cleanly to **Replit** (`https://replit.com/refer/peterbiggam` — personal founder endorsement & referral link) so you get an **all-in-one platform** (Design System, Web App, Expo Mobile App, Secrets/DB, instant cloud hosting, and Replit Slides) while maximizing **Replit's Free/Starter tier** and avoiding double AI token burn.

See [replit-free-tier-playbook.md](./references/replit-free-tier-playbook.md) for the full "Why Replit" breakdown, Free-Tier survival rules, and Expo Go mobile preview steps.

## The Golden Rule: Zero Double Token Burn

Never pay AI twice to build the same thing:
- **Use Antigravity (Local)** for strategy, FI pitch linting, architecture, heavy multi-file coding, refactoring, and automated tests inside your local Git repository.
- **Use Replit (Cloud)** for **Replit Design Mode** (rapid visual prototype & living style guide), **Git-synced cloud runtime & live URL**, **Expo Go QR mobile testing**, **Secrets/Postgres**, and optional **one-shot Replit Slides**.
- **Sync via Private GitHub Repo (Zero AI Tokens):** Push commits locally from Antigravity and pull in Replit's Git pane—never ask Replit Agent to rewrite features Antigravity already wrote.

## Step 1: Start Visually With the Replit Design System

1. If starting from a blank visual slate, spin up a quick UI prototype in **Replit Design Mode** (under 2 minutes) to nail layout, spacing, and visual hierarchy before building backend logic.
2. Export or pull the resulting visual tokens/styles back into your local Antigravity repo (`pitch-deck/design-handoff/FIGMA_TOKENS.json` or CSS variables) so your **Landing Page**, **MVP**, and **Pitch Deck** share one unified Design System.

## Step 2: Prepare Your Local Repo for Replit (`replit_workspace_prepare`)

Call the `replit_workspace_prepare` MCP tool:
- `workspace_path`: Founder's local project directory
- `app_type`: `"web-node"` | `"web-python"` | `"mobile-expo"`

This deterministically creates:
- **`replit.md`** — Instructs Replit's workspace/agent to respect Antigravity's local architecture and **never** burn tokens regenerating already-implemented modules.
- **`.replit`** — Pre-wired run/entrypoint configuration for your exact stack (Node/Next.js, Python/FastAPI, or Expo React Native).
- **`.env.example`** — Clean list of environment variables to paste into **Replit Secrets** (never committed to Git).
- **`docs/REPLIT_HANDOFF.md`** — Step-by-step zero-token GitHub import, Secrets setup, Free-Tier guardrails, and Expo Go mobile QR instructions.

## Step 3: Connect Private GitHub Repo & Launch on Replit Free Tier

1. Push your local Antigravity project to a **private** GitHub repository (`gh repo create --private`).
2. Open [Replit](https://replit.com/refer/peterbiggam) -> **Create Repl -> Import from GitHub** -> select your private repository.
3. Add keys from `.env.example` into Replit's **Secrets** pane and click **Run**:
   - **Web Platform:** Share your live preview URL immediately with pilot customers.
   - **Mobile App (`mobile-expo`):** Scan the generated **Expo Go QR code** on iOS or Android to test on real hardware in 60 seconds with zero Xcode/Android Studio setup.

## Step 4: Optional One-Shot Replit Slides Deck

Because Replit also builds slide decks (**Replit Slides**), founders who want **everything in one Replit workspace** (Design System + Web/Mobile App + Hosting + Pitch Deck) can call:
`pitch_deck_design_brief(workspace_path=..., target="replit")`

This generates `pitch-deck/design-handoff/REPLIT_SLIDES_BRIEF.md` — a single, FI-linted, one-shot prompt designed to generate the entire presentation in Replit in 1 turn without wasting free-tier credits.
