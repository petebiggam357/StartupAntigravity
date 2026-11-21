---
name: multi-ai-connectors
description: >-
  Optional BYO-AI connector hub for novice and technical founders who want to plug
  their favorite external AI platforms — xAI/Grok, Anthropic Claude (Code CLI or API),
  OpenAI (Codex CLI or API), Google Gemini CLI, or free local Ollama — into Startup
  Antigravity. Detects installed CLIs/env vars, syncs company context files (`CLAUDE.md`,
  `docs/GROK_CONTEXT.md`, `docs/AI_CONTEXT_PACK.md`) so every AI shares FI & Mensarius
  guardrails, and runs optional multi-model second-opinion critiques.
---

# Multi-AI Addon Connectors (Antigravity First, Any AI Optional)

**Google Antigravity** is your primary Founder OS brain (running all skills, FI linting, MCP state, pitch decks, and hooks). This optional addon lets **even a non-technical / novice founder** plug in whatever additional AI subscription or CLI they already love—**xAI / Grok, Claude, OpenAI / Codex, Gemini CLI, or \$0 local Ollama**—without losing context or duplicating work.

See [byo-ai-setup-guide.md](./references/byo-ai-setup-guide.md) for beginner-friendly Windows, macOS, and Linux setup steps for every provider.

## Step 1: Auto-Detect Available AI Connectors (`detect`)

Call `ai_connectors_manage(action="detect")` to inspect which AI CLIs (`claude`, `codex`, `gemini`, `ollama`, `aider`) and API keys (`XAI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`) are ready on the founder's machine.
- **Security Guarantee:** Only reports `configured: true/false` — **never** prints, logs, or stores API key values.

## Step 2: Sync Your Startup OS Context Across Every AI (`sync_context`)

Call `ai_connectors_manage(action="sync_context", workspace_path=..., targets=["all"])`.

This writes three synchronized bridge files directly from `.startup/state.json` and `.startup/assumptions.json`:
- **`CLAUDE.md`** — Auto-loaded by Anthropic Claude Code CLI so Claude respects your FI One-Sentence Pitch, 7-day Cut-List, and Mensarius guardrails.
- **`docs/GROK_CONTEXT.md`** — Paste/attach into **xAI / Grok** for real-time X/social market intel, trend validation, and blunt pitch critiques.
- **`docs/AI_CONTEXT_PACK.md`** — Universal context pack for **OpenAI Codex CLI / ChatGPT / Gemini CLI / Ollama**.

## Step 3: Optional Multi-Model "Second Opinion" Council (`second_opinion`)

When a founder wants an outside gut-check (e.g., *"Ask Grok to check real-time market positioning"* or *"Ask Claude to review our landing page copy for clarity"*):
1. Call `ai_connectors_manage(action="second_opinion", provider="xai"|"openai"|"anthropic"|"ollama"|"claude-cli"|"codex-cli"|"gemini-cli", prompt=..., workspace_path=...)`.
2. If the founder hasn't configured an API key or CLI yet, the tool gracefully returns a **ready-to-paste `readyPrompt`** plus exact 1-line setup instructions so a novice founder is never stuck!

## Cost & Margin Discipline (No Double Token Burn)

- **Default to Antigravity** for day-to-day execution, strategy, and coding.
- Use **Ollama** (`ollama pull llama3.2`) for **\$0 local drafts** if bootstrapping on zero budget.
- Reserve paid external API calls (`xai`, `openai`, `anthropic`) for targeted high-leverage second opinions or specialized CLI tasks—never run two coding agents blindly over the same files at once.
