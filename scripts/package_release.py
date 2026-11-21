#!/usr/bin/env python3
"""Package Startup Antigravity into a clean, ready-to-unzip Antigravity plugin archive."""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDE_DIRS = {".git", "__pycache__", ".pytest_cache", "dist", ".startup", "pitch-deck", "landing", "tmp", ".venv", "venv"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo", ".DS_Store"}


def package_release() -> Path:
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    version = manifest.get("version", "0.0.1-alpha")
    plugin_dir_name = manifest.get("name", "startup-antigravity")

    dist_dir = ROOT / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dist_dir / f"{plugin_dir_name}-v{version}.zip"

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(ROOT.rglob("*")):
            if file_path.is_dir():
                continue
            rel = file_path.relative_to(ROOT)
            if any(part in EXCLUDE_DIRS for part in rel.parts):
                continue
            if file_path.suffix in EXCLUDE_SUFFIXES or file_path.name == ".DS_Store":
                continue
            arcname = Path(plugin_dir_name) / rel
            zf.write(file_path, arcname.as_posix())

    return zip_path


if __name__ == "__main__":
    out = package_release()
    print(json.dumps({"archive": str(out), "sizeBytes": out.stat().st_size}, indent=2))
    sys.exit(0)
