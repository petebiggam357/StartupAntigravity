#!/usr/bin/env python3
"""Startup Antigravity — Cross-Platform Desktop Launcher & Offline Plugin Installer.

Works in three modes:
  1. Native GUI (Tkinter dark-mode desktop app) when double-clicked from an
     AppImage, .deb desktop entry, macOS .app/.dmg, or Windows .exe.
  2. Headless CLI (`--install`, `--uninstall`, `--status`, `--dashboard`, `--deck`, `--version`).
  3. Zero external runtime dependencies (Python 3.10+ standard library only).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
import webbrowser
import zipfile
from pathlib import Path
from typing import Any

APP_NAME = "Startup Antigravity"
PLUGIN_NAME = "startup-antigravity"
APP_VERSION = "0.2.1-beta"
GITHUB_RELEASES_API = "https://api.github.com/repos/petebiggam357/StartupAntigravity/releases"

STARTER_PROMPTS: list[tuple[str, str]] = [
    (
        "Day-0 Startup Kickstart (FI Pitch + Deck)",
        "Kickstart my startup idea with an FI One-Sentence Pitch, 14-day first-dollar validation plan, For-Progress iKPI, and interactive pitch deck.",
    ),
    (
        "AI Margin & x402 Monetization Audit",
        "Audit our AI token gross margins (target >=75%) and model an x402 HTTP 402 USDC pay-per-call endpoint for AI agents.",
    ),
    (
        "PMF Truth Audit (Sean Ellis 40% Rule)",
        "Run a brutally honest PMF reality check on our customer interviews and retention cohorts to find our High-Expectation Customer segment.",
    ),
    (
        "Extract Mom Test Insights from Call Notes",
        "Ingest this raw customer discovery transcript with transcript_ingest, flag any leading questions, and log verified pain & WTP signals.",
    ),
    (
        "Pitch Deck Roast (FI Mentor + VC Lab Partner)",
        "Critique our pitch-deck/deck.json like a Founder Institute Mentor and VC Lab Partner, then rebuild the interactive slides.",
    ),
    (
        "Build Investor Data Room & Diligence Pack",
        "Compile our investor-ready Data Room (data-room/index.html) and run the VC Lab / FI diligence readiness checklist.",
    ),
    (
        "Exponential Thinking & 6Ds ExO Blueprint",
        "Score our Exponential Organization (MTP + SCALE + IDEAS) quotient, map our industry on the 6Ds of Exponentials, and model 36-month Accelerating Returns.",
    ),
]


def default_plugin_dir() -> Path:
    """Return the Antigravity user plugins directory for startup-antigravity."""
    return Path.home() / ".gemini" / "config" / "plugins" / PLUGIN_NAME


def find_bundled_zip() -> Path | None:
    """Locate the bundled startup-antigravity plugin ZIP payload."""
    candidates: list[Path] = []

    # 1. PyInstaller frozen bundle (_MEIPASS)
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(Path(meipass))

    # 2. AppImage $APPDIR
    appdir = os.environ.get("APPDIR")
    if appdir:
        candidates.append(Path(appdir) / "usr" / "share" / PLUGIN_NAME)

    # 3. Directory containing this script / executable
    here = Path(sys.executable if getattr(sys, "frozen", False) else __file__).resolve().parent
    candidates.extend([
        here,
        here.parent / "share" / PLUGIN_NAME,
        here.parent / "dist",
        Path("/usr/share") / PLUGIN_NAME,
    ])

    for base in candidates:
        if not base.exists():
            continue
        zips = sorted(base.glob(f"{PLUGIN_NAME}-v*.zip"), reverse=True)
        if zips:
            return zips[0]
        direct = base / f"{PLUGIN_NAME}.zip"
        if direct.exists():
            return direct
    return None


def detect_bundled_version(zip_path: Path | None) -> str:
    """Read plugin.json version from the bundled ZIP, falling back to APP_VERSION."""
    if not zip_path or not zip_path.exists():
        return APP_VERSION
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            for member in zf.namelist():
                if member.endswith("plugin.json") and member.count("/") <= 1:
                    data = json.loads(zf.read(member).decode("utf-8"))
                    return str(data.get("version", APP_VERSION))
    except Exception:
        pass
    return APP_VERSION


def detect_installed_version(plugin_dir: Path | None = None) -> str | None:
    """Read version from an installed plugin.json if present."""
    target = plugin_dir or default_plugin_dir()
    manifest = target / "plugin.json"
    if not manifest.exists():
        return None
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        return str(data.get("version", "unknown"))
    except Exception:
        return "unknown"


def get_status(plugin_dir: Path | None = None) -> dict[str, Any]:
    """Collect installation, runtime, and payload health status."""
    target = plugin_dir or default_plugin_dir()
    bundled_zip = find_bundled_zip()
    bundled_version = detect_bundled_version(bundled_zip)
    installed_version = detect_installed_version(target)
    is_symlink = target.is_symlink()

    return {
        "app": APP_NAME,
        "launcherVersion": APP_VERSION,
        "bundledVersion": bundled_version,
        "bundledZip": str(bundled_zip) if bundled_zip else None,
        "installed": installed_version is not None,
        "installedVersion": installed_version,
        "pluginDir": str(target),
        "isSymlink": is_symlink,
        "pythonVersion": platform.python_version(),
        "platform": f"{platform.system()} {platform.machine()}",
        "agyCliDetected": shutil.which("agy") is not None,
    }


def _ensure_executable_bits(root: Path) -> None:
    """Ensure shell scripts, hooks, and MCP server scripts are executable on POSIX."""
    if os.name == "nt":
        return
    patterns = [
        "install.sh",
        "hooks/*.py",
        "mcp_server/server.py",
        "scripts/*.py",
        "skills/*/scripts/*.py",
    ]
    for pat in patterns:
        for path in root.glob(pat):
            if path.is_file():
                mode = path.stat().st_mode
                path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _ensure_windows_python3_shim() -> str | None:
    """On Windows, ensure python3.exe exists next to python.exe if missing."""
    if os.name != "nt":
        return None
    py3 = shutil.which("python3")
    if py3 and "WindowsApps" not in py3:
        return None
    py = shutil.which("python")
    if not py or "WindowsApps" in py:
        return None
    py_path = Path(py)
    shim = py_path.parent / "python3.exe"
    if not shim.exists():
        try:
            shutil.copy2(py_path, shim)
            return str(shim)
        except OSError:
            return None
    return None


def install_plugin(
    plugin_dir: Path | None = None,
    zip_path: Path | None = None,
) -> dict[str, Any]:
    """Install or update Startup Antigravity from the bundled offline ZIP."""
    target = plugin_dir or default_plugin_dir()
    payload = zip_path or find_bundled_zip()
    if not payload or not payload.exists():
        raise FileNotFoundError(
            "Bundled plugin archive (startup-antigravity-v*.zip) was not found."
        )

    plugins_root = target.parent
    plugins_root.mkdir(parents=True, exist_ok=True)

    # Clean existing installation (remove symlink or directory)
    if target.is_symlink():
        target.unlink()
    elif target.exists():
        shutil.rmtree(target)

    # Extract safely into plugins_root (ZIP contains top-level startup-antigravity/)
    with zipfile.ZipFile(payload, "r") as zf:
        # Guard against Zip Slip
        root_resolved = plugins_root.resolve()
        for member in zf.infolist():
            dest = (plugins_root / member.filename).resolve()
            if not str(dest).startswith(str(root_resolved)):
                raise ValueError(f"Unsafe archive path detected: {member.filename}")
        zf.extractall(plugins_root)

    # Handle case where custom plugin_dir name differs from PLUGIN_NAME
    extracted_default = plugins_root / PLUGIN_NAME
    if extracted_default != target and extracted_default.exists() and not target.exists():
        extracted_default.rename(target)

    _ensure_executable_bits(target)
    shim_created = _ensure_windows_python3_shim()
    installed_ver = detect_installed_version(target)

    return {
        "ok": True,
        "action": "install",
        "installedVersion": installed_ver,
        "pluginDir": str(target),
        "sourceArchive": str(payload),
        "windowsPython3Shim": shim_created,
    }


def uninstall_plugin(plugin_dir: Path | None = None) -> dict[str, Any]:
    """Remove Startup Antigravity from the user's Antigravity plugins directory."""
    target = plugin_dir or default_plugin_dir()
    if target.is_symlink():
        target.unlink()
        removed = True
    elif target.exists():
        shutil.rmtree(target)
        removed = True
    else:
        removed = False
    return {"ok": True, "action": "uninstall", "removed": removed, "pluginDir": str(target)}


def open_dashboard(workspace: Path, plugin_dir: Path | None = None) -> dict[str, Any]:
    """Build (if possible) and open dashboard/index.html for a startup workspace."""
    ws = workspace.resolve()
    dash_html = ws / "dashboard" / "index.html"
    target = plugin_dir or default_plugin_dir()
    builder = target / "skills" / "unit-economics-and-profit-os" / "scripts" / "build_dashboard.py"

    if builder.exists() and (ws / ".startup").exists():
        subprocess.run(
            [sys.executable, str(builder), "--workspace", str(ws)],
            check=False,
            capture_output=True,
            text=True,
        )

    if not dash_html.exists():
        raise FileNotFoundError(
            f"No dashboard found at {dash_html}. Initialize your startup workspace in Antigravity first."
        )
    webbrowser.open(dash_html.as_uri())
    return {"ok": True, "opened": str(dash_html)}


def open_pitch_deck(workspace: Path) -> dict[str, Any]:
    """Open pitch-deck/index.html for a startup workspace."""
    ws = workspace.resolve()
    deck_html = ws / "pitch-deck" / "index.html"
    if not deck_html.exists():
        raise FileNotFoundError(
            f"No pitch deck found at {deck_html}. Run startup-kickstart or pitch-deck-builder first."
        )
    webbrowser.open(deck_html.as_uri())
    return {"ok": True, "opened": str(deck_html)}


def open_data_room(workspace: Path, plugin_dir: Path | None = None) -> dict[str, Any]:
    """Build (if possible) and open data-room/index.html for a startup workspace."""
    ws = workspace.resolve()
    dr_html = ws / "data-room" / "index.html"
    target = plugin_dir or default_plugin_dir()
    builder = target / "skills" / "vc-lab-fundraising-os" / "scripts" / "build_data_room.py"

    if builder.exists() and (ws / ".startup").exists():
        subprocess.run(
            [sys.executable, str(builder), "--workspace", str(ws)],
            check=False,
            capture_output=True,
            text=True,
        )

    if not dr_html.exists():
        raise FileNotFoundError(
            f"No investor data room found at {dr_html}. Run data_room_build or Preview Sample Startup first."
        )
    webbrowser.open(dr_html.as_uri())
    return {"ok": True, "opened": str(dr_html)}


def preview_demo_workspace(
    output_dir: Path | None = None,
    plugin_dir: Path | None = None,
    zip_path: Path | None = None,
    open_browser: bool = True,
) -> dict[str, Any]:
    """Generate the realistic SolarLedger sample startup workspace and optionally open it."""
    target = plugin_dir or default_plugin_dir()
    # Locate generate_demo_workspace.py in installed plugin or repo checkout
    repo_root = Path(__file__).resolve().parent.parent
    gen_script = target / "scripts" / "generate_demo_workspace.py"
    if not gen_script.exists():
        if (repo_root / "scripts" / "generate_demo_workspace.py").exists():
            gen_script = repo_root / "scripts" / "generate_demo_workspace.py"
        else:
            # Install plugin from bundled zip first so demo generator is available offline
            install_plugin(plugin_dir=target, zip_path=zip_path)
            gen_script = target / "scripts" / "generate_demo_workspace.py"

    demo_dir = (output_dir or (Path.home() / ".cache" / "startup-antigravity-demo")).resolve()
    proc = subprocess.run(
        [sys.executable, str(gen_script), "--output", str(demo_dir)],
        check=True,
        capture_output=True,
        text=True,
    )
    res = json.loads(proc.stdout)
    if open_browser:
        webbrowser.open(Path(res["dashboardHtml"]).as_uri())
    return res


def check_for_updates(plugin_dir: Path | None = None, timeout: float = 5.0) -> dict[str, Any]:
    """Read-only check against public GitHub Releases for a newer Startup Antigravity version."""
    current = detect_installed_version(plugin_dir) or APP_VERSION
    req = urllib.request.Request(
        GITHUB_RELEASES_API,
        headers={"Accept": "application/vnd.github+json", "User-Agent": f"{PLUGIN_NAME}/{APP_VERSION}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            releases = json.loads(resp.read().decode("utf-8"))
        if not releases:
            return {"ok": True, "currentVersion": current, "latestVersion": current, "updateAvailable": False}
        latest_rel = releases[0]
        latest_tag = str(latest_rel.get("tag_name", "")).lstrip("v")
        html_url = str(latest_rel.get("html_url", "https://github.com/petebiggam357/StartupAntigravity/releases"))
        return {
            "ok": True,
            "currentVersion": current,
            "latestVersion": latest_tag,
            "updateAvailable": bool(latest_tag and latest_tag != current),
            "releaseUrl": html_url,
        }
    except Exception as exc:
        return {
            "ok": False,
            "currentVersion": current,
            "updateAvailable": False,
            "error": str(exc),
        }


def verify_sha256_file(file_path: Path, expected_hex: str) -> bool:
    """Verify SHA-256 hex digest of a downloaded release archive."""
    h = hashlib.sha256()
    with file_path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest().lower() == expected_hex.strip().lower()


def self_update_plugin(plugin_dir: Path | None = None, timeout: float = 15.0) -> dict[str, Any]:
    """Download latest public release ZIP, verify SHA-256 against SHA256SUMS.txt, and install."""
    req = urllib.request.Request(
        GITHUB_RELEASES_API,
        headers={"Accept": "application/vnd.github+json", "User-Agent": f"{PLUGIN_NAME}/{APP_VERSION}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        releases = json.loads(resp.read().decode("utf-8"))
    if not releases:
        raise RuntimeError("No GitHub Releases found.")

    latest = releases[0]
    assets = {a["name"]: a["browser_download_url"] for a in (latest.get("assets") or [])}
    zip_name = next((n for n in assets if n.startswith(f"{PLUGIN_NAME}-v") and n.endswith(".zip")), None)
    if not zip_name:
        raise RuntimeError("Latest release does not contain a universal plugin .zip asset.")

    with tempfile.TemporaryDirectory() as td:
        tmp_zip = Path(td) / zip_name
        urllib.request.urlretrieve(assets[zip_name], tmp_zip)

        sha_verified = False
        if "SHA256SUMS.txt" in assets:
            sums_text = urllib.request.urlopen(assets["SHA256SUMS.txt"], timeout=timeout).read().decode("utf-8")
            expected = None
            for line in sums_text.splitlines():
                parts = line.strip().split()
                if len(parts) >= 2 and parts[-1].endswith(zip_name):
                    expected = parts[0]
                    break
            if expected:
                if not verify_sha256_file(tmp_zip, expected):
                    raise RuntimeError(f"SHA-256 verification FAILED for {zip_name}! Aborting update.")
                sha_verified = True

        res = install_plugin(plugin_dir=plugin_dir, zip_path=tmp_zip)
        res["sha256Verified"] = sha_verified
        res["releaseTag"] = latest.get("tag_name")
        return res


def run_doctor(plugin_dir: Path | None = None) -> dict[str, Any]:
    """Run a 3-second preflight check: Python, plugin manifest, live MCP 25-tool handshake & companion CLIs."""
    target = plugin_dir or default_plugin_dir()
    repo_root = Path(__file__).resolve().parent.parent
    probe_root = target if (target / "mcp_server" / "server.py").exists() else repo_root

    py_ok = sys.version_info >= (3, 10)
    manifest_ok = (probe_root / "plugin.json").exists()
    hooks_ok = (probe_root / "hooks.json").exists()
    mcp_server = probe_root / "mcp_server" / "server.py"

    mcp_ok = False
    mcp_tool_count = 0
    mcp_error: str | None = None
    if mcp_server.exists():
        try:
            payload = (
                json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
                + "\n"
                + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
                + "\n"
            )
            env = {**os.environ, "PLUGIN_ROOT": str(probe_root)}
            proc = subprocess.run(
                [sys.executable, str(mcp_server)],
                input=payload,
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
            )
            lines = [json.loads(ln) for ln in proc.stdout.splitlines() if ln.strip()]
            if len(lines) >= 2 and "tools" in (lines[1].get("result") or {}):
                mcp_tool_count = len(lines[1]["result"]["tools"])
                mcp_ok = proc.returncode == 0 and mcp_tool_count >= 25
        except Exception as exc:
            mcp_error = str(exc)

    companions = {
        cli: shutil.which(cli) is not None
        for cli in ("agy", "git", "gh", "node", "ollama", "claude", "codex")
    }

    return {
        "ok": py_ok and manifest_ok and hooks_ok and mcp_ok,
        "pythonVersion": platform.python_version(),
        "pythonSupported": py_ok,
        "probeRoot": str(probe_root),
        "manifestFound": manifest_ok,
        "hooksFound": hooks_ok,
        "mcpHandshakeOk": mcp_ok,
        "mcpToolCount": mcp_tool_count,
        "mcpError": mcp_error,
        "companionClis": companions,
    }


def launch_local_studio(
    workspace: Path,
    plugin_dir: Path | None = None,
    port: int = 4020,
    open_browser: bool = True,
) -> None:
    """Start the zero-dependency unified Startup Antigravity Web Studio."""
    here = Path(__file__).resolve().parent
    if str(here) not in sys.path:
        sys.path.insert(0, str(here))
    from studio_server import serve_studio  # noqa: E402

    p_root = plugin_dir or default_plugin_dir()
    if not (p_root / "mcp_server" / "founder_resources.json").exists():
        p_root = here.parent
    serve_studio(workspace=workspace, plugin_root=p_root, port=port, open_browser=open_browser)


def launch_gui() -> int:
    """Launch the native dark-mode Tkinter desktop launcher."""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except Exception as exc:
        print(
            f"GUI unavailable ({exc}). Use CLI flags instead: --install, --status, --dashboard.",
            file=sys.stderr,
        )
        return 1

    root = tk.Tk()
    root.title(f"{APP_NAME} — Launcher")
    root.geometry("680x520")
    root.minsize(620, 480)
    root.configure(bg="#0F172A")

    # Colors matching Startup Antigravity palette
    BG = "#0F172A"
    CARD = "#1E293B"
    BORDER = "#334155"
    TEXT = "#F8FAFC"
    MUTED = "#94A3B8"
    EMERALD = "#10B981"
    EMERALD_DARK = "#059669"
    AMBER = "#F59E0B"
    SLATE_BTN = "#334155"

    workspace_var = tk.StringVar(value=str(Path.cwd()))
    status_vars = {
        "installed": tk.StringVar(value="Checking..."),
        "bundled": tk.StringVar(value="Checking..."),
        "path": tk.StringVar(value=str(default_plugin_dir())),
        "runtime": tk.StringVar(value="Checking..."),
    }

    # Header
    header = tk.Frame(root, bg=BG, padx=24, pady=18)
    header.pack(fill="x")
    tk.Label(
        header,
        text="STARTUP ANTIGRAVITY",
        font=("Sans", 18, "bold"),
        fg=EMERALD,
        bg=BG,
    ).pack(anchor="w")
    tk.Label(
        header,
        text="Ethical Venture OS — Offline Installer & Founder Command Center Launcher",
        font=("Sans", 10),
        fg=MUTED,
        bg=BG,
    ).pack(anchor="w", pady=(2, 0))

    # Status Card
    card = tk.Frame(root, bg=CARD, padx=18, pady=14, highlightbackground=BORDER, highlightthickness=1)
    card.pack(fill="x", padx=24, pady=(0, 14))

    rows = [
        ("Plugin Status:", status_vars["installed"]),
        ("Bundled Release:", status_vars["bundled"]),
        ("Install Path:", status_vars["path"]),
        ("Runtime:", status_vars["runtime"]),
    ]
    for idx, (label, var) in enumerate(rows):
        tk.Label(card, text=label, font=("Sans", 10, "bold"), fg=MUTED, bg=CARD).grid(
            row=idx, column=0, sticky="w", pady=2, padx=(0, 12)
        )
        tk.Label(card, textvariable=var, font=("Sans", 10), fg=TEXT, bg=CARD).grid(
            row=idx, column=1, sticky="w", pady=2
        )

    # Workspace Selector
    ws_frame = tk.Frame(root, bg=BG, padx=24)
    ws_frame.pack(fill="x", pady=(0, 12))
    tk.Label(
        ws_frame,
        text="Startup Workspace Folder (for Dashboard & Pitch Deck):",
        font=("Sans", 9, "bold"),
        fg=MUTED,
        bg=BG,
    ).pack(anchor="w")
    ws_row = tk.Frame(ws_frame, bg=BG)
    ws_row.pack(fill="x", pady=(4, 0))
    tk.Entry(
        ws_row,
        textvariable=workspace_var,
        bg=CARD,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        font=("Monospace", 9),
    ).pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))

    def browse_workspace() -> None:
        chosen = filedialog.askdirectory(initialdir=workspace_var.get() or str(Path.home()))
        if chosen:
            workspace_var.set(chosen)

    tk.Button(
        ws_row,
        text="Browse...",
        command=browse_workspace,
        bg=SLATE_BTN,
        fg=TEXT,
        activebackground=BORDER,
        activeforeground=TEXT,
        relief="flat",
        padx=12,
        pady=5,
        cursor="hand2",
    ).pack(side="right")

    # Log area
    log_box = tk.Text(
        root,
        height=7,
        bg="#020617",
        fg="#CBD5E1",
        font=("Monospace", 9),
        relief="flat",
        padx=10,
        pady=8,
        state="disabled",
    )

    def log(msg: str) -> None:
        log_box.configure(state="normal")
        log_box.insert("end", msg + "\n")
        log_box.see("end")
        log_box.configure(state="disabled")

    def refresh_status() -> None:
        st = get_status()
        if st["installed"]:
            mode = " (symlink)" if st["isSymlink"] else ""
            status_vars["installed"].set(f"Installed — v{st['installedVersion']}{mode}")
        else:
            status_vars["installed"].set("Not installed yet")
        status_vars["bundled"].set(
            f"v{st['bundledVersion']}" + (" (offline bundle ready)" if st["bundledZip"] else " (no zip found)")
        )
        status_vars["path"].set(st["pluginDir"])
        status_vars["runtime"].set(f"Python {st['pythonVersion']} • {st['platform']}")

    def on_install() -> None:
        try:
            res = install_plugin()
            log(f"[OK] Installed Startup Antigravity v{res['installedVersion']} -> {res['pluginDir']}")
            if res.get("windowsPython3Shim"):
                log(f"[OK] Created Windows python3.exe shim -> {res['windowsPython3Shim']}")
            log("Restart Antigravity or reload plugins to activate all 18 skills & 20 MCP tools.")
            refresh_status()
            messagebox.showinfo(
                APP_NAME,
                f"Startup Antigravity v{res['installedVersion']} installed!\n\n"
                f"Path: {res['pluginDir']}\n\n"
                "Open Antigravity in your startup workspace to start.",
            )
        except Exception as exc:
            log(f"[ERROR] Install failed: {exc}")
            messagebox.showerror(APP_NAME, f"Install failed:\n{exc}")

    def on_dashboard() -> None:
        try:
            res = open_dashboard(Path(workspace_var.get()))
            log(f"[OK] Opened Founder Command Center -> {res['opened']}")
        except Exception as exc:
            log(f"[WARN] {exc}")
            messagebox.showwarning(APP_NAME, str(exc))

    def on_deck() -> None:
        try:
            res = open_pitch_deck(Path(workspace_var.get()))
            log(f"[OK] Opened Interactive Pitch Deck -> {res['opened']}")
        except Exception as exc:
            log(f"[WARN] {exc}")
            messagebox.showwarning(APP_NAME, str(exc))

    def on_data_room() -> None:
        try:
            res = open_data_room(Path(workspace_var.get()))
            log(f"[OK] Opened Investor Data Room -> {res['opened']}")
        except Exception as exc:
            log(f"[WARN] {exc}")
            messagebox.showwarning(APP_NAME, str(exc))

    def on_demo() -> None:
        try:
            res = preview_demo_workspace(open_browser=True)
            workspace_var.set(res["workspace"])
            log(f"[OK] Built SolarLedger Sample Startup -> {res['workspace']}")
            log(f"     Dashboard, Pitch Deck, Landing Page & Data Room ({res['dataRoomReadinessPct']}% ready) compiled!")
            refresh_status()
        except Exception as exc:
            log(f"[ERROR] Demo preview failed: {exc}")
            messagebox.showerror(APP_NAME, f"Demo preview failed:\n{exc}")

    def on_uninstall() -> None:
        if not messagebox.askyesno(
            APP_NAME,
            f"Remove Startup Antigravity plugin from:\n{default_plugin_dir()}?",
        ):
            return
        res = uninstall_plugin()
        log(f"[OK] Uninstalled plugin (removed={res['removed']})")
        refresh_status()

    def on_studio() -> None:
        ws = Path(workspace_var.get())
        threading.Thread(
            target=launch_local_studio,
            kwargs={"workspace": ws, "port": 4020, "open_browser": True},
            daemon=True,
        ).start()
        log(f"[OK] Started Startup Antigravity Web Studio at http://127.0.0.1:4020 for {ws}")

    def on_check_updates() -> None:
        res = check_for_updates()
        if not res.get("ok"):
            log(f"[INFO] Update check skipped (offline): {res.get('error')}")
            return
        if res.get("updateAvailable"):
            log(f"[UPDATE] New release v{res['latestVersion']} available (current: v{res['currentVersion']})")
            if messagebox.askyesno(
                APP_NAME,
                f"Startup Antigravity v{res['latestVersion']} is available!\n"
                f"Current version: v{res['currentVersion']}\n\nDownload, SHA-256 verify, and install now?",
            ):
                try:
                    up = self_update_plugin()
                    log(f"[OK] Self-updated to v{up['installedVersion']} (sha256Verified={up['sha256Verified']})")
                    refresh_status()
                    messagebox.showinfo(APP_NAME, f"Updated to v{up['installedVersion']} cleanly!")
                except Exception as exc:
                    log(f"[ERROR] Self-update failed: {exc}")
                    webbrowser.open(res["releaseUrl"])
        else:
            log(f"[OK] You are up to date (v{res['currentVersion']}).")
            messagebox.showinfo(APP_NAME, f"You are running the latest version (v{res['currentVersion']}).")

    # Action Buttons
    btn_frame = tk.Frame(root, bg=BG, padx=24)
    btn_frame.pack(fill="x", pady=(0, 12))

    row1 = tk.Frame(btn_frame, bg=BG)
    row1.pack(fill="x", pady=(0, 8))
    tk.Button(
        row1,
        text="Install / Update Antigravity Plugin",
        command=on_install,
        bg=EMERALD,
        fg="#022C22",
        activebackground=EMERALD_DARK,
        activeforeground=TEXT,
        font=("Sans", 10, "bold"),
        relief="flat",
        padx=16,
        pady=10,
        cursor="hand2",
    ).pack(side="left", expand=True, fill="x", padx=(0, 6))

    tk.Button(
        row1,
        text="Open Web Studio",
        command=on_studio,
        bg="#0284C7",
        fg=TEXT,
        activebackground="#0369A1",
        activeforeground=TEXT,
        font=("Sans", 10, "bold"),
        relief="flat",
        padx=12,
        pady=10,
        cursor="hand2",
    ).pack(side="left", padx=(0, 6))

    tk.Button(
        row1,
        text="Sample Demo",
        command=on_demo,
        bg=AMBER,
        fg="#1C1917",
        activebackground="#D97706",
        activeforeground=TEXT,
        font=("Sans", 10, "bold"),
        relief="flat",
        padx=12,
        pady=10,
        cursor="hand2",
    ).pack(side="right")

    row2 = tk.Frame(btn_frame, bg=BG)
    row2.pack(fill="x")
    tk.Button(
        row2,
        text="Dashboard",
        command=on_dashboard,
        bg=SLATE_BTN,
        fg=TEXT,
        activebackground=BORDER,
        activeforeground=TEXT,
        relief="flat",
        padx=8,
        pady=8,
        cursor="hand2",
    ).pack(side="left", expand=True, fill="x", padx=(0, 5))

    tk.Button(
        row2,
        text="Pitch Deck",
        command=on_deck,
        bg=SLATE_BTN,
        fg=TEXT,
        activebackground=BORDER,
        activeforeground=TEXT,
        relief="flat",
        padx=8,
        pady=8,
        cursor="hand2",
    ).pack(side="left", expand=True, fill="x", padx=(0, 5))

    tk.Button(
        row2,
        text="Data Room",
        command=on_data_room,
        bg=SLATE_BTN,
        fg=TEXT,
        activebackground=BORDER,
        activeforeground=TEXT,
        relief="flat",
        padx=8,
        pady=8,
        cursor="hand2",
    ).pack(side="left", expand=True, fill="x", padx=(0, 5))

    tk.Button(
        row2,
        text="Check Updates",
        command=on_check_updates,
        bg=SLATE_BTN,
        fg=EMERALD,
        activebackground=BORDER,
        activeforeground=TEXT,
        relief="flat",
        padx=8,
        pady=8,
        cursor="hand2",
    ).pack(side="left", expand=True, fill="x", padx=(0, 5))

    tk.Button(
        row2,
        text="Uninstall",
        command=on_uninstall,
        bg="#7F1D1D",
        fg=TEXT,
        activebackground="#991B1B",
        activeforeground=TEXT,
        relief="flat",
        padx=8,
        pady=8,
        cursor="hand2",
    ).pack(side="right")

    # 1-Click Starter Prompt Palette
    prompt_frame = tk.Frame(root, bg=BG, padx=24)
    prompt_frame.pack(fill="x", pady=(0, 10))
    tk.Label(
        prompt_frame,
        text="Quickstart Antigravity Prompt (pick & copy into Antigravity chat):",
        font=("Sans", 9, "bold"),
        fg=MUTED,
        bg=BG,
    ).pack(anchor="w")
    prompt_row = tk.Frame(prompt_frame, bg=BG)
    prompt_row.pack(fill="x", pady=(4, 0))
    prompt_labels = [p[0] for p in STARTER_PROMPTS]
    prompt_map = dict(STARTER_PROMPTS)
    selected_prompt = tk.StringVar(value=prompt_labels[0])
    menu = tk.OptionMenu(prompt_row, selected_prompt, *prompt_labels)
    menu.configure(bg=CARD, fg=TEXT, activebackground=BORDER, activeforeground=TEXT, highlightthickness=0, relief="flat")
    menu["menu"].configure(bg=CARD, fg=TEXT)
    menu.pack(side="left", expand=True, fill="x", padx=(0, 8))

    def on_copy_prompt() -> None:
        text = prompt_map[selected_prompt.get()]
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        log(f"[COPIED] {selected_prompt.get()} -> paste into Antigravity chat!")

    tk.Button(
        prompt_row,
        text="Copy Prompt",
        command=on_copy_prompt,
        bg=SLATE_BTN,
        fg=EMERALD,
        activebackground=BORDER,
        activeforeground=TEXT,
        font=("Sans", 9, "bold"),
        relief="flat",
        padx=12,
        pady=5,
        cursor="hand2",
    ).pack(side="right")

    log_box.pack(fill="both", expand=True, padx=24, pady=(0, 16))
    refresh_status()
    log(f"Ready — {APP_NAME} Launcher v{APP_VERSION}. Click 'Install / Update' to deploy offline.")
    root.mainloop()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="startup-antigravity",
        description="Startup Antigravity — Offline Plugin Installer & Founder Command Center Launcher",
    )
    parser.add_argument("--install", action="store_true", help="Install or update the plugin offline")
    parser.add_argument("--uninstall", action="store_true", help="Remove the installed plugin")
    parser.add_argument("--status", action="store_true", help="Print installation & runtime status")
    parser.add_argument("--prompts", action="store_true", help="Print quickstart Antigravity prompts as JSON")
    parser.add_argument("--dashboard", metavar="WORKSPACE", help="Open Founder Command Center for WORKSPACE")
    parser.add_argument("--deck", metavar="WORKSPACE", help="Open interactive Pitch Deck for WORKSPACE")
    parser.add_argument("--data-room", metavar="WORKSPACE", help="Build & open Investor Data Room for WORKSPACE")
    parser.add_argument(
        "--serve",
        nargs="?",
        const=".",
        metavar="WORKSPACE",
        help="Start unified local Web Studio HTTP server for WORKSPACE (default: current directory)",
    )
    parser.add_argument("--port", type=int, default=4020, help="Port for --serve Web Studio (default: 4020)")
    parser.add_argument("--check-update", action="store_true", help="Check GitHub Releases for a newer version")
    parser.add_argument("--update", action="store_true", help="Download, SHA-256 verify, and install latest GitHub Release")
    parser.add_argument("--doctor", action="store_true", help="Run preflight diagnostics (Python, manifest, live MCP handshake, CLIs)")
    parser.add_argument(
        "--demo",
        nargs="?",
        const="",
        metavar="DIR",
        help="Generate the SolarLedger sample startup workspace (optionally at DIR)",
    )
    parser.add_argument("--no-browser", action="store_true", help="Do not launch browser during --demo or --serve")
    parser.add_argument("--plugin-dir", metavar="DIR", help="Override target plugin installation directory")
    parser.add_argument("--zip", metavar="ARCHIVE", help="Override bundled plugin ZIP path")
    parser.add_argument("--version", action="store_true", help="Print launcher version and exit")
    parser.add_argument("--json", action="store_true", help="Output JSON for CLI subcommands")

    args = parser.parse_args(argv)
    plugin_dir = Path(args.plugin_dir) if args.plugin_dir else None
    zip_override = Path(args.zip) if args.zip else None

    if args.version:
        print(f"{PLUGIN_NAME} {APP_VERSION}")
        return 0

    if args.prompts:
        print(json.dumps([{"label": k, "prompt": v} for k, v in STARTER_PROMPTS], indent=2))
        return 0

    if args.check_update:
        print(json.dumps(check_for_updates(plugin_dir=plugin_dir), indent=2))
        return 0

    if args.update:
        print(json.dumps(self_update_plugin(plugin_dir=plugin_dir), indent=2))
        return 0

    if args.doctor:
        doc = run_doctor(plugin_dir=plugin_dir)
        print(json.dumps(doc, indent=2))
        return 0 if doc["ok"] else 1

    if args.serve is not None:
        launch_local_studio(
            workspace=Path(args.serve),
            plugin_dir=plugin_dir,
            port=args.port,
            open_browser=not args.no_browser,
        )
        return 0

    if args.status:
        st = get_status(plugin_dir)
        print(json.dumps(st, indent=2))
        return 0

    if args.install:
        res = install_plugin(plugin_dir=plugin_dir, zip_path=zip_override)
        print(json.dumps(res, indent=2))
        return 0

    if args.uninstall:
        res = uninstall_plugin(plugin_dir=plugin_dir)
        print(json.dumps(res, indent=2))
        return 0

    if args.dashboard:
        res = open_dashboard(Path(args.dashboard), plugin_dir=plugin_dir)
        print(json.dumps(res, indent=2))
        return 0

    if args.deck:
        res = open_pitch_deck(Path(args.deck))
        print(json.dumps(res, indent=2))
        return 0

    if args.data_room:
        res = open_data_room(Path(args.data_room), plugin_dir=plugin_dir)
        print(json.dumps(res, indent=2))
        return 0

    if args.demo is not None:
        out_dir = Path(args.demo) if args.demo else None
        res = preview_demo_workspace(
            output_dir=out_dir,
            plugin_dir=plugin_dir,
            zip_path=zip_override,
            open_browser=not args.no_browser,
        )
        print(json.dumps(res, indent=2))
        return 0

    return launch_gui()


if __name__ == "__main__":
    raise SystemExit(main())
