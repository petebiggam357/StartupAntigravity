---
name: founder-resources-library
description: >-
  On-demand, stage-aware Founder Resources Library powered by `founder_resources_hub`.
  Surfaces curated Founder Institute (fi.co), VC Lab / Decile Group (govclab.com),
  PMF, Mom Test, legal/equity (SAFE, FAST, Stripe Atlas), accounting (QuickBooks Online),
  cloud/design (Replit, Canva, Figma, Zapier), and FI Alumni Scale Stack (Dipity Studio,
  Shelled AI) resources matched to the founder's exact stage, plus lets teams save
  custom bookmarks into `.startup/custom_resources.json`.
---

# Founder Resources Library (On-Demand Curated Knowledge Hub)

Founders waste weeks drowning in contradictory startup advice. Use the `founder_resources_hub` MCP tool to deliver **high-signal, stage-matched playbooks, templates, tools, and primary sources** on demand—always paired with the exact Startup Antigravity action that puts the lesson into practice immediately.

## Workflow

1. **Stage-Matched Action Kit (`action="stage_kit"`)**:
   - Call `founder_resources_hub(action="stage_kit", workspace_path=...)` whenever a founder asks *"What should I learn or focus on right now?"*
   - Automatically reads `.startup/state.json` to detect their current FI stage (`idea` -> `validation` -> `mvp` -> `pre_seed_traction` -> `seed_scale`) and returns the exact curated resources + recommended next skill/subagent for that stage.
2. **Targeted Topic or Keyword Search (`action="search"`)**:
   - Call `founder_resources_hub(action="search", query=..., category=..., stage=..., limit=6)` when the founder asks about a specific topic (e.g., `"SAFE"`, `"83(b)"`, `"PMF"`, `"pricing"`, `"Product Hunt"`, `"QuickBooks"`, `"Replit"`, `"Dipity"`, `"Shelled"`, `"Mom Test"`).
   - Call `founder_resources_hub(action="categories")` to show all 11 browsable categories (`accelerators`, `pitching`, `validation`, `pmf`, `product-mvp`, `gtm-growth`, `content-distribution`, `finance-accounting`, `legal-equity`, `fundraising`, `ethics-impact`).
3. **Save Team / Cohort Bookmarks (`action="save_custom"`)**:
   - Call `founder_resources_hub(action="save_custom", workspace_path=..., title=..., url=..., category=..., summary=..., tags=[...])` so founders, co-founders, or FI mentors can add their own custom playbooks, local chapter links, or industry registries to `.startup/custom_resources.json`.
4. **Always Pair Knowledge With Action**:
   - Never dump a wall of links without a next step. For every resource returned, highlight its `keyTakeaway` and offer the exact Startup Antigravity skill/tool (e.g., `fi_pitch_lint`, `pmf_engine_manage`, `financial_calc`, `landing_page_build`, `replit_workspace_prepare`) to apply it right away.
