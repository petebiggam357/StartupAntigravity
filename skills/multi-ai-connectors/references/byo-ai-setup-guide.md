# Novice-Friendly BYO-AI Connector Setup Guide

> **Antigravity First:** You do **NOT** need any external AI account or API key to use Startup Antigravity. These connectors are 100% optional power-ups if you already pay for **xAI/Grok**, **Claude**, **OpenAI/Codex**, or want free local **Ollama**.

## Quick Connector Matrix

| Platform | Best Used For Alongside Antigravity | CLI Option | API Env Var |
| :--- | :--- | :--- | :--- |
| **xAI / Grok** | Blunt red-team pitch critiques, X/social sentiment & "Why Now?" market pulse | Web / API | `XAI_API_KEY` |
| **Anthropic Claude** | Long-form writing, copy polish, deep code reviews (`CLAUDE.md` auto-synced!) | `claude` (Claude Code) | `ANTHROPIC_API_KEY` |
| **OpenAI / Codex** | Code generation second opinions, structured brainstorming | `codex` (Codex CLI) | `OPENAI_API_KEY` |
| **Google Gemini CLI** | Terminal-native companion workflows | `gemini` (Gemini CLI) | `GEMINI_API_KEY` |
| **Ollama (Local)** | **\$0/token** offline drafts & private customer note synthesis | `ollama` | None (`localhost:11434`) |

---

## Setting Environment Variables Safely (Never Put Keys in Git!)

### macOS / Linux (`~/.zshrc` or `~/.bashrc`)
```bash
# Add ONLY the providers you actually use:
export XAI_API_KEY="xai-..."
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIza..."
```
Reload your terminal (`source ~/.zshrc`) and restart Antigravity's MCP server (`MCP Servers > Refresh`).

### Windows (PowerShell — Persists for Your User Account)
```powershell
# Add ONLY the providers you actually use:
[Environment]::SetEnvironmentVariable("XAI_API_KEY", "xai-...", "User")
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")
```
Open a new Antigravity session (or refresh MCP Servers) so the local MCP server sees the new variables.

---

## Installing Optional AI CLIs (1 Command Each)

- **Anthropic Claude Code CLI:** `npm install -g @anthropic-ai/claude-code` -> run `claude` to sign in.
- **OpenAI Codex CLI:** `npm install -g @openai/codex` -> run `codex` to sign in.
- **Google Gemini CLI:** `npm install -g @google/gemini-cli` -> run `gemini` to sign in.
- **Ollama (Free Local AI, Zero API Key):** Download at https://ollama.com/download, then run `ollama pull llama3.2`.

> **Tip for Non-Technical Founders:** Don't want to touch API keys or CLIs at all? Just ask Antigravity to run `ai_connectors_manage(action="sync_context")` and copy-paste `docs/GROK_CONTEXT.md` or `docs/AI_CONTEXT_PACK.md` straight into Grok, ChatGPT, or Claude in your web browser!
