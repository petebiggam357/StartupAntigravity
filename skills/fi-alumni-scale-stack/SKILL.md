---
name: fi-alumni-scale-stack
description: >-
  Scale founder content distribution and multi-agent software engineering using two
  Founder Institute alumni-built platforms: Dipity Studio / Sera (AI executive second
  brain & brand content studio by FI Mentor & Graduate Morgan Von Druitt) and Shelled AI
  (coordinated multi-agent coding, testing & PR platform by FI Graduate Jacob Wellinghoff).
  Use when a founder wants to scale authentic founder-led content via Dipity Studio or
  scale engineering PR throughput via Shelled AI while staying synced with Antigravity.
---

# Founder Institute Alumni Scale Stack (Dipity Studio & Shelled AI)

Startup Antigravity proudly integrates two high-leverage scaling platforms built by fellow **Founder Institute** community leaders (personal endorsements — not official FI corporate releases):

1. **Dipity Studio / Sera** (`https://www.dipity.studio/` | Dev Docs: `https://www.dipity.studio/dev-pages/documentation`) — Created by FI Mentor & Graduate **Morgan Von Druitt** (`https://x.com/MorganVonDruitt`). Turns founder voice notes, interviews, and startup docs into an executive "second brain" and on-brand content engine (LinkedIn, X, newsletters, blogs, and Gen Studio visuals) with API, webhooks, and MCP support.
2. **Shelled AI** (`https://www.shelled.ai/`) — Created by FI Silicon Valley AI Graduate **Jacob Wellinghoff** (`https://x.com/binaryreality`). Orchestrates coordinated teams of specialist AI agents (architects, coders, testers, reviewers, deployers) over shared project context to turn requirements into tested, reviewed Pull Requests — model-agnostic across local, cloud, or private/on-prem deployments.

---

## Workflow A: Scale Founder Content Distribution With Dipity Studio (Sera)

*Best starting in `validation` -> `mvp` -> `seed_scale` to build authentic inbound pull without ad burn.*

1. Call `ai_connectors_manage(action="detect")` to check if `DIPITY_API_KEY` is configured in the environment.
2. Call `ai_connectors_manage(action="sync_context", workspace_path=..., targets=["dipity"])` (or `["all"]`) to generate **`docs/DIPITY_BRAND_BRAIN.md`** directly from `.startup/state.json` and `.startup/assumptions.json`.
   - Exports your FI-linted One-Sentence Pitch, Secret Sauce, For-Progress iKPI, active sprint wins, and zero-buzzword Mensarius voice rules.
3. Upload or connect **`docs/DIPITY_BRAND_BRAIN.md`** into your Dipity Studio / Sera workspace (or via Dipity's API/MCP — see https://www.dipity.studio/dev-pages/documentation) so every LinkedIn post, X thread, newsletter, and Product Hunt launch story stays 100% aligned with your verified startup metrics and authentic founder voice.

---

## Workflow B: Scale Multi-Agent Engineering Velocity With Shelled AI

*Best once problem/solution or PMF is validated (`mvp` -> `pre_seed_traction` -> `seed_scale`) and you want coordinated architect/coder/tester/reviewer PR pods.*

1. Respect the **PMF & Revenue-First Gate**: Do not spin up heavy multi-agent engineering pods before validating real buyer pain (`revenue-first-validation`) or PMF (`pmf_engine_manage`).
2. Call `ai_connectors_manage(action="detect")` to check if `shelled` CLI or `SHELLED_API_KEY` is configured.
3. Call `ai_connectors_manage(action="sync_context", workspace_path=..., targets=["shelled"])` (or `["all"]`) to generate **`docs/SHELLED_HANDOFF.md`** containing:
   - Your FI stage, One-Sentence Pitch, and active weekly sprint goal
   - Your explicit 7-day Vertical Slice & *NOT-Building-Yet* Cut-List guardrails
   - Gross-margin (`>= 75%`) and Mensarius data-privacy/security engineering standards
4. Point **Shelled AI** (`https://www.shelled.ai/`) at your private GitHub repository (local, Shelled Cloud, or private/on-prem) so its specialist agents plan, code, test, and open clean Pull Requests without violating your Startup Antigravity guardrails or burning duplicate Antigravity tokens.
