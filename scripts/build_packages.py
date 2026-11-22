#!/usr/bin/env python3
"""Build native app packages for Startup Antigravity (ZIP, .deb, AppDir, .AppImage, SHA256SUMS).

Usage examples:
  python3 scripts/build_packages.py --target zip
  python3 scripts/build_packages.py --target deb
  python3 scripts/build_packages.py --target appdir
  python3 scripts/build_packages.py --target appimage --binary dist/startup-antigravity-bin
  python3 scripts/build_packages.py --target all
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from package_release import package_release  # noqa: E402

DIST_DIR = ROOT / "dist"
LAUNCHER_SRC = ROOT / "launcher" / "app.py"
STUDIO_SERVER_SRC = ROOT / "launcher" / "studio_server.py"
X402_STOREFRONT_SRC = ROOT / "launcher" / "x402_storefront.py"
ICON_SRC = ROOT / "assets" / "logo.svg"


def load_manifest() -> dict[str, Any]:
    return json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))


def _chmod_exec(path: Path) -> None:
    if os.name == "nt":
        return
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def desktop_entry_text(exec_cmd: str = "startup-antigravity") -> str:
    return (
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Startup Antigravity\n"
        "GenericName=Ethical Venture OS Launcher\n"
        "Comment=Install Startup Antigravity for Antigravity IDE and launch your Founder Command Center\n"
        f"Exec={exec_cmd}\n"
        "Icon=startup-antigravity\n"
        "Terminal=false\n"
        "Categories=Development;Office;Utility;\n"
        "StartupNotify=true\n"
    )


def build_deb(zip_path: Path, manifest: dict[str, Any]) -> Path:
    """Build a native Debian / Ubuntu / Pop!_OS .deb package using dpkg-deb."""
    if not shutil.which("dpkg-deb"):
        raise RuntimeError("dpkg-deb is not installed on this host.")

    version = str(manifest["version"])
    # Debian versions allow digits, letters, '.', '+', '-', '~'
    deb_version = version.replace("-", "~")
    pkg_name = str(manifest["name"])
    stage = DIST_DIR / f"_deb_stage_{pkg_name}"
    if stage.exists():
        shutil.rmtree(stage)

    debian_dir = stage / "DEBIAN"
    bin_dir = stage / "usr" / "bin"
    share_dir = stage / "usr" / "share" / pkg_name
    apps_dir = stage / "usr" / "share" / "applications"
    icons_dir = stage / "usr" / "share" / "icons" / "hicolor" / "scalable" / "apps"

    for d in (debian_dir, bin_dir, share_dir, apps_dir, icons_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Payload: offline plugin ZIP + launcher script + local Studio server
    shutil.copy2(zip_path, share_dir / zip_path.name)
    launcher_dest = share_dir / "launcher.py"
    shutil.copy2(LAUNCHER_SRC, launcher_dest)
    shutil.copy2(STUDIO_SERVER_SRC, share_dir / "studio_server.py")
    shutil.copy2(X402_STOREFRONT_SRC, share_dir / "x402_storefront.py")
    _chmod_exec(launcher_dest)

    # CLI & desktop wrapper in /usr/bin
    wrapper = bin_dir / pkg_name
    wrapper.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        f'exec python3 "/usr/share/{pkg_name}/launcher.py" "$@"\n',
        encoding="utf-8",
    )
    _chmod_exec(wrapper)

    # Desktop entry & SVG icon
    (apps_dir / f"{pkg_name}.desktop").write_text(desktop_entry_text(pkg_name), encoding="utf-8")
    shutil.copy2(ICON_SRC, icons_dir / f"{pkg_name}.svg")

    # Installed-Size in KiB
    total_bytes = sum(p.stat().st_size for p in stage.rglob("*") if p.is_file())
    installed_kb = max(1, (total_bytes + 1023) // 1024)

    control_text = (
        f"Package: {pkg_name}\n"
        f"Version: {deb_version}\n"
        "Section: devel\n"
        "Priority: optional\n"
        "Architecture: all\n"
        f"Installed-Size: {installed_kb}\n"
        "Depends: python3 (>= 3.10)\n"
        "Recommends: python3-tk\n"
        "Maintainer: petebiggam357 <359430747+petebiggam357@users.noreply.github.com>\n"
        f"Homepage: {manifest.get('homepage', 'https://github.com/petebiggam357/StartupAntigravity')}\n"
        "Description: Startup Antigravity — Ethical Venture OS Launcher & Plugin Bundle\n"
        " Offline desktop launcher and installer for the Startup Antigravity\n"
        " Antigravity plugin (18 skills, 7 subagents, 20 MCP tools, 4 hooks,\n"
        " visual pitch deck engine, and live Founder Command Center dashboard).\n"
    )
    control_path = debian_dir / "control"
    control_path.write_text(control_text, encoding="utf-8")

    # Normalize permissions required by dpkg-deb (DEBIAN dir must be 0755..0775)
    for d in [stage, *[p for p in stage.rglob("*") if p.is_dir()]]:
        d.chmod(0o755)
    control_path.chmod(0o644)

    deb_out = DIST_DIR / f"{pkg_name}_{version}_all.deb"
    if deb_out.exists():
        deb_out.unlink()

    subprocess.run(
        ["dpkg-deb", "--root-owner-group", "--build", str(stage), str(deb_out)],
        check=True,
        capture_output=True,
        text=True,
    )
    shutil.rmtree(stage)
    return deb_out


def build_appdir(
    zip_path: Path,
    manifest: dict[str, Any],
    compiled_binary: Path | None = None,
) -> Path:
    """Build a Freedesktop-compliant StartupAntigravity.AppDir."""
    pkg_name = str(manifest["name"])
    appdir = DIST_DIR / "StartupAntigravity.AppDir"
    if appdir.exists():
        shutil.rmtree(appdir)

    usr_bin = appdir / "usr" / "bin"
    usr_share = appdir / "usr" / "share" / pkg_name
    apps_dir = appdir / "usr" / "share" / "applications"
    icons_dir = appdir / "usr" / "share" / "icons" / "hicolor" / "scalable" / "apps"

    for d in (usr_bin, usr_share, apps_dir, icons_dir):
        d.mkdir(parents=True, exist_ok=True)

    # Copy offline plugin ZIP payload
    shutil.copy2(zip_path, usr_share / zip_path.name)

    # Copy compiled binary (PyInstaller ELF) OR pure-Python launcher
    if compiled_binary and compiled_binary.exists():
        target_bin = usr_bin / pkg_name
        shutil.copy2(compiled_binary, target_bin)
        _chmod_exec(target_bin)
        apprun_exec = f'exec "$HERE/usr/bin/{pkg_name}" "$@"'
    else:
        launcher_dest = usr_share / "launcher.py"
        shutil.copy2(LAUNCHER_SRC, launcher_dest)
        shutil.copy2(STUDIO_SERVER_SRC, usr_share / "studio_server.py")
        shutil.copy2(X402_STOREFRONT_SRC, usr_share / "x402_storefront.py")
        _chmod_exec(launcher_dest)
        apprun_exec = f'exec python3 "$HERE/usr/share/{pkg_name}/launcher.py" "$@"'

    # Top-level AppRun
    apprun = appdir / "AppRun"
    apprun.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        'HERE="$(dirname "$(readlink -f "${0}")")"\n'
        'export APPDIR="$HERE"\n'
        f"{apprun_exec}\n",
        encoding="utf-8",
    )
    _chmod_exec(apprun)

    # Top-level + standard .desktop & SVG icons
    desktop_content = desktop_entry_text(pkg_name)
    (appdir / f"{pkg_name}.desktop").write_text(desktop_content, encoding="utf-8")
    (apps_dir / f"{pkg_name}.desktop").write_text(desktop_content, encoding="utf-8")

    shutil.copy2(ICON_SRC, appdir / f"{pkg_name}.svg")
    shutil.copy2(ICON_SRC, appdir / ".DirIcon")
    shutil.copy2(ICON_SRC, icons_dir / f"{pkg_name}.svg")

    return appdir


def build_appimage(
    zip_path: Path,
    manifest: dict[str, Any],
    compiled_binary: Path | None = None,
    appimagetool: str | None = None,
) -> Path:
    """Build a Linux x86_64 AppImage using appimagetool."""
    tool = appimagetool or shutil.which("appimagetool")
    if not tool:
        raise RuntimeError(
            "appimagetool not found on PATH. Install appimagetool or run the GitHub Actions Release workflow."
        )
    appdir = build_appdir(zip_path, manifest, compiled_binary=compiled_binary)
    version = str(manifest["version"])
    out_path = DIST_DIR / f"StartupAntigravity-v{version}-x86_64.AppImage"
    if out_path.exists():
        out_path.unlink()

    env = os.environ.copy()
    env.setdefault("ARCH", "x86_64")
    subprocess.run([tool, str(appdir), str(out_path)], check=True, env=env)
    _chmod_exec(out_path)
    return out_path


def write_checksums(dist_dir: Path = DIST_DIR) -> Path:
    """Generate SHA256SUMS.txt for all release package files in dist/."""
    exts = {".zip", ".deb", ".AppImage", ".dmg", ".exe"}
    files = sorted(
        p for p in dist_dir.iterdir()
        if p.is_file() and (p.suffix in exts or p.name.endswith(".AppImage"))
    )
    lines: list[str] = []
    for path in files:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        lines.append(f"{h.hexdigest()}  {path.name}")
    out = dist_dir / "SHA256SUMS.txt"
    out.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build Startup Antigravity native app packages.")
    parser.add_argument(
        "--target",
        choices=["zip", "deb", "appdir", "appimage", "checksums", "all"],
        default="all",
        help="Package target to build (default: all supported on current host)",
    )
    parser.add_argument("--binary", help="Optional PyInstaller-compiled binary to embed in AppDir/AppImage")
    parser.add_argument("--appimagetool", help="Optional explicit path to appimagetool executable")
    args = parser.parse_args(argv)

    manifest = load_manifest()
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, Any] = {"version": manifest["version"], "artifacts": []}

    zip_path = package_release()
    results["artifacts"].append({"type": "zip", "path": str(zip_path), "sizeBytes": zip_path.stat().st_size})

    binary_path = Path(args.binary) if args.binary else None

    if args.target in ("deb", "all"):
        if shutil.which("dpkg-deb"):
            deb_path = build_deb(zip_path, manifest)
            results["artifacts"].append({"type": "deb", "path": str(deb_path), "sizeBytes": deb_path.stat().st_size})
        elif args.target == "deb":
            raise RuntimeError("dpkg-deb not found on this host.")

    if args.target in ("appdir", "all"):
        appdir = build_appdir(zip_path, manifest, compiled_binary=binary_path)
        results["artifacts"].append({"type": "appdir", "path": str(appdir)})

    if args.target == "appimage" or (args.target == "all" and (args.appimagetool or shutil.which("appimagetool"))):
        appimg = build_appimage(
            zip_path,
            manifest,
            compiled_binary=binary_path,
            appimagetool=args.appimagetool,
        )
        results["artifacts"].append({"type": "appimage", "path": str(appimg), "sizeBytes": appimg.stat().st_size})

    if args.target in ("checksums", "all", "zip", "deb", "appimage"):
        sums = write_checksums(DIST_DIR)
        results["checksums"] = str(sums)

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
