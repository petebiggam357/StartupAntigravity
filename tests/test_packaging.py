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


if __name__ == "__main__":
    unittest.main()
