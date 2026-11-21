"""Tests for the Founder Institute pitch deck linter, compiler, and Day-0 scaffolder."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "pitch-deck-builder" / "scripts"))
sys.path.insert(0, str(ROOT / "skills" / "startup-kickstart" / "scripts"))

from build_deck import build_deck, lint_deck, lint_one_sentence_pitch  # noqa: E402
from scaffold_startup import scaffold_workspace  # noqa: E402


class TestPitchDeckAndScaffolder(unittest.TestCase):
    def test_fi_one_sentence_pitch_lint_clean(self) -> None:
        pitch = (
            "My company, ClaimGuard, is developing automated billing reconciliation software "
            "to help independent dental clinics recover $4,000/month in denied claims "
            "with real-time payer-rule validation."
        )
        res = lint_one_sentence_pitch(pitch)
        self.assertTrue(res["passed"])
        self.assertEqual(res["score"], 100)
        self.assertEqual(res["issues"], [])

    def test_fi_one_sentence_pitch_catches_buzzwords_and_vague_audience(self) -> None:
        bad = (
            "My company, FooAI, is developing a revolutionary seamless platform "
            "to help small businesses grow faster."
        )
        res = lint_one_sentence_pitch(bad)
        self.assertFalse(res["passed"])
        rules = {i["rule"] for i in res["issues"]}
        self.assertIn("fi-no-buzzwords", rules)
        self.assertIn("fi-specific-audience", rules)
        self.assertIn("fi-secret-sauce", rules)

    def test_problem_solution_traction_and_teaser_templates_compile(self) -> None:
        res_dir = ROOT / "skills" / "pitch-deck-builder" / "resources"
        for tpl_name in ("deck.problem-solution.json", "deck.traction.json", "deck.teaser.json"):
            with tempfile.TemporaryDirectory() as td:
                src = Path(td) / "deck.json"
                src.write_text((res_dir / tpl_name).read_text(encoding="utf-8"), encoding="utf-8")
                out = build_deck(src)
                html_path = Path(out["htmlPath"])
                md_path = Path(out["markdownPath"])
                self.assertTrue(html_path.exists())
                self.assertTrue(md_path.exists())
                html_txt = html_path.read_text(encoding="utf-8")
                self.assertIn('class="slide', html_txt)
                self.assertIn("Export PDF", html_txt)
                self.assertIn("marp: true", md_path.read_text(encoding="utf-8"))
                if tpl_name == "deck.teaser.json":
                    self.assertIn("<svg", html_txt)
                    self.assertIn("<polyline", html_txt)
                if tpl_name == "deck.traction.json":
                    self.assertIn("Competitive 2x2 Quadrant", html_txt)
                    self.assertIn("browser-frame", html_txt)

    def test_chart_bar_slide_renders_svg_bars(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            deck = {
                "meta": {
                    "companyName": "ClaimGuard",
                    "deckMode": "teaser",
                    "fiOneSentencePitch": (
                        "My company, ClaimGuard, is developing billing software to help "
                        "independent dental clinics stop claim losses with automated payer checks."
                    ),
                },
                "slides": [
                    {"id": "cover", "type": "cover", "headline": "ClaimGuard Teaser"},
                    {
                        "id": "bar",
                        "type": "chart-bar",
                        "headline": "Quarterly Net Profit Growth",
                        "unitPrefix": "$",
                        "series": [{"label": "Q1", "value": 10000}, {"label": "Q2", "value": 28000}],
                    },
                    {"id": "ask", "type": "ask", "headline": "Raising $500K Seed", "askAmount": "$500K"},
                ],
            }
            src = Path(td) / "deck.json"
            src.write_text(json.dumps(deck), encoding="utf-8")
            out = build_deck(src)
            html_txt = Path(out["htmlPath"]).read_text(encoding="utf-8")
            self.assertIn("<rect ", html_txt)
            self.assertIn("$28K", html_txt)
            self.assertTrue(out["lint"]["passed"])

    def test_deck_linter_detects_mismatched_problem_solution_bullets(self) -> None:
        deck = {
            "meta": {
                "companyName": "ClaimGuard",
                "fiOneSentencePitch": (
                    "My company, ClaimGuard, is developing billing software to help "
                    "independent dental clinics stop claim losses with automated payer checks."
                ),
            },
            "slides": [
                {"id": "problem", "type": "bullets", "headline": "Clinics Lose Money", "bullets": ["A", "B", "C"]},
                {"id": "solution", "type": "bullets", "headline": "We Recover Claims", "bullets": ["A", "B"]},
            ],
        }
        report = lint_deck(deck)
        rules = {i["rule"] for i in report["issues"]}
        self.assertIn("fi-problem-solution-mirror", rules)

    def test_scaffold_workspace_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            res = scaffold_workspace(
                workspace=td,
                company="ClaimGuard",
                offering="automated claim reconciliation software",
                audience="independent dental clinic managers",
                problem="recover $4,000/month in unbilled claims",
                secret_sauce="real-time regional payer-rule validation",
                impact_thesis="Keep community dental clinics financially healthy and accessible",
                ikpi="Dollars recovered for independent community clinics",
            )
            self.assertTrue(res["pitchLint"]["passed"])
            for fp in res["filesCreated"]:
                self.assertTrue(Path(fp).exists(), f"Expected scaffolded file: {fp}")
            state = json.loads((Path(td) / ".startup" / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["companyName"], "ClaimGuard")
            self.assertEqual(state["stage"], "idea")


if __name__ == "__main__":
    unittest.main()
