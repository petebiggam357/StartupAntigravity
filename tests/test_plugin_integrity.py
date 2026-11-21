"""Validate Antigravity plugin manifest, rules, hooks, MCP config, skills, and subagents."""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ALLOWED_MANIFEST_KEYS = {
    "name",
    "displayName",
    "version",
    "description",
    "logo",
    "suggestedPrompts",
    "author",
    "homepage",
    "repository",
    "disabled",
}


def _parse_frontmatter(md_text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", md_text, re.DOTALL)
    if not match:
        return {}
    fm: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm


class TestPluginIntegrity(unittest.TestCase):
    def test_plugin_manifest(self) -> None:
        manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
        unknown = set(manifest.keys()) - ALLOWED_MANIFEST_KEYS
        self.assertEqual(unknown, set(), f"Disallowed top-level manifest keys: {unknown}")
        self.assertEqual(manifest["name"], "startup-antigravity")
        self.assertEqual(len(manifest["suggestedPrompts"]), 3)
        logo = ROOT / manifest["logo"]
        self.assertTrue(logo.exists(), "Declared logo asset must exist")
        self.assertTrue(logo.suffix in {".svg", ".png", ".jpg", ".jpeg", ".webp"})

    def test_rules_budget_and_format(self) -> None:
        rules = ROOT / "rules" / "AGENTS.md"
        self.assertTrue(rules.exists())
        raw = rules.read_bytes()
        self.assertLess(len(raw), 24_000, "rules/AGENTS.md must stay under 24KB")
        text = raw.decode("utf-8")
        self.assertFalse(text.startswith("---\n"), "Plugin rules/AGENTS.md must not have frontmatter")

    def test_mcp_config_namespaced(self) -> None:
        cfg = json.loads((ROOT / "mcp_config.json").read_text(encoding="utf-8"))
        servers = cfg.get("mcpServers", {})
        self.assertIn("startup-antigravity-os", servers)
        for name in servers:
            self.assertTrue(
                name.startswith("startup-antigravity"),
                f"MCP server '{name}' must be prefixed with plugin name",
            )

    def test_hooks_schema(self) -> None:
        hooks = json.loads((ROOT / "hooks.json").read_text(encoding="utf-8"))
        self.assertEqual(len(hooks), 4)
        # SessionStart and Stop must be flat arrays of handlers
        ss = hooks["startup-session-bootstrap"]["SessionStart"]
        self.assertIsInstance(ss, list)
        self.assertIn("command", ss[0])

        stop = hooks["startup-json-integrity"]["Stop"]
        self.assertIsInstance(stop, list)
        self.assertIn("command", stop[0])

        # PreToolUse and PostToolUse must be grouped with matcher + hooks
        pre = hooks["startup-ethics-and-scope-guard"]["PreToolUse"]
        self.assertIn("matcher", pre[0])
        self.assertIn("hooks", pre[0])

        post = hooks["pitch-deck-auto-rebuild"]["PostToolUse"]
        self.assertIn("matcher", post[0])
        self.assertIn("hooks", post[0])

    def test_all_thirteen_skills(self) -> None:
        expected_skills = {
            "startup-kickstart",
            "pitch-deck-builder",
            "design-studio-canva-figma",
            "replit-launchpad",
            "product-hunt-launch",
            "revenue-first-validation",
            "mvp-and-profit-architecture",
            "market-and-unfair-moat",
            "gtm-and-cash-velocity",
            "unit-economics-and-profit-os",
            "advisors-equity-and-fast",
            "vc-lab-fundraising-os",
            "weekly-sprint-review",
        }
        skills_dir = ROOT / "skills"
        found = {p.name for p in skills_dir.iterdir() if p.is_dir()}
        self.assertEqual(found, expected_skills)

        for name in expected_skills:
            skill_md = skills_dir / name / "SKILL.md"
            self.assertTrue(skill_md.exists(), f"Missing {skill_md}")
            fm = _parse_frontmatter(skill_md.read_text(encoding="utf-8"))
            self.assertEqual(fm.get("name"), name)
            self.assertTrue(fm.get("description"), f"Missing description in {skill_md}")

    def test_ikpi_catalog_covers_all_17_sdgs(self) -> None:
        catalog = json.loads((ROOT / "mcp_server" / "ikpi_catalog.json").read_text(encoding="utf-8"))
        sdgs = {item["sdgNumber"] for item in catalog}
        self.assertEqual(sdgs, set(range(1, 18)))
        self.assertGreaterEqual(len(catalog), 34)

    def test_all_five_subagents(self) -> None:
        expected_agents = {
            "fi-mentor-pitch-critic",
            "vc-lab-partner-skeptic",
            "customer-revenue-coach",
            "lean-cto-margin-architect",
            "ethical-growth-strategist",
        }
        agents_dir = ROOT / "agents"
        found = {p.stem for p in agents_dir.glob("*.md")}
        self.assertEqual(found, expected_agents)

        for name in expected_agents:
            agent_md = agents_dir / f"{name}.md"
            fm = _parse_frontmatter(agent_md.read_text(encoding="utf-8"))
            self.assertEqual(fm.get("name"), name)
            self.assertEqual(fm.get("subagent"), "true")
            self.assertEqual(fm.get("inheritMcp"), "true")


if __name__ == "__main__":
    unittest.main()
