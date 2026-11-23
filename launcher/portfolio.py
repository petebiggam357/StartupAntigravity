#!/usr/bin/env python3
"""Mentor & Accelerator Cohort Portfolio Command Center (`startup-antigravity --portfolio <dir>`).

Scans a parent directory for startup workspaces containing `.startup/state.json`,
runs the 3-lens Board Review on each company, and compiles a single-file interactive
`cohort-portfolio.html` leaderboard for FI Directors, Mentors, Startup Grind chapters,
and Pre-Seed funds.
"""

from __future__ import annotations

import html
import json
import sys
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
BOARD_SCRIPTS = ROOT / "skills" / "weekly-sprint-review" / "scripts"
if str(BOARD_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(BOARD_SCRIPTS))

from board_review import run_board_review  # noqa: E402


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def build_portfolio(parent_dir: Path, out_html: Path | None = None, open_browser: bool = False) -> dict[str, Any]:
    root = parent_dir.resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Portfolio directory not found: {root}")

    candidates: list[Path] = []
    if (root / ".startup" / "state.json").exists():
        candidates.append(root)
    for child in sorted(root.iterdir()):
        if child.is_dir() and (child / ".startup" / "state.json").exists():
            candidates.append(child)

    companies: list[dict[str, Any]] = []
    total_mrr = 0.0
    for ws in candidates:
        state = _load_json(ws / ".startup" / "state.json", {})
        pmf = _load_json(ws / ".startup" / "pmf.json", {})
        exo = _load_json(ws / ".startup" / "exponential.json", {})
        br = run_board_review(ws, write_memo=False)

        metrics = state.get("metrics") or {}
        mrr = float(metrics.get("mrrUsd", state.get("mrrUsd", 0)) or 0)
        gm = float(metrics.get("grossMarginPct", state.get("grossMarginPct", 0)) or 0)
        surveys = pmf.get("surveys") or pmf.get("responses") or []
        very = sum(1 for r in surveys if r.get("disappointment") == "very_disappointed")
        pmf_pct = round((very / len(surveys)) * 100.0, 1) if surveys else None

        total_mrr += mrr
        companies.append(
            {
                "name": state.get("companyName") or ws.name,
                "path": str(ws),
                "stage": state.get("stage", "idea"),
                "mrrUsd": mrr,
                "grossMarginPct": gm,
                "pmfPct": pmf_pct,
                "boardScore": br["overallScore"],
                "verdict": br["verdict"],
                "exoQuotient": exo.get("exoQuotient"),
                "topAction": (br.get("topActions") or ["On track"])[0],
            }
        )

    companies.sort(key=lambda c: (-c["boardScore"], -c["mrrUsd"]))
    avg_board = round(sum(c["boardScore"] for c in companies) / len(companies), 2) if companies else 0.0
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    rows_html = []
    for c in companies:
        pmf_str = f"{c['pmfPct']}%" if c["pmfPct"] is not None else "—"
        exo_str = f"{c['exoQuotient']}/100" if c["exoQuotient"] is not None else "—"
        rows_html.append(
            f"<tr>"
            f"<td><strong>{html.escape(str(c['name']))}</strong></td>"
            f"<td><span class='pill'>{html.escape(str(c['stage']))}</span></td>"
            f"<td>${c['mrrUsd']:,.0f}</td>"
            f"<td>{c['grossMarginPct']:.0f}%</td>"
            f"<td>{pmf_str}</td>"
            f"<td><strong>{c['boardScore']} / 5.0</strong></td>"
            f"<td>{exo_str}</td>"
            f"<td style='color:#94a3b8;font-size:13px;'>{html.escape(str(c['topAction']))}</td>"
            f"</tr>"
        )
    if not rows_html:
        rows_html.append("<tr><td colspan='8' style='text-align:center;color:#94a3b8;padding:24px;'>No startup workspaces (.startup/state.json) found in this folder.</td></tr>")

    page_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Mentor &amp; Accelerator Cohort Command Center</title>
  <style>
    :root {{ --bg:#020617; --card:#0f172a; --border:#1e293b; --text:#f8fafc; --muted:#94a3b8; --accent:#10b981; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--text); padding:28px 20px; }}
    .wrap {{ max-width:1180px; margin:0 auto; }}
    h1 {{ margin:0 0 6px; font-size:28px; }}
    .sub {{ color:var(--muted); margin:0 0 22px; font-size:14px; }}
    .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin-bottom:22px; }}
    .kpi {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px; }}
    .kpi-v {{ font-size:26px; font-weight:800; color:var(--accent); }}
    .kpi-l {{ font-size:12px; color:var(--muted); text-transform:uppercase; }}
    table {{ width:100%; border-collapse:collapse; background:var(--card); border:1px solid var(--border); border-radius:12px; overflow:hidden; }}
    th, td {{ padding:12px 14px; text-align:left; border-bottom:1px solid var(--border); font-size:14px; }}
    th {{ background:#111c33; color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }}
    .pill {{ padding:2px 8px; border-radius:999px; background:#064e3b; color:#6ee7b7; font-size:11px; font-weight:700; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>Mentor &amp; Accelerator Cohort Command Center</h1>
    <p class="sub">Scanned <code>{html.escape(str(root))}</code> • Updated {now_iso} • Startup Antigravity Portfolio Mode</p>
    <div class="kpis">
      <div class="kpi"><div class="kpi-v">{len(companies)}</div><div class="kpi-l">Tracked Startups</div></div>
      <div class="kpi"><div class="kpi-v">${total_mrr:,.0f}</div><div class="kpi-l">Combined Cohort MRR</div></div>
      <div class="kpi"><div class="kpi-v">{avg_board} / 5.0</div><div class="kpi-l">Avg 3-Lens Board Score</div></div>
    </div>
    <table>
      <thead>
        <tr><th>Startup</th><th>FI Stage</th><th>MRR</th><th>Margin</th><th>PMF %</th><th>Board Score</th><th>ExO</th><th>#1 Priority Bottleneck</th></tr>
      </thead>
      <tbody>{"".join(rows_html)}</tbody>
    </table>
  </div>
</body>
</html>
"""
    dest = (out_html or (root / "cohort-portfolio.html")).resolve()
    dest.write_text(page_html, encoding="utf-8")
    if open_browser:
        webbrowser.open(dest.as_uri())

    return {
        "ok": True,
        "portfolioDir": str(root),
        "htmlPath": str(dest),
        "startupCount": len(companies),
        "totalMrrUsd": round(total_mrr, 2),
        "avgBoardScore": avg_board,
        "companies": companies,
    }
