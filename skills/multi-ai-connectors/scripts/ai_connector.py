#!/usr/bin/env python3
"""
Startup Antigravity — Zero-Dependency Optional BYO-AI Connectors.

Antigravity is the primary Founder OS brain. This module lets founders optionally
plug in external AI platforms they already love — xAI / Grok, Anthropic Claude
(CLI or API), OpenAI (Codex CLI or API), Google Gemini CLI, or local Ollama —
to sync startup context across tools or get multi-model second opinions.

Zero third-party pip packages required (Python 3 standard library only).
Security rule: NEVER logs, prints, or writes API key values to disk.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

CLI_PROBES = {
    "claude-cli": {
        "binary": "claude",
        "label": "Anthropic Claude Code CLI",
        "installHint": "npm install -g @anthropic-ai/claude-code",
    },
    "codex-cli": {
        "binary": "codex",
        "label": "OpenAI Codex CLI",
        "installHint": "npm install -g @openai/codex",
    },
    "gemini-cli": {
        "binary": "gemini",
        "label": "Google Gemini CLI",
        "installHint": "npm install -g @google/gemini-cli",
    },
    "ollama": {
        "binary": "ollama",
        "label": "Ollama (100% Local / $0 Token AI)",
        "installHint": "https://ollama.com/download",
    },
    "aider": {
        "binary": "aider",
        "label": "Aider Multi-Model Coding CLI",
        "installHint": "pip install aider-chat",
    },
    "intuit-qbo-cli": {
        "binary": "intuit",
        "label": "Intuit Official QuickBooks Online CLI",
        "installHint": "https://github.com/intuit/intuit-cli-for-quickbooks",
    },
}

API_ENV_PROBES = {
    "xai": {
        "envVar": "XAI_API_KEY",
        "label": "xAI / Grok API",
        "defaultModel": "grok-3-mini",
        "endpoint": "https://api.x.ai/v1/chat/completions",
        "docsUrl": "https://console.x.ai/",
    },
    "openai": {
        "envVar": "OPENAI_API_KEY",
        "label": "OpenAI API",
        "defaultModel": "gpt-4o-mini",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "docsUrl": "https://platform.openai.com/api-keys",
    },
    "anthropic": {
        "envVar": "ANTHROPIC_API_KEY",
        "label": "Anthropic Claude API",
        "defaultModel": "claude-3-5-sonnet-latest",
        "endpoint": "https://api.anthropic.com/v1/messages",
        "docsUrl": "https://console.anthropic.com/",
    },
    "gemini": {
        "envVar": "GEMINI_API_KEY",
        "label": "Google Gemini API",
        "defaultModel": "gemini-2.5-flash",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
        "docsUrl": "https://aistudio.google.com/apikey",
    },
}


def detect_connectors() -> dict[str, Any]:
    """Detect installed AI CLIs and configured API key environment variables (never returns key values)."""
    clis: dict[str, Any] = {}
    for cid, meta in CLI_PROBES.items():
        path = shutil.which(meta["binary"])
        clis[cid] = {
            "label": meta["label"],
            "binary": meta["binary"],
            "installed": path is not None,
            "path": path or "",
            "installHint": meta["installHint"],
        }

    apis: dict[str, Any] = {}
    for pid, meta in API_ENV_PROBES.items():
        configured = bool(os.environ.get(meta["envVar"], "").strip())
        apis[pid] = {
            "label": meta["label"],
            "envVar": meta["envVar"],
            "configured": configured,
            "defaultModel": meta["defaultModel"],
            "docsUrl": meta["docsUrl"],
        }

    ready_providers = [k for k, v in clis.items() if v["installed"]] + [
        k for k, v in apis.items() if v["configured"]
    ]
    return {
        "primaryOS": "Google Antigravity (Startup Antigravity OS)",
        "readyAddons": ready_providers,
        "clis": clis,
        "apis": apis,
        "securityNote": "API key values are never read into logs, disk files, or Git.",
    }


def _load_startup_context(ws: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    sdir = ws / ".startup"
    state_file = sdir / "state.json"
    assump_file = sdir / "assumptions.json"
    state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {}
    assumptions = json.loads(assump_file.read_text(encoding="utf-8")) if assump_file.exists() else []
    return state, assumptions


def sync_ai_context(workspace_path: str | Path, targets: list[str] | None = None) -> dict[str, Any]:
    """
    Export Startup Antigravity's live state, FI pitch, Cut-List, and Mensarius guardrails
    into universal bridge files (`CLAUDE.md`, `docs/GROK_CONTEXT.md`, `docs/AI_CONTEXT_PACK.md`)
    so external AIs stay 100% aligned with Antigravity without re-explaining your startup.
    """
    ws = Path(workspace_path).expanduser().resolve()
    ws.mkdir(parents=True, exist_ok=True)
    state, assumptions = _load_startup_context(ws)

    company = state.get("companyName") or "Your Startup"
    stage = state.get("stage") or "idea"
    pitch = state.get("fiOneSentencePitch") or "Run startup-kickstart in Antigravity to define your FI One-Sentence Pitch."
    offering = state.get("offering") or "[defined offering]"
    audience = state.get("audience") or "[defined target audience]"
    secret = state.get("secretSauce") or "[secret sauce]"
    mrr = float(state.get("mrrUsd", 0))
    gm = float(state.get("grossMarginPct", 80))
    ikpi = state.get("ikpi") or {}
    ikpi_str = f"{ikpi.get('name', 'Unset')} ({ikpi.get('current', 0)}/{ikpi.get('target', 0)})"
    sprint_goal = state.get("activeSprintGoal") or "Close first paying Customer PACT within 14 days."

    untested = [a for a in assumptions if a.get("status") not in ("validated", "invalidated")]
    untested.sort(key=lambda x: x.get("riskScore", 0), reverse=True)
    top_risks = "\n".join(
        f"- [{a.get('id')}] (Risk {a.get('riskScore')}/25): {a.get('statement')}"
        for a in untested[:3]
    ) or "- No untested assumptions logged yet."

    core_block = f"""## Company Snapshot (Synced from Startup Antigravity OS)
- **Company:** {company}
- **FI Funding Readiness Stage:** `{stage}` (MRR: `${mrr:,.0f}` | Target Gross Margin: `{gm:.0f}%`)
- **FI One-Sentence Pitch:** {pitch}
- **Offering / Audience / Secret Sauce:** {offering} | {audience} | {secret}
- **Active Weekly Sprint Goal:** {sprint_goal}
- **For-Progress iKPI:** {ikpi_str}

## Top Riskiest Untested Assumptions
{top_risks}

## Non-Negotiable Founder Guardrails (FI.co + Mensarius Oath)
1. **Antigravity First, Zero Double Work:** Treat `.startup/state.json`, `docs/MVP_SPEC.md`, and `pitch-deck/deck.json` as source of truth. Do not rewrite architecture already committed.
2. **Revenue-First Velocity:** If stage is `idea` or `validation`, reject premature infra (Kubernetes, Terraform, microservices, custom auth/billing). Default to 7-day vertical slices.
3. **Zero Buzzwords & Radical Evidence Honesty:** Never use unverified superlatives (`revolutionary`, `disruptive`, `best`, `first`). Tag claims `[VALIDATED]` vs `[HYPOTHESIS]`.
4. **Mensarius Ethics:** Zero dark patterns, transparent pricing, 100% customer-owned data, never commit `.env` or secrets.
"""

    wanted = set(t.lower() for t in (targets or ["all"]))
    files_written: list[str] = []

    if "all" in wanted or "claude" in wanted:
        claude_md = ws / "CLAUDE.md"
        claude_md.write_text(
            f"# {company} — Claude Code / Anthropic Addon Context\n\n"
            "> Auto-synced from **Startup Antigravity**. Keep `.startup/` updated inside Antigravity.\n\n"
            + core_block,
            encoding="utf-8",
        )
        files_written.append(str(claude_md))

    docs_dir = ws / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    if "all" in wanted or "xai" in wanted or "grok" in wanted:
        grok_md = docs_dir / "GROK_CONTEXT.md"
        grok_md.write_text(
            f"# {company} — xAI / Grok Companion Context Pack\n\n"
            "> Paste or attach this file in **xAI / Grok** (web or API) for real-time market intel, X/social sentiment checks, or red-team pitch critiques aligned with Startup Antigravity.\n\n"
            + core_block,
            encoding="utf-8",
        )
        files_written.append(str(grok_md))

    if "all" in wanted or "openai" in wanted or "codex" in wanted or "universal" in wanted:
        pack_md = docs_dir / "AI_CONTEXT_PACK.md"
        pack_md.write_text(
            f"# {company} — Universal Multi-AI Context Pack (OpenAI / Codex / Gemini / Ollama)\n\n"
            "> Attach or paste this into OpenAI Codex CLI, ChatGPT, Gemini CLI, or local Ollama so any secondary AI shares your exact Startup Antigravity state and ethical guardrails.\n\n"
            + core_block,
            encoding="utf-8",
        )
        files_written.append(str(pack_md))

    return {
        "companyName": company,
        "stage": stage,
        "filesWritten": files_written,
        "tip": "Re-run sync_context after major stage or pitch updates so Claude, OpenAI, Grok, and Ollama stay 100% aligned with Antigravity.",
    }


def _http_post_json(url: str, headers: dict[str, str], body: dict[str, Any], timeout: int = 45) -> dict[str, Any]:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run_second_opinion(
    provider: str,
    prompt: str,
    workspace_path: str | Path | None = None,
    model: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Query an optional external AI provider (xai, openai, anthropic, ollama, or installed CLI)."""
    prov = provider.lower().strip()
    context_prefix = ""
    if workspace_path:
        ws = Path(workspace_path).expanduser().resolve()
        state, _ = _load_startup_context(ws)
        if state:
            context_prefix = (
                f"Startup Context: {state.get('companyName', 'Startup')} | "
                f"Stage: {state.get('stage', 'idea')} | "
                f"FI Pitch: {state.get('fiOneSentencePitch', '')}\n"
                "Rules: Be direct, zero buzzwords, Mensarius ethics (no dark patterns), focus on ethical profit velocity.\n\n"
            )

    full_prompt = context_prefix + prompt.strip()

    if dry_run:
        return {
            "provider": prov,
            "mode": "dry_run",
            "readyPrompt": full_prompt,
            "note": "Dry run only — no external API call or CLI process executed.",
        }

    # OpenAI-compatible APIs (xAI Grok & OpenAI)
    if prov in ("xai", "grok", "openai"):
        key_id = "xai" if prov in ("xai", "grok") else "openai"
        meta = API_ENV_PROBES[key_id]
        api_key = os.environ.get(meta["envVar"], "").strip()
        if not api_key:
            return {
                "provider": key_id,
                "configured": False,
                "error": f"{meta['envVar']} is not set in your environment.",
                "setupHint": f"Export {meta['envVar']} (from {meta['docsUrl']}) or paste readyPrompt directly into the web UI.",
                "readyPrompt": full_prompt,
            }
        chosen_model = model or meta["defaultModel"]
        data = _http_post_json(
            meta["endpoint"],
            {"Authorization": f"Bearer {api_key}"},
            {
                "model": chosen_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a sharp, ethical startup advisor giving a concise second opinion.",
                    },
                    {"role": "user", "content": full_prompt},
                ],
                "temperature": 0.4,
            },
        )
        reply = data["choices"][0]["message"]["content"]
        return {"provider": key_id, "model": chosen_model, "configured": True, "response": reply}

    # Anthropic Messages API
    if prov == "anthropic":
        meta = API_ENV_PROBES["anthropic"]
        api_key = os.environ.get(meta["envVar"], "").strip()
        if not api_key:
            return {
                "provider": "anthropic",
                "configured": False,
                "error": f"{meta['envVar']} is not set in your environment.",
                "setupHint": f"Export {meta['envVar']} (from {meta['docsUrl']}) or install Claude CLI (`claude`).",
                "readyPrompt": full_prompt,
            }
        chosen_model = model or meta["defaultModel"]
        data = _http_post_json(
            meta["endpoint"],
            {"x-api-key": api_key, "anthropic-version": "2023-06-01"},
            {
                "model": chosen_model,
                "max_tokens": 1200,
                "messages": [{"role": "user", "content": full_prompt}],
            },
        )
        blocks = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
        return {"provider": "anthropic", "model": chosen_model, "configured": True, "response": "\n".join(blocks)}

    # Local Ollama ($0 token cost)
    if prov == "ollama":
        chosen_model = model or "llama3.2"
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        try:
            data = _http_post_json(
                f"{host}/api/generate",
                {},
                {"model": chosen_model, "prompt": full_prompt, "stream": False},
                timeout=60,
            )
            return {"provider": "ollama", "model": chosen_model, "configured": True, "response": data.get("response", "")}
        except Exception as exc:
            return {
                "provider": "ollama",
                "configured": False,
                "error": f"Could not reach local Ollama at {host}: {exc}",
                "setupHint": "Install Ollama (https://ollama.com/download) and run `ollama pull llama3.2`.",
                "readyPrompt": full_prompt,
            }

    # Installed CLI connectors (claude-cli, codex-cli, gemini-cli)
    if prov in ("claude-cli", "codex-cli", "gemini-cli"):
        meta = CLI_PROBES[prov]
        binary = shutil.which(meta["binary"])
        if not binary:
            return {
                "provider": prov,
                "configured": False,
                "error": f"CLI '{meta['binary']}' not found on PATH.",
                "setupHint": f"Install via: {meta['installHint']}",
                "readyPrompt": full_prompt,
            }
        cmd_map = {
            "claude-cli": [binary, "-p", full_prompt],
            "codex-cli": [binary, "exec", full_prompt],
            "gemini-cli": [binary, "-p", full_prompt],
        }
        proc = subprocess.run(cmd_map[prov], capture_output=True, text=True, timeout=90)
        if proc.returncode != 0:
            return {
                "provider": prov,
                "configured": True,
                "error": proc.stderr.strip() or f"CLI exited with code {proc.returncode}",
            }
        return {"provider": prov, "configured": True, "response": proc.stdout.strip()}

    raise ValueError(
        "Unsupported provider. Choose one of: xai, openai, anthropic, ollama, claude-cli, codex-cli, gemini-cli."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Startup Antigravity BYO-AI Connector Utility")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("detect", help="Detect installed AI CLIs and configured API env vars")

    p_sync = sub.add_parser("sync", help="Sync Startup Antigravity context to CLAUDE.md / GROK_CONTEXT.md / AI_CONTEXT_PACK.md")
    p_sync.add_argument("--workspace", required=True)
    p_sync.add_argument("--targets", nargs="*", default=["all"])

    p_ask = sub.add_parser("ask", help="Request a second opinion from an external AI connector")
    p_ask.add_argument("--provider", required=True)
    p_ask.add_argument("--prompt", required=True)
    p_ask.add_argument("--workspace")
    p_ask.add_argument("--model")
    p_ask.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()
    if args.cmd == "detect":
        print(json.dumps(detect_connectors(), indent=2))
    elif args.cmd == "sync":
        print(json.dumps(sync_ai_context(args.workspace, args.targets), indent=2))
    elif args.cmd == "ask":
        print(
            json.dumps(
                run_second_opinion(args.provider, args.prompt, args.workspace, args.model, args.dry_run),
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
