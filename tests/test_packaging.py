"""Tests for Startup Antigravity native app launcher, .deb/AppDir packager, and release CI."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class TestNativeAppPackages(unittest.TestCase):
    def test_launcher_cli_install_status_and_uninstall(self) -> None:
        # Ensure fresh release ZIP exists
        res_pkg = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "package_release.py")],
            check=True,
            capture_output=True,
            text=True,
        )
        zip_path = Path(json.loads(res_pkg.stdout)["archive"])
        self.assertTrue(zip_path.exists())

        with tempfile.TemporaryDirectory() as tmp:
            plugin_dir = Path(tmp) / "startup-antigravity"

            # --version
            ver_out = subprocess.run(
                [sys.executable, str(ROOT / "launcher" / "app.py"), "--version"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("startup-antigravity", ver_out.stdout)

            # --status before install
            st_before = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "launcher" / "app.py"),
                    "--status",
                    "--plugin-dir",
                    str(plugin_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            before_data = json.loads(st_before.stdout)
            self.assertFalse(before_data["installed"])

            # --install offline from bundled ZIP
            inst = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "launcher" / "app.py"),
                    "--install",
                    "--plugin-dir",
                    str(plugin_dir),
                    "--zip",
                    str(zip_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            inst_data = json.loads(inst.stdout)
            self.assertTrue(inst_data["ok"])
            self.assertTrue((plugin_dir / "plugin.json").exists())
            self.assertTrue((plugin_dir / "mcp_server" / "server.py").exists())
            self.assertTrue((plugin_dir / "hooks.json").exists())

            # --status after install
            st_after = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "launcher" / "app.py"),
                    "--status",
                    "--plugin-dir",
                    str(plugin_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            after_data = json.loads(st_after.stdout)
            self.assertTrue(after_data["installed"])
            self.assertEqual(after_data["installedVersion"], inst_data["installedVersion"])

            # --uninstall
            uninst = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "launcher" / "app.py"),
                    "--uninstall",
                    "--plugin-dir",
                    str(plugin_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertTrue(json.loads(uninst.stdout)["removed"])
            self.assertFalse(plugin_dir.exists())

    def test_build_packages_appdir_deb_and_checksums(self) -> None:
        res = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_packages.py"), "--target", "all"],
            check=True,
            capture_output=True,
            text=True,
        )
        data = json.loads(res.stdout)
        artifact_types = {a["type"]: Path(a["path"]) for a in data["artifacts"]}
        self.assertIn("zip", artifact_types)
        self.assertIn("appdir", artifact_types)
        self.assertTrue(artifact_types["zip"].exists())

        # Verify AppDir structure
        appdir = artifact_types["appdir"]
        self.assertTrue((appdir / "AppRun").exists())
        self.assertTrue((appdir / "startup-antigravity.desktop").exists())
        self.assertTrue((appdir / "startup-antigravity.svg").exists())
        self.assertTrue((appdir / ".DirIcon").exists())
        bundled_zips = list((appdir / "usr" / "share" / "startup-antigravity").glob("*.zip"))
        self.assertEqual(len(bundled_zips), 1)

        # Verify .deb if dpkg-deb is installed on this host
        if shutil.which("dpkg-deb"):
            self.assertIn("deb", artifact_types)
            deb_path = artifact_types["deb"]
            self.assertTrue(deb_path.exists())
            contents = subprocess.run(
                ["dpkg-deb", "--contents", str(deb_path)],
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            self.assertIn("./usr/bin/startup-antigravity", contents)
            self.assertIn("./usr/share/applications/startup-antigravity.desktop", contents)
            self.assertIn("./usr/share/icons/hicolor/scalable/apps/startup-antigravity.svg", contents)

        # Verify SHA256SUMS.txt
        checksums = Path(data["checksums"])
        self.assertTrue(checksums.exists())
        self.assertIn(artifact_types["zip"].name, checksums.read_text(encoding="utf-8"))

    def test_release_workflow_covers_all_native_platforms(self) -> None:
        wf = ROOT / ".github" / "workflows" / "release.yml"
        self.assertTrue(wf.exists())
        text = wf.read_text(encoding="utf-8")
        for token in (
            "build-linux",
            "build-macos",
            "build-windows",
            "publish-release",
            "appimagetool",
            ".AppImage",
            "_all.deb",
            "-macos-arm64.dmg",
            "-win64.exe",
            "SHA256SUMS.txt",
            "generate_app_icons.py",
            "startup-antigravity.icns",
            "startup-antigravity.ico",
        ):
            self.assertIn(token, text, f"release.yml missing {token}")

    def test_demo_workspace_generator_and_launcher_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            demo_dir = Path(tmp) / "solarledger-demo"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "launcher" / "app.py"),
                    "--demo",
                    str(demo_dir),
                    "--no-browser",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            res = json.loads(proc.stdout)
            self.assertTrue(res["ok"])
            self.assertEqual(res["slideCount"], 13)
            self.assertTrue(res["deckLintPassed"], "Demo 13-slide pitch deck must pass FI linter cleanly")
            self.assertTrue(Path(res["dashboardHtml"]).exists())
            self.assertTrue(Path(res["pitchDeckHtml"]).exists())
            self.assertTrue(Path(res["landingHtml"]).exists())
            self.assertTrue(Path(res["dataRoomHtml"]).exists())
            self.assertEqual(res["dataRoomReadinessPct"], 100)

        # Verify --prompts CLI returns all 6 starter prompts
        prompts_proc = subprocess.run(
            [sys.executable, str(ROOT / "launcher" / "app.py"), "--prompts"],
            check=True,
            capture_output=True,
            text=True,
        )
        prompts = json.loads(prompts_proc.stdout)
        self.assertGreaterEqual(len(prompts), 6)
        self.assertTrue(any("x402" in p["prompt"] for p in prompts))

    def test_local_web_studio_server_and_pages_site_and_community_kit(self) -> None:
        import threading
        import urllib.error
        import urllib.request

        sys.path.insert(0, str(ROOT / "launcher"))
        from studio_server import create_studio_server  # noqa: E402

        with tempfile.TemporaryDirectory() as tmp:
            demo_dir = Path(tmp) / "demo"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "generate_demo_workspace.py"), "--output", str(demo_dir)],
                check=True,
                capture_output=True,
                text=True,
            )

            server = create_studio_server(demo_dir, plugin_root=ROOT, port=0)
            port = server.server_address[1]
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            try:
                base = f"http://127.0.0.1:{port}"
                shell = urllib.request.urlopen(base + "/").read().decode("utf-8")
                self.assertIn("STARTUP ANTIGRAVITY STUDIO", shell)
                self.assertIn("ClaimPulse", shell)

                health = json.loads(urllib.request.urlopen(base + "/api/health").read().decode("utf-8"))
                self.assertTrue(health["ok"])
                self.assertGreaterEqual(health["resourceCount"], 48)

                res = json.loads(urllib.request.urlopen(base + "/api/resources?q=x402").read().decode("utf-8"))
                self.assertGreaterEqual(res["count"], 2)

                dash = urllib.request.urlopen(base + "/workspace/dashboard/index.html").read().decode("utf-8")
                self.assertIn("Startup <span>Command Center</span>", dash)
                self.assertIn("ClaimPulse", dash)
                self.assertIn("83.6/100", dash)
                self.assertIn("6Ds Stage: Disruptive", dash)
                self.assertIn("what-if-simulator", dash)

                dr_html = urllib.request.urlopen(base + "/workspace/data-room/index.html").read().decode("utf-8")
                self.assertIn("DR_I18N", dr_html)
                self.assertIn("downloadReport", shell)
                self.assertIn("updateOnboardPreview", shell)
                self.assertIn("addEditorSlide", shell)
                self.assertIn("moveEditorSlide", shell)

                # Weekly Rhythm & Snapshot Export Studio APIs
                req_ry = urllib.request.Request(
                    base + "/api/weekly-rhythm",
                    data=json.dumps({"action": "friday_digest"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                ry_res = json.loads(urllib.request.urlopen(req_ry).read().decode("utf-8"))
                self.assertTrue(ry_res["ok"])
                self.assertIn("Founder Friday Update", ry_res["markdown"])

                snap = json.loads(urllib.request.urlopen(base + "/api/export-snapshot").read().decode("utf-8"))
                self.assertTrue(snap["ok"])
                self.assertIn("state.json", snap["startup"])
                self.assertIsNotNone(snap["deck"])

                # Live 3-Lens Board Review API
                br = json.loads(urllib.request.urlopen(base + "/api/board-review").read().decode("utf-8"))
                self.assertTrue(br["ok"])
                self.assertGreaterEqual(br["overallScore"], 4.0)

                # Live Metered x402 Storefront: unpaid -> HTTP 402, paid -> HTTP 200 + ledger increment
                req_unpaid = urllib.request.Request(
                    base + "/api/x402/agent-call",
                    data=json.dumps({"query": "test"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with self.assertRaises(urllib.error.HTTPError) as ctx402:
                    urllib.request.urlopen(req_unpaid)
                self.assertEqual(ctx402.exception.code, 402)
                self.assertTrue(ctx402.exception.headers.get("X-PAYMENT-REQUIRED"))

                req_paid = urllib.request.Request(
                    base + "/api/x402/agent-call",
                    data=json.dumps({"query": "test"}).encode("utf-8"),
                    headers={"Content-Type": "application/json", "X-PAYMENT": "demo-usdc-proof", "X-AGENT-ID": "test-bot"},
                    method="POST",
                )
                paid_res = json.loads(urllib.request.urlopen(req_paid).read().decode("utf-8"))
                self.assertTrue(paid_res["ok"])
                self.assertGreaterEqual(paid_res["totalCalls"], 143)

                # Live Voice Coach & War Room Studio APIs
                req_vc = urllib.request.Request(
                    base + "/api/voice-coach",
                    data=json.dumps({"transcript": "ClaimPulse cuts dental denials to 3% with $14,400 MRR raising $750K.", "duration_seconds": 30}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                vc_res = json.loads(urllib.request.urlopen(req_vc).read().decode("utf-8"))
                self.assertTrue(vc_res["ok"])

                req_wr = urllib.request.Request(
                    base + "/api/war-room",
                    data=json.dumps({"question": "Should we hire 2 engineers now?"}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                wr_res = json.loads(urllib.request.urlopen(req_wr).read().decode("utf-8"))
                self.assertTrue(wr_res["ok"])
                self.assertEqual(len(wr_res["perspectives"]), 4)

                # Path-traversal guard
                with self.assertRaises(urllib.error.HTTPError) as ctx:
                    urllib.request.urlopen(base + "/workspace/../../etc/passwd")
                self.assertEqual(ctx.exception.code, 403)

                # Live metric update via POST /api/metrics
                req_m = urllib.request.Request(
                    base + "/api/metrics",
                    data=json.dumps({"mrrUsd": 12500, "grossMarginPct": 86}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                m_res = json.loads(urllib.request.urlopen(req_m).read().decode("utf-8"))
                self.assertTrue(m_res["ok"])
                self.assertEqual(m_res["state"]["metrics"]["mrrUsd"], 12500.0)

                # Visual Slide Editor GET /api/deck + 1-Click Publish Live POST /api/publish
                dk = json.loads(urllib.request.urlopen(base + "/api/deck").read().decode("utf-8"))
                self.assertTrue(dk["ok"])
                self.assertEqual(len(dk["deck"]["slides"]), 13)

                req_pub = urllib.request.Request(
                    base + "/api/publish",
                    data=json.dumps({"include_data_room": False}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                pub_res = json.loads(urllib.request.urlopen(req_pub).read().decode("utf-8"))
                self.assertTrue(pub_res["ok"])
                self.assertTrue((Path(pub_res["publishDir"]) / "deck" / "index.html").exists())
            finally:
                server.shutdown()
                server.server_close()

            # Test Mentor & Accelerator Cohort Portfolio Mode (--portfolio)
            port_proc = subprocess.run(
                [sys.executable, str(ROOT / "launcher" / "app.py"), "--portfolio", str(Path(tmp)), "--no-browser"],
                check=True,
                capture_output=True,
                text=True,
            )
            port_res = json.loads(port_proc.stdout)
            self.assertTrue(port_res["ok"])
            self.assertGreaterEqual(port_res["startupCount"], 1)
            self.assertTrue(Path(port_res["htmlPath"]).exists())

            # Verify SHA-256 helper used by --update
            from app import verify_sha256_file  # noqa: E402
            import hashlib

            sample_f = Path(tmp) / "sample.bin"
            sample_f.write_bytes(b"startup-antigravity-beta")
            good_hash = hashlib.sha256(b"startup-antigravity-beta").hexdigest()
            self.assertTrue(verify_sha256_file(sample_f, good_hash))
            self.assertFalse(verify_sha256_file(sample_f, "0" * 64))

            # Verify --doctor preflight CLI checks Python, manifest, hooks & live 25-tool MCP handshake
            doc_proc = subprocess.run(
                [sys.executable, str(ROOT / "launcher" / "app.py"), "--doctor"],
                check=True,
                capture_output=True,
                text=True,
            )
            doc = json.loads(doc_proc.stdout)
            self.assertTrue(doc["ok"])
            self.assertTrue(doc["mcpHandshakeOk"])
            self.assertGreaterEqual(doc["mcpToolCount"], 25)

            # Build public GitHub Pages site + live demo
            site_dir = Path(tmp) / "site_dist"
            site_proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_site.py"), "--out-dir", str(site_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
            site_res = json.loads(site_proc.stdout)
            self.assertTrue(Path(site_res["indexHtml"]).exists())
            self.assertTrue((site_dir / ".nojekyll").exists())
            self.assertTrue((site_dir / "demo" / "dashboard" / "index.html").exists())
            self.assertTrue((site_dir / "demo" / "data-room" / "index.html").exists())

        # Community & trust kit files
        for rel in (
            "CONTRIBUTING.md",
            "SECURITY.md",
            ".github/workflows/pages.yml",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/feature_request.md",
            ".github/ISSUE_TEMPLATE/resource_submission.md",
        ):
            self.assertTrue((ROOT / rel).exists(), f"Missing {rel}")

    def test_v050_snapshot_import_validation_and_backup(self) -> None:
        import threading
        import urllib.error
        import urllib.request

        sys.path.insert(0, str(ROOT / "launcher"))
        from studio_server import create_studio_server  # noqa: E402

        with tempfile.TemporaryDirectory() as tmp:
            demo_dir = Path(tmp) / "demo"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "generate_demo_workspace.py"), "--output", str(demo_dir)],
                check=True,
                capture_output=True,
                text=True,
            )

            server = create_studio_server(demo_dir, plugin_root=ROOT, port=0)
            port = server.server_address[1]
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            try:
                base = f"http://127.0.0.1:{port}"
                original_snap = json.loads(urllib.request.urlopen(base + "/api/export-snapshot").read().decode("utf-8"))
                original_mrr = original_snap["startup"]["state.json"]["metrics"]["mrrUsd"]

                # Mutate MRR before restore so we can verify both restore and pre-restore backup
                req_mut = urllib.request.Request(
                    base + "/api/metrics",
                    data=json.dumps({"mrrUsd": 99999}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                urllib.request.urlopen(req_mut)

                # Reject invalid snapshot schemas (path traversal, bad extension, empty, bad deck)
                bad_payloads = [
                    {},
                    {"startup": {"../evil.json": {"a": 1}}},
                    {"startup": {"state.txt": {"a": 1}}},
                    {"startup": {"state.json": ["not-a-dict"]}},
                    {"startup": {}, "deck": {"slides": "not-a-list"}},
                ]
                for bad in bad_payloads:
                    req_bad = urllib.request.Request(
                        base + "/api/import-snapshot",
                        data=json.dumps(bad).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with self.assertRaises(urllib.error.HTTPError) as ctx_bad:
                        urllib.request.urlopen(req_bad)
                    self.assertEqual(ctx_bad.exception.code, 400)

                # Valid restore succeeds, restores original MRR, and writes pre-restore backup
                req_ok = urllib.request.Request(
                    base + "/api/import-snapshot",
                    data=json.dumps(original_snap).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                res_ok = json.loads(urllib.request.urlopen(req_ok).read().decode("utf-8"))
                self.assertTrue(res_ok["ok"])
                self.assertTrue(res_ok["deckRestored"])
                self.assertIn("state.json", res_ok["restoredStartupFiles"])

                backup_path = Path(res_ok["backupPath"])
                self.assertTrue(backup_path.exists())
                backup_data = json.loads(backup_path.read_text(encoding="utf-8"))
                self.assertEqual(backup_data["startup"]["state.json"]["metrics"]["mrrUsd"], 99999.0)

                restored_state = json.loads((demo_dir / ".startup" / "state.json").read_text(encoding="utf-8"))
                self.assertEqual(restored_state["metrics"]["mrrUsd"], original_mrr)
            finally:
                server.shutdown()
                server.server_close()

    def test_v050_studio_portfolio_warroom_presets_voice_rehearsal_and_themes(self) -> None:
        import threading
        import urllib.request

        sys.path.insert(0, str(ROOT / "launcher"))
        from studio_server import create_studio_server  # noqa: E402

        with tempfile.TemporaryDirectory() as tmp:
            cohort = Path(tmp) / "cohort"
            ws1 = cohort / "claimpulse"
            ws2 = cohort / "solarledger"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "generate_demo_workspace.py"), "--output", str(ws1)],
                check=True,
                capture_output=True,
                text=True,
            )
            (ws2 / ".startup").mkdir(parents=True, exist_ok=True)
            (ws2 / ".startup" / "state.json").write_text(
                json.dumps({"companyName": "SolarLedger", "stage": "mvp", "metrics": {"mrrUsd": 8200, "grossMarginPct": 82}}),
                encoding="utf-8",
            )

            server = create_studio_server(ws1, plugin_root=ROOT, port=0)
            port = server.server_address[1]
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            try:
                base = f"http://127.0.0.1:{port}"
                shell = urllib.request.urlopen(base + "/").read().decode("utf-8")
                for marker in (
                    "importSnapshotFile",
                    "switchDeckTheme",
                    "runWarRoomPreset",
                    "loadPortfolio",
                    "updateLiveVoiceTelemetry",
                    "vc-live-wpm",
                    "vc-live-fillers",
                    'value="midnight"',
                    'value="ivory"',
                    'value="emerald"',
                    'value="crimson"',
                ):
                    self.assertIn(marker, shell, f"Studio shell missing {marker}")

                # Embedded Cohort Portfolio API
                pf = json.loads(urllib.request.urlopen(base + "/api/portfolio").read().decode("utf-8"))
                self.assertTrue(pf["ok"])
                self.assertEqual(pf["startupCount"], 2)
                self.assertIsNone(pf["htmlPath"])
                names = {c["name"] for c in pf["companies"]}
                self.assertIn("ClaimPulse", names)
                self.assertIn("SolarLedger", names)

                # War Room Scenario Presets
                for prompt, expected_snippet in (
                    ("Pricing Shock: Should we raise ACV by 35%?", "price war"),
                    ("Runway Crunch: Cash runway drops below 9 months", "Runway defense"),
                    ("Pivot Audit: Should we pivot to an adjacent ICP?", "pivot"),
                ):
                    req = urllib.request.Request(
                        base + "/api/war-room",
                        data=json.dumps({"question": prompt}).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    wr = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
                    self.assertTrue(wr["ok"])
                    self.assertEqual(len(wr["perspectives"]), 4)
                    combined = " ".join(p["argument"].lower() for p in wr["perspectives"])
                    self.assertIn(expected_snippet.lower(), combined)

                # Live Theme Switching via POST /api/deck
                dk = json.loads(urllib.request.urlopen(base + "/api/deck").read().decode("utf-8"))["deck"]
                for preset, expected_bg in (
                    ("midnight", "#0B1120"),
                    ("ivory", "#FAF8F5"),
                    ("emerald", "#041410"),
                    ("crimson", "#14080C"),
                ):
                    dk["theme"] = {"preset": preset}
                    req_dk = urllib.request.Request(
                        base + "/api/deck",
                        data=json.dumps({"deck": dk}).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    res_dk = json.loads(urllib.request.urlopen(req_dk).read().decode("utf-8"))
                    self.assertTrue(res_dk["ok"])
                    compiled = (ws1 / "pitch-deck" / "index.html").read_text(encoding="utf-8")
                    self.assertIn(expected_bg, compiled)
            finally:
                server.shutdown()
                server.server_close()

    def test_v050_single_file_investor_portal_and_pages_smoke_test(self) -> None:
        sys.path.insert(0, str(ROOT / "skills" / "vc-lab-fundraising-os" / "scripts"))
        from build_data_room import build_data_room  # noqa: E402

        with tempfile.TemporaryDirectory() as tmp:
            demo_dir = Path(tmp) / "demo"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "generate_demo_workspace.py"), "--output", str(demo_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
            dr = build_data_room(demo_dir)
            self.assertTrue(dr["ok"])
            self.assertTrue(dr["singleFilePortal"])
            self.assertEqual(dr["embeddedSlideCount"], 13)
            portal_html = Path(dr["portalHtml"]).read_text(encoding="utf-8")
            for marker in (
                "sec-overview",
                "sec-deck",
                "sec-financials",
                "sec-pacts",
                "sec-diligence",
                "PORTAL_SLIDES",
                "renderFinancialModel",
                "Investor Due-Diligence Q&amp;A",
                "For-Progress Impact Ledger",
                "DR_I18N",
            ):
                self.assertIn(marker, portal_html, f"Single-file Investor Portal missing {marker}")

        # Run automated GitHub Pages showcase smoke test
        smoke = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "smoke_test_pages.py")],
            check=True,
            capture_output=True,
            text=True,
        )
        smoke_res = json.loads(smoke.stdout)
        self.assertTrue(smoke_res["ok"])
        self.assertEqual(smoke_res["errors"], [])
        self.assertIn("/demo/data-room/index.html", smoke_res["checkedRoutes"])

    def test_v050_regressions_theme_strip_portal_all_slides_and_stale_snapshot_cleanup(self) -> None:
        import re
        import shutil
        import threading
        import urllib.error
        import urllib.request

        sys.path.insert(0, str(ROOT / "launcher"))
        from studio_server import create_studio_server, render_studio_shell  # noqa: E402
        sys.path.insert(0, str(ROOT / "skills" / "vc-lab-fundraising-os" / "scripts"))
        from build_data_room import build_data_room  # noqa: E402

        with tempfile.TemporaryDirectory() as tmp:
            demo_dir = Path(tmp) / "demo"
            subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "generate_demo_workspace.py"), "--output", str(demo_dir)],
                check=True,
                capture_output=True,
                text=True,
            )

            server = create_studio_server(demo_dir, plugin_root=ROOT, port=0)
            port = server.server_address[1]
            t = threading.Thread(target=server.serve_forever, daemon=True)
            t.start()
            try:
                base = f"http://127.0.0.1:{port}"

                # 1. Real deck has explicit bg/surface/text keys; mutating ONLY theme.preset must still switch palette
                dk = json.loads(urllib.request.urlopen(base + "/api/deck").read().decode("utf-8"))["deck"]
                self.assertIn("bg", dk["theme"])  # confirm demo deck has hardcoded palette keys
                dk["theme"]["preset"] = "ivory"
                req_dk = urllib.request.Request(
                    base + "/api/deck",
                    data=json.dumps({"deck": dk}).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                res_dk = json.loads(urllib.request.urlopen(req_dk).read().decode("utf-8"))
                self.assertTrue(res_dk["ok"])
                compiled = (demo_dir / "pitch-deck" / "index.html").read_text(encoding="utf-8")
                self.assertIn("#FAF8F5", compiled)
                self.assertNotIn("--bg: #090D16", compiled)

                # 2. Snapshot import rejects hidden/empty-stem filenames & cleans up stale .startup/*.json files
                for bad_name in (".json", ".hidden.json"):
                    req_bad = urllib.request.Request(
                        base + "/api/import-snapshot",
                        data=json.dumps({"startup": {bad_name: {"a": 1}}}).encode("utf-8"),
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                    with self.assertRaises(urllib.error.HTTPError) as ctx_bad:
                        urllib.request.urlopen(req_bad)
                    self.assertEqual(ctx_bad.exception.code, 400)

                orig_snap = json.loads(urllib.request.urlopen(base + "/api/export-snapshot").read().decode("utf-8"))
                stale_file = demo_dir / ".startup" / "stale_extra.json"
                stale_file.write_text(json.dumps({"stale": True}), encoding="utf-8")
                self.assertTrue(stale_file.exists())

                req_restore = urllib.request.Request(
                    base + "/api/import-snapshot",
                    data=json.dumps(orig_snap).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                res_restore = json.loads(urllib.request.urlopen(req_restore).read().decode("utf-8"))
                self.assertTrue(res_restore["ok"])
                self.assertFalse(stale_file.exists(), "Stale .startup/*.json file should be removed on restore")
                backup_snap = json.loads(Path(res_restore["backupPath"]).read_text(encoding="utf-8"))
                self.assertIn("stale_extra.json", backup_snap["startup"])
            finally:
                server.shutdown()
                server.server_close()

            # 3. Execute generated JS in Node.js (when available) to verify all 13 Investor Portal slides & Studio helpers
            if shutil.which("node"):
                dr = build_data_room(demo_dir)
                portal_html = Path(dr["portalHtml"]).read_text(encoding="utf-8")
                portal_js = re.findall(r"<script[^>]*>(.*?)</script>", portal_html, re.S)[0]
                studio_html = render_studio_shell(demo_dir, ROOT)
                studio_js = re.findall(r"<script[^>]*>(.*?)</script>", studio_html, re.S)[0]

                harness = Path(tmp) / "verify_js.js"
                harness.write_text(
                    """
const vm = require('vm');
const fs = require('fs');
const assert = require('assert');

function makeDom() {
  const els = {};
  const getEl = (id) => {
    if (!els[id]) {
      els[id] = { id, textContent: '', innerHTML: '', value: '', style: {}, dataset: {}, options: [], classList: { toggle() {}, contains() { return false; } } };
    }
    return els[id];
  };
  return {
    els,
    document: {
      documentElement: { lang: 'en', dir: 'ltr' },
      getElementById: getEl,
      querySelectorAll: () => [],
      addEventListener: () => {},
      createElement: () => ({ click() {}, style: {} }),
    },
    localStorage: { getItem: () => null, setItem: () => {} },
    setInterval: () => 1,
    clearInterval: () => {},
    fetch: async () => ({ json: async () => ({ ok: true }) }),
    URL: { createObjectURL: () => '' },
    Blob: class {},
    alert: () => {},
    window: {},
  };
}

// A. Verify Investor Portal renders ALL 13 slides with non-empty bodies + XSS escaping + $0 burn
const pDom = makeDom();
pDom.document.getElementById('fm-growth').value = '10';
pDom.document.getElementById('fm-burn-adj').value = '0';
const pCtx = vm.createContext(pDom);
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), pCtx);
const slidesCount = vm.runInContext('PORTAL_SLIDES.length', pCtx);
assert.strictEqual(slidesCount, 13);
for (let i = 0; i < slidesCount; i++) {
  vm.runInContext(`portalSlideIdx = ${i}; renderPortalSlide();`, pCtx);
  const bullets = pDom.els['ps-bullets'].innerHTML.trim();
  const body = pDom.els['ps-body'].innerHTML.trim();
  const sub = pDom.els['ps-sub'].textContent.trim();
  assert.ok(bullets.length > 0 || body.length > 0 || sub.length > 0, `Slide ${i + 1} rendered empty body`);
}
// XSS check in renderPortalSlide
vm.runInContext(`PORTAL_SLIDES.push({ kicker: 'XSS', headline: 'Test', bullets: ['<img src=x onerror=alert(1)>'] }); portalSlideIdx = PORTAL_SLIDES.length - 1; renderPortalSlide();`, pCtx);
assert.ok(pDom.els['ps-bullets'].innerHTML.includes('&lt;img'), 'Bullet HTML must be escaped');
assert.ok(!pDom.els['ps-bullets'].innerHTML.includes('<img'), 'Raw <img> must not appear');
// $0 burn check
vm.runInContext('BASE_FIN.burn = 0; renderFinancialModel();', pCtx);
assert.ok(pDom.els['fm-summary'].textContent.includes('Default-Alive ($0 monthly burn)'));

// B. Verify Studio JS theme preset strip + live voice telemetry + escHtml
const sDom = makeDom();
const sCtx = vm.createContext(sDom);
vm.runInContext(fs.readFileSync(process.argv[3], 'utf8'), sCtx);
assert.strictEqual(vm.runInContext(`escHtml('<script>"x"</script>')`, sCtx), '&lt;script&gt;&quot;x&quot;&lt;/script&gt;');
vm.runInContext(`currentDeckObj = { theme: { preset: 'obsidian-gold', bg: '#090D16', text: '#F8FAFC' }, slides: [] }; _applyThemePresetToDeck('ivory');`, sCtx);
assert.strictEqual(vm.runInContext('currentDeckObj.theme.preset', sCtx), 'ivory');
assert.strictEqual(vm.runInContext('currentDeckObj.theme.bg', sCtx), undefined);
sDom.document.getElementById('vc-transcript').value = 'Um we are building a revolutionary platform, uh like you know basically great.';
vm.runInContext('updateLiveVoiceTelemetry();', sCtx);
assert.strictEqual(sDom.els['vc-live-fillers'].textContent, '5');
assert.strictEqual(sDom.els['vc-live-buzz'].textContent, '1');
console.log('NODE_JS_VERIFIED_OK');
""",
                    encoding="utf-8",
                )
                p_js = Path(tmp) / "portal.js"
                s_js = Path(tmp) / "studio.js"
                p_js.write_text(portal_js, encoding="utf-8")
                s_js.write_text(studio_js, encoding="utf-8")
                node_res = subprocess.run(
                    ["node", str(harness), str(p_js), str(s_js)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertIn("NODE_JS_VERIFIED_OK", node_res.stdout)


if __name__ == "__main__":
    unittest.main()
