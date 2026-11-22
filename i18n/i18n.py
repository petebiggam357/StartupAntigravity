#!/usr/bin/env python3
"""Multilingual (Top 10 Global Founder Languages) loader & locale manager."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LOCALES_PATH = Path(__file__).resolve().parent / "locales.json"


def load_all_locales() -> dict[str, dict[str, Any]]:
    return json.loads(LOCALES_PATH.read_text(encoding="utf-8"))


def get_locale(code: str = "en") -> dict[str, Any]:
    locales = load_all_locales()
    norm = (code or "en").strip().lower().split("-")[0]
    return locales.get(norm, locales["en"])


def list_supported_languages() -> list[dict[str, Any]]:
    locales = load_all_locales()
    return [
        {
            "code": code,
            "name": data["name"],
            "nativeName": data["nativeName"],
            "rtl": bool(data.get("rtl", False)),
        }
        for code, data in locales.items()
    ]


def set_workspace_locale(workspace: Path, locale_code: str) -> dict[str, Any]:
    locales = load_all_locales()
    norm = (locale_code or "en").strip().lower().split("-")[0]
    if norm not in locales:
        raise ValueError(f"Unsupported locale '{locale_code}'. Supported: {', '.join(locales.keys())}")
    sdir = workspace.resolve() / ".startup"
    sdir.mkdir(parents=True, exist_ok=True)
    state_file = sdir / "state.json"
    state: dict[str, Any] = {}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except Exception:
            state = {}
    state["locale"] = norm
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return {
        "ok": True,
        "locale": norm,
        "name": locales[norm]["name"],
        "nativeName": locales[norm]["nativeName"],
        "rtl": bool(locales[norm].get("rtl", False)),
        "statePath": str(state_file),
    }
