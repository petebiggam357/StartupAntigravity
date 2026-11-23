#!/usr/bin/env python3
"""Automated Weekly Founder Rhythm (Monday Focus & Friday Digest) + 1-Click Static Publish Packager.

Zero external dependencies (Python 3.10+ standard library only).
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def run_weekly_rhythm(workspace: Path, action: str = "monday_focus") -> dict[str, Any]:
    ws = workspace.resolve()
    sdir = ws / ".startup"
    docs = ws / "docs"
    docs.mkdir(parents=True, exist_ok=True)

    state = _load_json(sdir / "state.json", {})
    assumptions = _load_json(sdir / "assumptions.json", [])
    pacts = _load_json(sdir / "pacts.json", [])
    pmf = _load_json(sdir / "pmf.json", {})
    sprints = _load_json(sdir / "sprints.json", [])

    company = state.get("companyName") or ws.name
    stage = state.get("stage", "idea")
    metrics = state.get("metrics") or {}
    mrr = float(metrics.get("mrrUsd", state.get("mrrUsd", 0)) or 0)
    gm = float(metrics.get("grossMarginPct", state.get("grossMarginPct", 0)) or 0)
    ikpi = state.get("ikpi") or {}
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    untested = [a for a in assumptions if a.get("status") in ("untested", "testing")]
    open_pacts = [p for p in pacts if p.get("type", "customer") == "customer" and p.get("status") not in ("paid", "closed")]
    surveys = pmf.get("surveys") or pmf.get("responses") or []
    very = sum(1 for r in surveys if r.get("disappointment") == "very_disappointed")
    pmf_pct = round((very / len(surveys)) * 100.0, 1) if surveys else None

    if action == "monday_focus":
        focus_items: list[str] = []
        if open_pacts:
            top_p = open_pacts[0]
            focus_items.append(
                f"Close Customer Paid-Pilot PACT with **{top_p.get('company', 'Lead Prospect')}** (${float(top_p.get('amountUsd', 0) or 0):,.0f})."
            )
        else:
            focus_items.append("Book 5 Mom Test discovery calls and pitch 2 Paid-Pilot PACTs before writing new features.")

        if untested:
            focus_items.append(f"Resolve Riskiest Assumption `{untested[0].get('id', 'A-01')}`: {untested[0].get('statement', '')}")
        else:
            focus_items.append("Log and test your next highest-uncertainty growth or retention assumption.")

        if pmf_pct is None or pmf_pct < 40.0:
            focus_items.append("Collect 5+ Sean Ellis PMF survey responses in `pmf_engine_manage` to isolate your >=40% HXC niche.")
        else:
            focus_items.append(f"Double down on your {pmf_pct}% PMF HXC segment and cut any roadmap item not requested by HXC buyers.")

        md = (
            f"# {company} — Monday Top-3 Revenue & PMF Focus ({now_str})\n\n"
            f"**Stage:** `{stage}` • **MRR:** `${mrr:,.0f}` • **Gross Margin:** `{gm:.0f}%`\n\n"
            "## This Week's 3 Needle-Movers\n"
            + "\n".join(f"{i}. {item}" for i, item in enumerate(focus_items[:3], 1))
            + "\n\n*Tip: Pair with `/schedule` every Monday at 8:00 AM so you start every week on paying customers.*\n"
        )
        out = docs / "MONDAY_FOCUS.md"
        out.write_text(md, encoding="utf-8")
        return {"ok": True, "action": "monday_focus", "path": str(out), "focusItems": focus_items[:3]}

    if action == "friday_digest":
        active_sprint = sprints[-1] if sprints else {}
        digest = (
            f"# {company} — Founder Friday Update ({now_str})\n\n"
            f"**TL;DR:** Stage `{stage}` | MRR `${mrr:,.0f}` | Gross Margin `{gm:.0f}%` | "
            f"PMF `{f'{pmf_pct}%' if pmf_pct is not None else 'Unmeasured'}`\n\n"
            f"- **Sprint Goal:** {active_sprint.get('goal', 'Advance customer discovery & Paid-Pilot PACTs')}\n"
            f"- **For-Progress iKPI:** {ikpi.get('metric', ikpi.get('name', 'Not set'))} "
            f"({ikpi.get('current', 0)} / {ikpi.get('target', 'TBD')})\n"
            f"- **Open Customer PACTs:** {len(open_pacts)} active\n"
            f"- **1 Ask for Mentors/Advisors:** Warm intros to 2 target ICP buyers matching our core segment.\n"
        )
        out = docs / "FRIDAY_DIGEST.md"
        out.write_text(digest, encoding="utf-8")
        return {"ok": True, "action": "friday_digest", "path": str(out), "wordCount": len(digest.split())}

    raise ValueError("action must be 'monday_focus' or 'friday_digest'.")


def build_publish_bundle(workspace: Path, include_data_room: bool = False) -> dict[str, Any]:
    """Assemble a static, zero-config deployable `publish/` bundle for Cloudflare Pages, Netlify Drop, or GitHub Pages."""
    ws = workspace.resolve()
    pub = ws / "publish"
    if pub.exists():
        shutil.rmtree(pub)
    pub.mkdir(parents=True, exist_ok=True)
    (pub / ".nojekyll").write_text("", encoding="utf-8")

    included: list[str] = []
    landing_html = ws / "landing" / "index.html"
    deck_html = ws / "pitch-deck" / "index.html"
    dr_dir = ws / "data-room"

    if landing_html.exists():
        shutil.copy2(landing_html, pub / "index.html")
        included.append("index.html (from landing/index.html)")
    elif deck_html.exists():
        shutil.copy2(deck_html, pub / "index.html")
        included.append("index.html (from pitch-deck/index.html)")
    else:
        (pub / "index.html").write_text(
            "<!doctype html><html><body style='background:#020617;color:#f8fafc;font-family:sans-serif;padding:40px;'>"
            "<h1>Startup Antigravity Publish Bundle</h1><p>Compile landing/index.html or pitch-deck/index.html first.</p></body></html>",
            encoding="utf-8",
        )

    if deck_html.exists():
        deck_out = pub / "deck"
        deck_out.mkdir(parents=True, exist_ok=True)
        shutil.copy2(deck_html, deck_out / "index.html")
        included.append("deck/index.html")

    if include_data_room and dr_dir.exists():
        shutil.copytree(dr_dir, pub / "data-room", dirs_exist_ok=True)
        included.append("data-room/")

    # Cloudflare Pages security headers + Netlify zero-config
    (pub / "_headers").write_text(
        "/*\n  X-Frame-Options: SAMEORIGIN\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n",
        encoding="utf-8",
    )
    (pub / "netlify.toml").write_text(
        '[build]\n  publish = "."\n',
        encoding="utf-8",
    )
    deploy_md = (
        "# 1-Click Publish Live Guide\n\n"
        "Your static site bundle is ready inside `publish/` with zero build step required:\n\n"
        "- **Netlify Drop (10 seconds, zero CLI):** Drag and drop the `publish/` folder onto https://app.netlify.com/drop\n"
        "- **Cloudflare Pages (CLI):** `npx wrangler pages deploy publish --project-name my-startup`\n"
        "- **GitHub Pages:** Push `publish/` to your `gh-pages` branch or configure Actions Pages.\n"
    )
    (pub / "DEPLOY_NOW.md").write_text(deploy_md, encoding="utf-8")

    return {
        "ok": True,
        "publishDir": str(pub),
        "included": included,
        "deployGuide": str(pub / "DEPLOY_NOW.md"),
    }
