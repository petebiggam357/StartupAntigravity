#!/usr/bin/env python3
"""Automated smoke test & optional Playwright browser check for the GitHub Pages showcase.

Usage:
  python3 scripts/smoke_test_pages.py                  # builds into a temp dir & verifies
  python3 scripts/smoke_test_pages.py --site-dir site_dist
  python3 scripts/smoke_test_pages.py --site-dir site_dist --playwright
"""

from __future__ import annotations

import argparse
import functools
import json
import subprocess
import sys
import tempfile
import threading
import urllib.error
import urllib.request
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent


class _LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for k, v in attrs:
            if k in ("href", "src") and v:
                if v.startswith(("http://", "https://", "#", "mailto:", "javascript:", "data:")):
                    continue
                self.refs.append(v.split("#", 1)[0].split("?", 1)[0])


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return


def run_pages_smoke_test(site_dir: Path, use_playwright: bool = False) -> dict[str, Any]:
    site_root = site_dir.resolve()
    if not site_root.exists() or not (site_root / "index.html").exists():
        raise FileNotFoundError(f"Built site not found at {site_root}")

    errors: list[str] = []
    if not (site_root / ".nojekyll").exists():
        errors.append("Missing .nojekyll file in site root.")

    handler = functools.partial(_QuietHandler, directory=str(site_root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    checked_routes: list[str] = []
    playwright_verified = False

    try:
        base = f"http://127.0.0.1:{port}"
        required_routes: list[tuple[str, list[str]]] = [
            ("/index.html", ["Startup Antigravity", "demo/dashboard/index.html"]),
            ("/logo.svg", ["<svg"]),
            ("/demo/dashboard/index.html", ["Command Center", "what-if-simulator"]),
            ("/demo/pitch-deck/index.html", ["<html"]),
            ("/demo/data-room/index.html", ["DR_I18N", "PORTAL_SLIDES", "renderFinancialModel", "Due-Diligence"]),
            ("/demo/landing/index.html", ["<html"]),
        ]

        index_html = ""
        for route, markers in required_routes:
            url = base + route
            try:
                with urllib.request.urlopen(url, timeout=10) as resp:
                    status = resp.status
                    body = resp.read().decode("utf-8", errors="replace")
            except Exception as exc:
                errors.append(f"Route {route} failed: {exc}")
                continue

            if status != 200:
                errors.append(f"Route {route} returned HTTP {status}")
            if not body.strip():
                errors.append(f"Route {route} returned empty body")
            for marker in markers:
                if marker.lower() not in body.lower():
                    errors.append(f"Route {route} missing expected marker: {marker!r}")
            if route == "/index.html":
                index_html = body
            checked_routes.append(route)

        # Verify all relative local links/assets referenced in index.html resolve to HTTP 200
        collector = _LinkCollector()
        collector.feed(index_html)
        checked_refs: set[str] = set()
        for ref in collector.refs:
            clean = ref.lstrip("/")
            if not clean or clean in checked_refs:
                continue
            checked_refs.add(clean)
            try:
                with urllib.request.urlopen(f"{base}/{clean}", timeout=10) as resp:
                    if resp.status != 200:
                        errors.append(f"Relative asset /{clean} returned HTTP {resp.status}")
            except Exception as exc:
                errors.append(f"Broken relative link /{clean}: {exc}")

        # Optional headless Playwright browser verification
        if use_playwright:
            try:
                from playwright.sync_api import sync_playwright  # type: ignore
            except ImportError as exc:
                errors.append(f"--playwright requested but playwright is not installed: {exc}")
            else:
                page_errors: list[str] = []
                with sync_playwright() as p:
                    browser = p.chromium.launch()
                    page = browser.new_page()
                    page.on("pageerror", lambda err: page_errors.append(str(err)))
                    for route in ("/index.html", "/demo/dashboard/index.html", "/demo/data-room/index.html"):
                        page.goto(base + route, wait_until="networkidle")
                    # Exercise single-file Investor Portal tabs
                    for tab in ("deck", "financials", "pacts", "diligence", "overview"):
                        page.click(f'button[data-sec="{tab}"]')
                    browser.close()
                if page_errors:
                    errors.extend(f"Playwright pageerror: {e}" for e in page_errors)
                else:
                    playwright_verified = True
    finally:
        server.shutdown()
        server.server_close()

    return {
        "ok": len(errors) == 0,
        "siteDir": str(site_root),
        "checkedRoutes": checked_routes,
        "checkedLocalLinks": len(checked_refs),
        "playwrightVerified": playwright_verified,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Smoke-test the Startup Antigravity GitHub Pages showcase.")
    parser.add_argument("--site-dir", default="", help="Existing built site_dist directory (builds temp copy if omitted)")
    parser.add_argument("--playwright", action="store_true", help="Also run headless Chromium checks via Playwright")
    args = parser.parse_args(argv)

    if args.site_dir:
        res = run_pages_smoke_test(Path(args.site_dir), use_playwright=args.playwright)
        print(json.dumps(res, indent=2))
        return 0 if res["ok"] else 1

    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp) / "site_dist"
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_site.py"), "--out-dir", str(out_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        res = run_pages_smoke_test(out_dir, use_playwright=args.playwright)
        print(json.dumps(res, indent=2))
        return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
