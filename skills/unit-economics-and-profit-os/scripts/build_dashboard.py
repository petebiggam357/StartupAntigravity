#!/usr/bin/env python3
"""
Startup Antigravity — Live Local Founder Command Center (`dashboard/index.html`).

Zero-dependency Python 3 generator that reads all `.startup/*.json` telemetry
(state, assumptions, experiments, interviews, pacts, sprints, pmf) and compiles
a clean, single-file executive browser dashboard at `<workspace>/dashboard/index.html`.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STAGES = [
    ("idea", "1. Idea"),
    ("validation", "2. Validation"),
    ("mvp", "3. MVP ($1K–$10K)"),
    ("pre_seed_traction", "4. Pre-Seed ($10K–$25K)"),
    ("seed_scale", "5. Seed ($25K+)"),
]


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def render_dashboard_html(workspace: Path) -> str:
    sdir = workspace / ".startup"
    state = _read_json(sdir / "state.json", {})
    assumptions = _read_json(sdir / "assumptions.json", [])
    experiments = _read_json(sdir / "experiments.json", [])
    interviews = _read_json(sdir / "interviews.json", [])
    pacts = _read_json(sdir / "pacts.json", [])
    sprints = _read_json(sdir / "sprints.json", [])
    pmf = _read_json(sdir / "pmf.json", {"surveys": [], "cohorts": []})
    exo = _read_json(sdir / "exponential.json", {})
    x402_ledger = _read_json(sdir / "x402_ledger.json", {"totalCalls": 0, "totalRevenueUsdc": 0.0, "network": "base-sepolia"})
    locales_file = Path(__file__).resolve().parent.parent.parent.parent / "i18n" / "locales.json"
    all_locales = _read_json(locales_file, {})
    default_locale = str(state.get("locale") or "en")
    if default_locale not in all_locales:
        default_locale = "en"
    locales_json_str = json.dumps(all_locales, ensure_ascii=False)
    locale_options_html = "".join(
        f'<option value="{code}"{" selected" if code == default_locale else ""}>{html.escape(data.get("nativeName", code))}</option>'
        for code, data in all_locales.items()
    )
    x402_calls = int(x402_ledger.get("totalCalls", 0) or 0)
    x402_rev = float(x402_ledger.get("totalRevenueUsdc", 0.0) or 0.0)

    company = html.escape(str(state.get("companyName") or "Your Startup"))
    pitch = html.escape(
        str(
            state.get("fiOneSentencePitch")
            or state.get("oneSentencePitch")
            or "Run startup-kickstart to define your FI One-Sentence Pitch."
        )
    )
    stage = str(state.get("stage") or "idea")
    metrics_obj = state.get("metrics") or {}
    mrr = float(metrics_obj.get("mrrUsd", state.get("mrrUsd", 0)) or 0)
    burn = float(metrics_obj.get("monthlyBurnUsd", state.get("monthlyBurnUsd", 0)) or 0)
    cash = float(metrics_obj.get("cashOnHandUsd", state.get("cashOnHandUsd", 0)) or 0)
    gm = float(metrics_obj.get("grossMarginPct", state.get("grossMarginPct", 80)) or 80)
    net_burn = max(0.0, burn - mrr * (gm / 100.0))
    default_alive = net_burn == 0
    runway_str = "Default-Alive" if default_alive else f"{round(cash / net_burn, 1)} mo"

    # Stage progress pills
    stage_idx = next((i for i, (k, _) in enumerate(STAGES) if k == stage), 0)
    stage_pills = []
    for i, (k, lbl) in enumerate(STAGES):
        cls = "st-done" if i < stage_idx else ("st-now" if i == stage_idx else "st-todo")
        stage_pills.append(f'<div class="stage-pill {cls}">{html.escape(lbl)}</div>')

    # PMF Gauge (supports both 'surveys' and 'responses')
    surveys = pmf.get("surveys") or pmf.get("responses") or []
    cohorts = pmf.get("cohorts") or []
    very_cnt = sum(1 for s in surveys if s.get("disappointment") == "very_disappointed")
    pmf_pct = round((very_cnt / len(surveys)) * 100.0, 1) if surveys else 0.0
    pmf_color = "#10B981" if pmf_pct >= 40 else ("#F59E0B" if pmf_pct >= 25 else "#EF4444")
    pmf_status = (
        "PMF PROVEN (>=40%)" if pmf_pct >= 40 else ("APPROACHING PMF — NARROW ICP" if pmf_pct >= 25 else "PRE-PMF — VALIDATE BEFORE SCALING")
    )
    if not surveys:
        pmf_status = "UNMEASURED — RUN SEAN ELLIS SURVEY"
        pmf_color = "#64748B"

    # Strongest segment
    seg_map: dict[str, list[dict[str, Any]]] = {}
    for s in surveys:
        seg_map.setdefault(str(s.get("userSegment") or "Core ICP"), []).append(s)
    seg_rows_html = []
    for seg, rows in sorted(
        seg_map.items(),
        key=lambda kv: (-(sum(1 for r in kv[1] if r.get("disappointment") == "very_disappointed") / len(kv[1])), -len(kv[1])),
    ):
        vc = sum(1 for r in rows if r.get("disappointment") == "very_disappointed")
        sp = round((vc / len(rows)) * 100.0, 1)
        badge = '<span class="pill-ok">>=40%</span>' if sp >= 40 else '<span class="pill-warn">&lt;40%</span>'
        seg_rows_html.append(
            f"<tr><td>{html.escape(seg)}</td><td>{len(rows)}</td><td><strong>{sp}%</strong></td><td>{badge}</td></tr>"
        )
    if not seg_rows_html:
        seg_rows_html.append('<tr><td colspan="4" class="muted">No PMF survey responses logged yet.</td></tr>')

    # PACT Pipeline
    cust_closed = sum(float(p.get("amountUsd", 0)) for p in pacts if p.get("kind") == "customer" and p.get("status") == "closed_cash")
    cust_signed = sum(float(p.get("amountUsd", 0)) for p in pacts if p.get("kind") == "customer" and p.get("status") == "pact_signed")
    inv_closed = sum(float(p.get("amountUsd", 0)) for p in pacts if p.get("kind") == "investor" and p.get("status") == "closed_cash")
    inv_signed = sum(float(p.get("amountUsd", 0)) for p in pacts if p.get("kind") == "investor" and p.get("status") == "pact_signed")

    # Assumptions ranked
    ranked_assump = sorted(
        assumptions,
        key=lambda x: (0 if x.get("status") not in ("validated", "invalidated") else 1, -int(x.get("riskScore", 0))),
    )
    assump_rows = []
    for a in ranked_assump[:8]:
        rs = int(a.get("riskScore", 0))
        rcls = "risk-hi" if rs >= 16 else ("risk-med" if rs >= 9 else "risk-lo")
        st = html.escape(str(a.get("status", "untested")))
        assump_rows.append(
            f"<tr><td><code>{html.escape(str(a.get('id', '')))}</code></td>"
            f"<td>{html.escape(str(a.get('statement', '')))}</td>"
            f'<td><span class="risk-badge {rcls}">{rs}/25</span></td>'
            f"<td><code>{st}</code></td></tr>"
        )
    if not assump_rows:
        assump_rows.append('<tr><td colspan="4" class="muted">No assumptions logged yet.</td></tr>')

    # Sprints & iKPI
    active_sprint = next((s for s in reversed(sprints) if s.get("status") == "active"), None)
    sprint_goal = html.escape(
        str(active_sprint.get("primaryGoal") if active_sprint else (state.get("activeSprintGoal") or "Start Sprint 1 via sprint_manage"))
    )
    closed_sprints = [s for s in sprints if s.get("status") == "closed"]
    avg_vel = (
        f"{round(sum(float(s.get('actuals', {}).get('fiVelocityScore', 0)) for s in closed_sprints) / len(closed_sprints), 2)} / 5.0"
        if closed_sprints
        else "No closed sprints yet"
    )

    ikpi = state.get("ikpi") or {}
    ikpi_name = html.escape(str(ikpi.get("name") or "Define your For-Progress iKPI via ikpi_catalog_search"))
    ikpi_cur = float(ikpi.get("current", 0))
    ikpi_tgt = max(1.0, float(ikpi.get("target", 100)))
    ikpi_pct = min(100.0, round((ikpi_cur / ikpi_tgt) * 100.0, 1))

    # Links to sibling local assets if present
    deck_link = '<a class="btn" href="../pitch-deck/index.html" target="_blank">Open Pitch Deck →</a>' if (workspace / "pitch-deck" / "index.html").exists() else ""
    land_link = '<a class="btn" href="../landing/index.html" target="_blank">Open Landing Page →</a>' if (workspace / "landing" / "index.html").exists() else ""

    # SVG semicircular PMF gauge math (r=70, circumference half = pi*70 = 219.9)
    dash_total = 219.9
    dash_fill = round(dash_total * (min(100.0, max(0.0, pmf_pct)) / 100.0), 1)
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    exo_mtp = html.escape(str(exo.get("mtp") or "Run exponential_audit(action='exo_scorecard') to define your 10x Massive Transformative Purpose."))
    exo_q = exo.get("exoQuotient")
    exo_tier = html.escape(str(exo.get("tier") or "UNSCORED"))
    exo_6d = html.escape(str(exo.get("currentD") or "disruptive").title())
    exo_badge = f"{exo_q}/100 • {exo_tier}" if exo_q is not None else "Not Scored Yet"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Startup Command Center — {company}</title>
  <style>
    :root {{
      --bg: #070B14;
      --surface: #111827;
      --surface2: #182235;
      --text: #F8FAFC;
      --muted: #94A3B8;
      --accent: #10B981;
      --accent2: #F59E0B;
      --border: #1F2937;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      padding: 28px;
      line-height: 1.5;
    }}
    .wrap {{ max-width: 1240px; margin: 0 auto; display: flex; flex-direction: column; gap: 22px; }}
    .top {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px 28px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 20px;
      flex-wrap: wrap;
    }}
    .top h1 {{ font-size: 28px; font-weight: 900; letter-spacing: -0.02em; }}
    .top h1 span {{ color: var(--accent); }}
    .pitch {{ color: var(--muted); margin-top: 6px; max-width: 780px; font-size: 15px; }}
    .top-actions {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    .btn {{
      background: var(--surface2);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 9px 14px;
      border-radius: 8px;
      text-decoration: none;
      font-size: 13px;
      font-weight: 700;
    }}
    .btn:hover {{ border-color: var(--accent); color: var(--accent); }}

    .stage-bar {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 10px;
    }}
    .stage-pill {{
      text-align: center;
      padding: 10px 8px;
      border-radius: 10px;
      font-size: 12px;
      font-weight: 700;
      border: 1px solid var(--border);
    }}
    .st-done {{ background: rgba(16, 185, 129, 0.14); color: #34D399; border-color: rgba(16, 185, 129, 0.4); }}
    .st-now {{ background: var(--accent); color: #052E16; border-color: var(--accent); }}
    .st-todo {{ background: var(--surface); color: var(--muted); }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 14px;
    }}
    .kpi {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
    }}
    .kpi-val {{ font-size: 24px; font-weight: 900; color: var(--accent); }}
    .kpi-lbl {{ font-size: 12px; color: var(--muted); margin-top: 4px; }}

    .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
    .card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .card h2 {{ font-size: 16px; font-weight: 800; letter-spacing: 0.02em; color: var(--text); }}
    .muted {{ color: var(--muted); font-size: 13px; }}

    .gauge-wrap {{ display: flex; flex-direction: column; align-items: center; gap: 6px; }}
    .pmf-badge {{
      font-size: 12px;
      font-weight: 800;
      padding: 4px 12px;
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.06);
      color: {pmf_color};
      border: 1px solid {pmf_color};
    }}

    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid var(--border); text-align: left; }}
    th {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; }}
    .pill-ok {{ background: rgba(16,185,129,0.18); color: #34D399; padding: 2px 8px; border-radius: 999px; font-weight: 700; font-size: 11px; }}
    .pill-warn {{ background: rgba(245,158,11,0.18); color: #FBBF24; padding: 2px 8px; border-radius: 999px; font-weight: 700; font-size: 11px; }}
    .risk-badge {{ padding: 2px 8px; border-radius: 6px; font-weight: 800; font-size: 11px; }}
    .risk-hi {{ background: rgba(239,68,68,0.2); color: #F87171; }}
    .risk-med {{ background: rgba(245,158,11,0.2); color: #FBBF24; }}
    .risk-lo {{ background: rgba(16,185,129,0.2); color: #34D399; }}

    .bar-track {{ width: 100%; height: 12px; background: var(--surface2); border-radius: 999px; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent2)); width: {ikpi_pct}%; }}
    .foot {{ text-align: center; font-size: 12px; color: var(--muted); padding-top: 8px; }}
    @media (max-width: 980px) {{
      .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .grid-2, .stage-bar {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="top">
      <div>
        <h1 id="i18n-title">Startup <span>Command Center</span></h1>
        <p class="pitch"><strong>{company}</strong> — {pitch}</p>
      </div>
      <div class="top-actions">
        <select id="lang-select" aria-label="Language" onchange="applyLang(this.value)" style="background:#0F172A;color:#F8FAFC;border:1px solid #334155;border-radius:8px;padding:7px 10px;font-weight:700;font-size:13px;">
          {locale_options_html}
        </select>
        {deck_link}
        {land_link}
      </div>
    </header>

    <section class="stage-bar">{"".join(stage_pills)}</section>

    <section class="kpi-grid">
      <div class="kpi"><div class="kpi-val">${mrr:,.0f}</div><div class="kpi-lbl" data-i18n="kpi.mrr">Monthly Recurring Revenue</div></div>
      <div class="kpi"><div class="kpi-val">{gm:.0f}%</div><div class="kpi-lbl" data-i18n="kpi.grossMargin">Gross Margin (Target >=75%)</div></div>
      <div class="kpi"><div class="kpi-val">{runway_str}</div><div class="kpi-lbl" data-i18n="kpi.runway">Runway (Cash ${cash:,.0f})</div></div>
      <div class="kpi"><div class="kpi-val">{len(interviews)} / 15</div><div class="kpi-lbl" data-i18n="kpi.interviews">Discovery Interviews</div></div>
      <div class="kpi"><div class="kpi-val">${cust_closed + cust_signed:,.0f}</div><div class="kpi-lbl">Customer PACTs Committed</div></div>
      <div class="kpi"><div class="kpi-val">${x402_rev:,.2f}</div><div class="kpi-lbl" data-i18n="kpi.x402Rev">x402 Agent Revenue ({x402_calls} calls)</div></div>
    </section>

    <section class="grid-2">
      <div class="card">
        <h2 data-i18n="sections.pmf">Product-Market Fit (Sean Ellis 40% Rule)</h2>
        <div class="gauge-wrap">
          <svg width="200" height="115" viewBox="0 0 200 115" role="img" aria-label="PMF Gauge">
            <path d="M 30 100 A 70 70 0 0 1 170 100" fill="none" stroke="#1F2937" stroke-width="16" stroke-linecap="round"/>
            <path d="M 30 100 A 70 70 0 0 1 170 100" fill="none" stroke="{pmf_color}" stroke-width="16" stroke-linecap="round" stroke-dasharray="{dash_fill} {dash_total}"/>
            <text x="100" y="92" text-anchor="middle" fill="#F8FAFC" font-size="28" font-weight="900">{pmf_pct}%</text>
            <text x="100" y="110" text-anchor="middle" fill="#94A3B8" font-size="11">Very Disappointed (n={len(surveys)})</text>
          </svg>
          <span class="pmf-badge">{pmf_status}</span>
        </div>
        <table>
          <thead><tr><th>Segment (HXC)</th><th>n</th><th>PMF %</th><th>40% Bar</th></tr></thead>
          <tbody>{"".join(seg_rows_html)}</tbody>
        </table>
      </div>

      <div class="card">
        <h2>Weekly Sprint, Experiments & For-Progress iKPI</h2>
        <div>
          <div class="muted">ACTIVE WEEKLY SPRINT GOAL</div>
          <div style="font-size:15px;font-weight:700;margin-top:4px;">{sprint_goal}</div>
          <div class="muted" style="margin-top:6px;">Avg FI Velocity Score: <strong>{avg_vel}</strong> • Experiments Logged: <strong>{len(experiments)}</strong> • Retention Cohorts: <strong>{len(cohorts)}</strong></div>
        </div>
        <div style="margin-top:8px;">
          <div class="muted">FOR-PROGRESS iKPI ({ikpi_cur:,.0f} / {ikpi_tgt:,.0f} — {ikpi_pct}%)</div>
          <div style="font-size:14px;font-weight:700;margin:4px 0 8px;">{ikpi_name}</div>
          <div class="bar-track"><div class="bar-fill"></div></div>
        </div>
        <div style="margin-top:8px;">
          <div class="muted" style="margin-bottom:6px;">PACT COMMITMENT PIPELINE</div>
          <table>
            <thead><tr><th>Track</th><th>Closed Cash</th><th>Signed PACTs</th></tr></thead>
            <tbody>
              <tr><td>Customer Pilots / Pre-Orders</td><td><strong>${cust_closed:,.0f}</strong></td><td>${cust_signed:,.0f}</td></tr>
              <tr><td>Investor Soft-Circles</td><td><strong>${inv_closed:,.0f}</strong></td><td>${inv_signed:,.0f}</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="card">
      <h2>Exponential Thinking &amp; Singularity Readiness (ExO / 6Ds)</h2>
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
        <div>
          <div class="muted">MASSIVE TRANSFORMATIVE PURPOSE (MTP)</div>
          <div style="font-size:15px;font-weight:700;margin-top:4px;">{exo_mtp}</div>
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;">
          <span class="badge st-now">ExO Quotient: {exo_badge}</span>
          <span class="badge st-done">6Ds Stage: {exo_6d}</span>
        </div>
      </div>
    </section>

    <section class="card">
      <h2>Riskiest Assumptions Board (Ranked by Impact × Uncertainty)</h2>
      <table>
        <thead><tr><th>ID</th><th>Assumption Statement</th><th>Risk</th><th>Status</th></tr></thead>
        <tbody>{"".join(assump_rows)}</tbody>
      </table>
    </section>

    <footer class="foot">
      Startup Antigravity — Ethical Venture OS • Last compiled: {updated_at} • 10 Languages Supported • Zero external servers required
    </footer>
  </div>
  <script>
    const I18N = {locales_json_str};
    function applyLang(code) {{
      const L = I18N[code] || I18N.en;
      if (!L) return;
      document.documentElement.lang = code;
      document.documentElement.dir = L.rtl ? 'rtl' : 'ltr';
      const t = document.getElementById('i18n-title');
      if (t && L.appTitle) t.innerHTML = code === 'en' ? 'Startup <span>Command Center</span>' : L.appTitle;
      document.querySelectorAll('[data-i18n]').forEach(el => {{
        const parts = el.dataset.i18n.split('.');
        let cur = L;
        for (const p of parts) cur = cur && cur[p];
        if (typeof cur === 'string') el.textContent = cur;
      }});
      try {{ localStorage.setItem('sa_lang', code); }} catch (e) {{}}
    }}
    (function () {{
      let saved = "{default_locale}";
      try {{ saved = localStorage.getItem('sa_lang') || saved; }} catch (e) {{}}
      const sel = document.getElementById('lang-select');
      if (sel && I18N[saved]) {{ sel.value = saved; applyLang(saved); }}
    }})();
  </script>
</body>
</html>
"""


def build_dashboard(workspace_path: str | Path) -> dict[str, Any]:
    ws = Path(workspace_path).expanduser().resolve()
    out_dir = ws / "dashboard"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.html"
    out_file.write_text(render_dashboard_html(ws), encoding="utf-8")
    return {
        "dashboardPath": str(out_file),
        "workspace": str(ws),
        "tip": "Open dashboard/index.html in any browser for your live local Founder Command Center.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build live local Founder Command Center dashboard")
    parser.add_argument("--workspace", required=True)
    args = parser.parse_args()
    print(json.dumps(build_dashboard(args.workspace), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
