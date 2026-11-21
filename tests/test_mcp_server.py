"""End-to-end stdio JSON-RPC 2.0 tests for the startup-antigravity-os MCP server."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestMCPServer(unittest.TestCase):
    def _run_rpc(self, requests: list[dict]) -> list[dict]:
        env = {**os.environ, "PLUGIN_ROOT": str(ROOT)}
        proc = subprocess.Popen(
            [sys.executable, str(ROOT / "mcp_server" / "server.py")],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        payload = "\n".join(json.dumps(r) for r in requests) + "\n"
        out, err = proc.communicate(payload, timeout=15)
        self.assertEqual(proc.returncode, 0, f"Server stderr: {err}")
        return [json.loads(line) for line in out.splitlines() if line.strip()]

    def test_initialize_and_list_tools(self) -> None:
        resps = self._run_rpc(
            [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            ]
        )
        self.assertEqual(len(resps), 2)
        self.assertEqual(resps[0]["result"]["serverInfo"]["name"], "startup-antigravity-os")
        tool_names = {t["name"] for t in resps[1]["result"]["tools"]}
        self.assertEqual(len(tool_names), 17)
        self.assertIn("financial_calc", tool_names)
        self.assertIn("fi_pitch_lint", tool_names)
        self.assertIn("pact_pipeline_manage", tool_names)
        self.assertIn("landing_page_build", tool_names)
        self.assertIn("ikpi_catalog_search", tool_names)
        self.assertIn("sprint_manage", tool_names)
        self.assertIn("pitch_deck_design_brief", tool_names)
        self.assertIn("replit_workspace_prepare", tool_names)
        self.assertIn("product_hunt_kit_build", tool_names)
        self.assertIn("ai_connectors_manage", tool_names)
        self.assertIn("pmf_engine_manage", tool_names)

    def test_financial_calculators_deterministic(self) -> None:
        calls = [
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "financial_calc",
                    "arguments": {"mode": "fast_advisor_equity", "stage": "idea", "tier": "strategic"},
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": "financial_calc",
                    "arguments": {
                        "mode": "tam_bottom_up",
                        "total_buyers": 100000,
                        "annual_acv_usd": 12000,
                        "sam_pct": 25,
                        "som_buyers": 1000,
                    },
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "financial_calc",
                    "arguments": {
                        "mode": "unit_economics",
                        "arpa_monthly_usd": 500,
                        "gross_margin_pct": 80,
                        "monthly_churn_pct": 4,
                        "cac_usd": 1200,
                    },
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 4,
                "method": "tools/call",
                "params": {
                    "name": "financial_calc",
                    "arguments": {
                        "mode": "safe_dilution",
                        "raise_usd": 500000,
                        "valuation_cap_usd": 5000000,
                        "safe_type": "post_money",
                        "option_pool_pct": 10,
                        "founder_count": 2,
                    },
                },
            },
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {
                    "name": "financial_calc",
                    "arguments": {
                        "mode": "runway",
                        "cash_usd": 100000,
                        "monthly_burn_usd": 10000,
                        "monthly_revenue_usd": 8000,
                        "monthly_growth_pct": 15,
                        "gross_margin_pct": 80,
                    },
                },
            },
        ]
        resps = self._run_rpc(calls)
        fast = json.loads(resps[0]["result"]["content"][0]["text"])
        self.assertEqual(fast["recommendedEquityPct"], 0.5)
        self.assertEqual(fast["vestingScheduleMonths"], 24)

        tam = json.loads(resps[1]["result"]["content"][0]["text"])
        self.assertEqual(tam["tamUsd"], 1_200_000_000.0)
        self.assertEqual(tam["samUsd"], 300_000_000.0)
        self.assertEqual(tam["somUsd"], 12_000_000.0)

        ue = json.loads(resps[2]["result"]["content"][0]["text"])
        self.assertEqual(ue["ltvUsd"], 10_000.0)
        self.assertEqual(ue["cacPaybackMonths"], 3.0)

        safe = json.loads(resps[3]["result"]["content"][0]["text"])
        self.assertEqual(safe["investorOwnershipPct"], 10.0)
        self.assertEqual(safe["perFounderEqualSplitPct"], 40.0)

        runway = json.loads(resps[4]["result"]["content"][0]["text"])
        self.assertTrue(runway["defaultAlive"])

    def test_state_assumptions_interviews_and_pacts_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            calls = [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "startup_update_stage",
                        "arguments": {
                            "workspace_path": td,
                            "companyName": "ClaimGuard",
                            "stage": "validation",
                            "mrrUsd": 1500,
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "assumption_manage",
                        "arguments": {
                            "action": "add",
                            "workspace_path": td,
                            "statement": "Clinics pay $500/mo for automated claim checks",
                            "impact": 5,
                            "uncertainty": 4,
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "interview_manage",
                        "arguments": {
                            "action": "log",
                            "workspace_path": td,
                            "persona": "Dental Office Manager",
                            "pain_severity": 5,
                            "willingness_to_pay_usd": 600,
                            "pledged_pilot": True,
                            "verbatim_quote": "We lose $4K every month on missed rejections.",
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "pact_pipeline_manage",
                        "arguments": {
                            "action": "add",
                            "workspace_path": td,
                            "kind": "customer",
                            "counterparty": "BrightSmile Dental",
                            "amount_usd": 1500,
                            "status": "pact_signed",
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "startup_get_state",
                        "arguments": {"workspace_path": td},
                    },
                },
            ]
            resps = self._run_rpc(calls)
            state_resp = json.loads(resps[4]["result"]["content"][0]["text"])
            self.assertTrue(state_resp["initialized"])
            self.assertEqual(state_resp["telemetry"]["interviewsCount"], 1)
            self.assertEqual(state_resp["telemetry"]["customerPactsCommittedUsd"], 1500.0)
            self.assertEqual(state_resp["telemetry"]["topRiskyAssumption"]["riskScore"], 20)

    def test_v11_cap_table_ikpi_landing_page_and_sprints(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            calls = [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "startup_update_stage",
                        "arguments": {
                            "workspace_path": td,
                            "companyName": "ClaimGuard",
                            "stage": "mvp",
                            "mrrUsd": 4500,
                            "monthlyBurnUsd": 6000,
                            "cashOnHandUsd": 60000,
                            "fiOneSentencePitch": (
                                "My company, ClaimGuard, is developing claim reconciliation software "
                                "to help independent dental clinics recover $4,000/month with payer-rule checks."
                            ),
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "ikpi_catalog_search",
                        "arguments": {"query": "healthcare dental", "limit": 3},
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "financial_calc",
                        "arguments": {
                            "mode": "cap_table_model",
                            "founders": [{"name": "Alice", "pct": 50}, {"name": "Bob", "pct": 50}],
                            "advisors": [{"name": "FI Mentor", "pct": 1.0}],
                            "safe_raise_usd": 500000,
                            "safe_cap_usd": 5000000,
                            "seed_raise_usd": 2000000,
                            "seed_pre_money_usd": 8000000,
                            "seed_option_pool_pct": 10,
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "landing_page_build",
                        "arguments": {"workspace_path": td, "contact_email": "ceo@claimguard.io"},
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "sprint_manage",
                        "arguments": {
                            "action": "start",
                            "workspace_path": td,
                            "primary_goal": "Close 3 dental pilot PACTs worth $1,500 MRR",
                            "target_interviews": 10,
                            "target_pacts": 3,
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "tools/call",
                    "params": {
                        "name": "sprint_manage",
                        "arguments": {
                            "action": "close",
                            "workspace_path": td,
                            "interviews_completed": 11,
                            "pacts_sent": 5,
                            "pacts_signed": 3,
                            "mrr_delta_usd": 1500,
                            "fi_velocity_score": 4.5,
                            "highlights": ["Signed 3 clinics on paid pilot PACTs"],
                            "lowlights": ["Onboarding took 25 mins instead of 10 mins"],
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 7,
                    "method": "tools/call",
                    "params": {
                        "name": "sprint_manage",
                        "arguments": {
                            "action": "investor_update",
                            "workspace_path": td,
                            "asks": ["Intro to multi-clinic dental groups"],
                        },
                    },
                },
            ]
            resps = self._run_rpc(calls)
            ikpi = json.loads(resps[1]["result"]["content"][0]["text"])
            self.assertGreater(ikpi["matchCount"], 0)
            self.assertEqual(ikpi["matches"][0]["sdgNumber"], 3)

            cap = json.loads(resps[2]["result"]["content"][0]["text"])
            self.assertEqual(cap["seedPostMoneyValuationUsd"], 10_000_000.0)
            self.assertGreater(cap["foundersFinalCombinedPct"], 60.0)

            lp = json.loads(resps[3]["result"]["content"][0]["text"])
            lp_html = Path(lp["htmlPath"]).read_text(encoding="utf-8")
            self.assertIn("ClaimGuard", lp_html)
            self.assertIn("Calculate Your Monthly ROI", lp_html)
            self.assertIn("ceo@claimguard.io", lp_html)

            upd = json.loads(resps[6]["result"]["content"][0]["text"])
            upd_md = Path(upd["updatePath"]).read_text(encoding="utf-8")
            self.assertIn("Signed 3 clinics on paid pilot PACTs", upd_md)
            self.assertIn("Intro to multi-clinic dental groups", upd_md)

    def test_replit_workspace_prepare_web_and_mobile(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            resps = self._run_rpc(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "replit_workspace_prepare",
                            "arguments": {
                                "workspace_path": td,
                                "app_type": "mobile-expo",
                                "company_name": "ClaimGuard Mobile",
                            },
                        },
                    }
                ]
            )
            out = json.loads(resps[0]["result"]["content"][0]["text"])
            self.assertEqual(out["appType"], "mobile-expo")
            self.assertEqual(out["replitSignupUrl"], "https://replit.com/refer/peterbiggam")
            for fp in out["filesCreated"]:
                self.assertTrue(Path(fp).exists(), f"Missing Replit file: {fp}")
            dot_replit = (Path(td) / ".replit").read_text(encoding="utf-8")
            replit_md = (Path(td) / "replit.md").read_text(encoding="utf-8")
            handoff = (Path(td) / "docs" / "REPLIT_HANDOFF.md").read_text(encoding="utf-8")
            self.assertIn("expo start", dot_replit)
            self.assertIn("Zero Double-Token Burn", replit_md)
            self.assertIn("https://replit.com/refer/peterbiggam", handoff)

    def test_product_hunt_kit_build_and_linter(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            resps = self._run_rpc(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "product_hunt_kit_build",
                            "arguments": {
                                "workspace_path": td,
                                "product_name": "ClaimGuard",
                                "tagline": "Recover $4K/mo in denied dental claims automatically",
                                "topics": ["SaaS", "HealthTech", "Productivity"],
                            },
                        },
                    },
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {
                            "name": "product_hunt_kit_build",
                            "arguments": {
                                "workspace_path": td,
                                "product_name": "ClaimGuard",
                                "tagline": "A revolutionary disruptive world-class AI platform that exceeds sixty characters easily",
                            },
                        },
                    },
                ]
            )
            ok_out = json.loads(resps[0]["result"]["content"][0]["text"])
            self.assertTrue(ok_out["lint"]["passed"])
            kit_md = Path(ok_out["kitPath"]).read_text(encoding="utf-8")
            self.assertIn("1270 x 760 px", kit_md)
            self.assertIn("Zero upvote rings", kit_md)

            bad_out = json.loads(resps[1]["result"]["content"][0]["text"])
            self.assertFalse(bad_out["lint"]["passed"])
            rules = {i["rule"] for i in bad_out["lint"]["issues"]}
            self.assertIn("ph-tagline-60", rules)
            self.assertIn("fi-no-buzzwords", rules)

    def test_ai_connectors_detect_sync_and_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            resps = self._run_rpc(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "tools/call",
                        "params": {
                            "name": "startup_update_stage",
                            "arguments": {
                                "workspace_path": td,
                                "companyName": "ClaimGuard",
                                "stage": "validation",
                                "fiOneSentencePitch": (
                                    "My company, ClaimGuard, is developing billing software to help "
                                    "independent dental clinics recover $4K/mo with payer-rule checks."
                                ),
                            },
                        },
                    },
                    {
                        "jsonrpc": "2.0",
                        "id": 2,
                        "method": "tools/call",
                        "params": {"name": "ai_connectors_manage", "arguments": {"action": "detect"}},
                    },
                    {
                        "jsonrpc": "2.0",
                        "id": 3,
                        "method": "tools/call",
                        "params": {
                            "name": "ai_connectors_manage",
                            "arguments": {"action": "sync_context", "workspace_path": td, "targets": ["all"]},
                        },
                    },
                    {
                        "jsonrpc": "2.0",
                        "id": 4,
                        "method": "tools/call",
                        "params": {
                            "name": "ai_connectors_manage",
                            "arguments": {
                                "action": "second_opinion",
                                "workspace_path": td,
                                "provider": "xai",
                                "prompt": "Tear apart our positioning and give 3 blunt improvements.",
                                "dry_run": True,
                            },
                        },
                    },
                ]
            )
            det = json.loads(resps[1]["result"]["content"][0]["text"])
            self.assertIn("xai", det["apis"])
            self.assertIn("claude-cli", det["clis"])
            self.assertIn("ollama", det["clis"])

            synced = json.loads(resps[2]["result"]["content"][0]["text"])
            self.assertEqual(len(synced["filesWritten"]), 3)
            self.assertIn("ClaimGuard", (Path(td) / "CLAUDE.md").read_text(encoding="utf-8"))
            self.assertIn("xAI / Grok", (Path(td) / "docs" / "GROK_CONTEXT.md").read_text(encoding="utf-8"))
            self.assertIn("Universal Multi-AI", (Path(td) / "docs" / "AI_CONTEXT_PACK.md").read_text(encoding="utf-8"))

            dry = json.loads(resps[3]["result"]["content"][0]["text"])
            self.assertEqual(dry["mode"], "dry_run")
            self.assertIn("ClaimGuard", dry["readyPrompt"])

    def test_pmf_engine_segmentation_retention_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            calls = [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "pmf_engine_manage",
                        "arguments": {
                            "action": "log_survey",
                            "workspace_path": td,
                            "user_segment": "Independent Dental Clinics",
                            "disappointment": "very_disappointed",
                            "main_benefit": "Recovers $4K/mo in rejected claims automatically",
                            "paying": True,
                            "referred_someone": True,
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "pmf_engine_manage",
                        "arguments": {
                            "action": "log_survey",
                            "workspace_path": td,
                            "user_segment": "Independent Dental Clinics",
                            "disappointment": "very_disappointed",
                            "main_benefit": "Saves 10 hours/week of billing reconciliation",
                            "paying": True,
                            "referred_someone": False,
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "pmf_engine_manage",
                        "arguments": {
                            "action": "log_survey",
                            "workspace_path": td,
                            "user_segment": "Solo Hobbyists",
                            "disappointment": "somewhat_disappointed",
                            "requested_improvement": "Faster CSV import",
                            "paying": False,
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "pmf_engine_manage",
                        "arguments": {
                            "action": "log_survey",
                            "workspace_path": td,
                            "user_segment": "Solo Hobbyists",
                            "disappointment": "not_disappointed",
                            "paying": False,
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {
                        "name": "pmf_engine_manage",
                        "arguments": {
                            "action": "record_retention",
                            "workspace_path": td,
                            "cohort_label": "2026-Q3",
                            "cohort_size": 25,
                            "day7_pct": 88,
                            "day30_pct": 80,
                            "day90_pct": 76,
                            "net_dollar_retention_pct": 112,
                        },
                    },
                },
                {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "tools/call",
                    "params": {
                        "name": "pmf_engine_manage",
                        "arguments": {"action": "generate_report", "workspace_path": td},
                    },
                },
            ]
            resps = self._run_rpc(calls)
            rep = json.loads(resps[5]["result"]["content"][0]["text"])
            sc = rep["scorecard"]
            self.assertEqual(sc["seanEllisScorePct"], 50.0)
            self.assertEqual(sc["verdict"], "PMF_PROVEN_READY_TO_SCALE")
            self.assertTrue(sc["retentionFlattening"])
            self.assertEqual(sc["strongestSegment"]["segment"], "Independent Dental Clinics")
            self.assertEqual(sc["strongestSegment"]["pmfScorePct"], 100.0)
            md = Path(rep["reportPath"]).read_text(encoding="utf-8")
            self.assertIn("Superhuman 50/50 PMF Roadmap", md)
            self.assertIn("Faster CSV import", md)


if __name__ == "__main__":
    unittest.main()
