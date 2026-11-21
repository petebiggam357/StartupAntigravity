# Contributing to Startup Antigravity

Welcome! **Startup Antigravity — Ethical Venture OS** is an open-source, zero-dependency Antigravity plugin built by founders, for founders. Contributions from Founder Institute alumni/mentors, Startup Grind chapters, Founders Guild builders, and open-source engineers are warmly welcomed.

## Core Design Principles
1. **Zero External Runtime Dependencies:** All skills, hooks, launcher scripts, and the local MCP server must run on **Python 3.10+ standard library only** (no required `pip` or `npm` installs).
2. **Radical Metric Honesty & Mensarius Oath Ethics:** No dark patterns, no hype buzzwords, no speculative tokenomics, and no fabricated claims.
3. **Always Tested:** Every PR must pass the full cross-platform test suite:
   ```bash
   python3 -m unittest discover -s tests -v
   ```

## High-Impact Ways to Contribute
- **Add Curated Founder Resources:** Submit a PR adding high-signal playbooks, templates, or tools to `mcp_server/founder_resources.json` (follow the existing schema and include `id`, `title`, `category`, `stages`, `format`, `source`, `url`, `summary`, `keyTakeaway`, and `tags`).
- **Add Pitch Deck Themes or Slide Layouts:** Extend `skills/pitch-deck-builder/scripts/build_deck.py`.
- **Add or Refine Startup Skills & Guardrails:** Keep `SKILL.md` concise and progressive-disclosure, and keep `rules/AGENTS.md` well under the 24 KB budget.
- **Test Native Packages Across OSes:** Report installation or launcher UX friction on macOS, Windows 10/11, Ubuntu, Pop!_OS, or Fedora.

## Local Development Setup
```bash
git clone https://github.com/petebiggam357/StartupAntigravity.git
cd StartupAntigravity
./install.sh --symlink        # macOS / Linux (or .\install.ps1 -Junction on Windows)
python3 -m unittest discover -s tests -v
```
