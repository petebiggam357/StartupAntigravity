"""Contract tests for all 4 Antigravity lifecycle hooks (camelCase stdin -> JSON stdout)."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run_hook(script_rel: str, payload: dict) -> dict:
    proc = subprocess.run(
        [sys.executable, str(ROOT / script_rel)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        timeout=15,
        check=True,
    )
    return json.loads(proc.stdout)


class TestHooks(unittest.TestCase):
    def test_session_bootstrap_uninitialized_and_initialized(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            # Uninitialized workspace -> kickstart hint
            out1 = _run_hook("hooks/session_bootstrap.py", {"workspacePaths": [td]})
            msg1 = out1["injectSteps"][0]["systemMessage"]["systemMessage"]
            self.assertIn("startup-kickstart", msg1)

            # Initialized workspace -> Founder Pulse
            sdir = Path(td) / ".startup"
            sdir.mkdir()
            (sdir / "state.json").write_text(
                json.dumps(
                    {
                        "companyName": "ClaimGuard",
                        "stage": "validation",
                        "mrrUsd": 2000,
                        "ikpi": {"name": "Claims Recovered", "current": 12, "target": 100},
                    }
                ),
                encoding="utf-8",
            )
            out2 = _run_hook("hooks/session_bootstrap.py", {"workspacePaths": [td]})
            msg2 = out2["injectSteps"][0]["systemMessage"]["systemMessage"]
            self.assertIn("ClaimGuard", msg2)
            self.assertIn("validation", msg2)

    def test_session_bootstrap_skips_plugin_own_repo(self) -> None:
        out = _run_hook("hooks/session_bootstrap.py", {"workspacePaths": [str(ROOT)]})
        self.assertEqual(out, {})

    def test_pre_tool_guard_blocks_secrets_and_nudges_early_infra(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            sdir = Path(td) / ".startup"
            sdir.mkdir()
            (sdir / "state.json").write_text(json.dumps({"stage": "validation"}), encoding="utf-8")

            # Secret leak -> deny
            out_deny = _run_hook(
                "hooks/pre_tool_guard.py",
                {
                    "workspacePaths": [td],
                    "toolCall": {"name": "run_command", "args": {"CommandLine": "git add .env"}},
                },
            )
            self.assertEqual(out_deny["decision"], "deny")

            # Early-stage heavy infra -> ask
            out_ask = _run_hook(
                "hooks/pre_tool_guard.py",
                {
                    "workspacePaths": [td],
                    "toolCall": {"name": "run_command", "args": {"CommandLine": "terraform apply -auto-approve"}},
                },
            )
            self.assertEqual(out_ask["decision"], "ask")

            # Normal command -> allow
            out_ok = _run_hook(
                "hooks/pre_tool_guard.py",
                {
                    "workspacePaths": [td],
                    "toolCall": {"name": "run_command", "args": {"CommandLine": "pytest"}},
                },
            )
            self.assertEqual(out_ok["decision"], "allow")

            # Mainnet broadcast -> ask
            out_mainnet = _run_hook(
                "hooks/pre_tool_guard.py",
                {
                    "workspacePaths": [td],
                    "toolCall": {
                        "name": "run_command",
                        "args": {"CommandLine": "forge script Deploy.s.sol --rpc-url base --broadcast"},
                    },
                },
            )
            self.assertEqual(out_mainnet["decision"], "ask")

            # Hardcoded wallet private key in write_file -> deny
            out_key = _run_hook(
                "hooks/pre_tool_guard.py",
                {
                    "workspacePaths": [td],
                    "toolCall": {
                        "name": "write_file",
                        "args": {
                            "Path": f"{td}/src/config.py",
                            "Content": "WALLET_PRIVATE_KEY = '0x" + ("a" * 64) + "'",
                        },
                    },
                },
            )
            self.assertEqual(out_key["decision"], "deny")

            # Raw email written into data-room/ -> ask
            out_pii = _run_hook(
                "hooks/pre_tool_guard.py",
                {
                    "workspacePaths": [td],
                    "toolCall": {
                        "name": "write_file",
                        "args": {
                            "Path": f"{td}/data-room/04_Pipeline_and_Proof/notes.md",
                            "Content": "Buyer contact: alice@bigcorp.com",
                        },
                    },
                },
            )
            self.assertEqual(out_pii["decision"], "ask")

    def test_post_deck_rebuild_compiles_html_and_md(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pdir = Path(td) / "pitch-deck"
            pdir.mkdir()
            deck_json = pdir / "deck.json"
            tpl = ROOT / "skills" / "pitch-deck-builder" / "resources" / "deck.problem-solution.json"
            deck_json.write_text(tpl.read_text(encoding="utf-8"), encoding="utf-8")

            # Also seed .startup/state.json + existing data-room/index.html to verify auto-sync
            sdir = Path(td) / ".startup"
            sdir.mkdir()
            state_json = sdir / "state.json"
            state_json.write_text(json.dumps({"companyName": "SyncCo", "stage": "mvp"}), encoding="utf-8")
            dr_dir = Path(td) / "data-room"
            dr_dir.mkdir()
            (dr_dir / "index.html").write_text("old", encoding="utf-8")

            out = _run_hook(
                "hooks/post_deck_rebuild.py",
                {
                    "workspacePaths": [td],
                    "toolCall": {"name": "write_file", "args": {"Path": str(deck_json)}},
                },
            )
            self.assertEqual(out, {})
            self.assertTrue((pdir / "index.html").exists())
            self.assertTrue((pdir / "DECK.md").exists())
            self.assertIn("SyncCo", (dr_dir / "index.html").read_text(encoding="utf-8"))

    def test_stop_integrity_check_and_loop_guard(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            pdir = Path(td) / "pitch-deck"
            pdir.mkdir()
            (pdir / "deck.json").write_text("{ broken json", encoding="utf-8")

            out_cont = _run_hook(
                "hooks/stop_integrity_check.py",
                {
                    "workspacePaths": [td],
                    "terminationReason": "NO_TOOL_CALL",
                    "continuationActive": False,
                },
            )
            self.assertEqual(out_cont["decision"], "continue")
            self.assertIn("pitch-deck/deck.json", out_cont["reason"])

            # When continuationActive is True, must NOT loop
            out_stop = _run_hook(
                "hooks/stop_integrity_check.py",
                {
                    "workspacePaths": [td],
                    "terminationReason": "NO_TOOL_CALL",
                    "continuationActive": True,
                },
            )
            self.assertEqual(out_stop, {})

        # Stale dashboard drift check
        with tempfile.TemporaryDirectory() as td:
            import os

            sdir = Path(td) / ".startup"
            sdir.mkdir()
            ddir = Path(td) / "dashboard"
            ddir.mkdir()
            dash = ddir / "index.html"
            state = sdir / "state.json"
            dash.write_text("<html>old</html>", encoding="utf-8")
            state.write_text(json.dumps({"companyName": "DriftCo", "stage": "mvp"}), encoding="utf-8")
            os.utime(dash, (1_700_000_000, 1_700_000_000))
            os.utime(state, (1_700_000_100, 1_700_000_100))

            out_drift = _run_hook(
                "hooks/stop_integrity_check.py",
                {
                    "workspacePaths": [td],
                    "terminationReason": "NO_TOOL_CALL",
                    "continuationActive": False,
                },
            )
            self.assertEqual(out_drift["decision"], "continue")
            self.assertIn("dashboard/index.html", out_drift["reason"])


if __name__ == "__main__":
    unittest.main()
