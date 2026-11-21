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


if __name__ == "__main__":
    unittest.main()
