#!/usr/bin/env python3
"""
Startup Antigravity — 48-Hour Ethical Smoke-Test Landing Page Generator.

Reads `.startup/state.json` (plus optional `landing/landing.json`) and generates a
zero-dependency, deploy-ready single-file `landing/index.html` featuring:
  - Linted FI One-Sentence Pitch hero
  - Interactive client-side ROI calculator (vanilla JS)
  - Transparent 3-tier value pricing (zero dark patterns)
  - Mensarius Oath & For-Progress iKPI trust charter
  - 1-page Paid-Pilot PACT request generator (works statically on Cloudflare Pages / Netlify)
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any


def _default_landing_config(state: dict[str, Any]) -> dict[str, Any]:
    company = state.get("companyName") or "Your Startup"
    offering = state.get("offering") or "automated workflow software"
    audience = state.get("audience") or "high-velocity operators"
    problem = state.get("problem") or "eliminate costly manual bottlenecks"
    secret = state.get("secretSauce") or "purpose-built automation"
    pitch = state.get("fiOneSentencePitch") or (
        f"My company, {company}, is developing {offering} to help {audience} {problem} with {secret}."
    )
    ikpi_obj = state.get("ikpi") or {}
    ikpi_name = ikpi_obj.get("name") or "Measurable customer progress tracked monthly"

    return {
        "companyName": company,
        "heroHeadline": f"Help {audience.title()} {problem.capitalize()}",
        "heroSubheadline": pitch,
        "secretSauce": secret,
        "audience": audience,
        "contactEmail": "founder@company.com",
        "impactThesis": state.get("impactThesis")
        or f"Deliver measurable, ethical ROI for {audience} while compounding transparent value.",
        "ikpiName": ikpi_name,
        "roiDefaults": {
            "hoursWastedPerWeek": 12,
            "hourlyCostUsd": 85,
            "efficiencyGainPct": 75,
            "monthlyPriceUsd": 499,
        },
        "tiers": [
            {
                "name": "Starter",
                "price": "$199",
                "period": "/month",
                "badge": "",
                "summary": f"Core {offering} for solo operators.",
                "features": [
                    "Full core workflow automation",
                    "Self-serve 5-minute onboarding",
                    "100% customer-owned data export",
                    "Cancel anytime in 1 click",
                ],
                "cta": "Start Founding Pilot",
            },
            {
                "name": "Growth Pro",
                "price": "$499",
                "period": "/month",
                "badge": "MOST POPULAR",
                "summary": f"Full ROI suite built for growing {audience}.",
                "features": [
                    "Everything in Starter + team seats",
                    f"Powered by {secret}",
                    "Live ROI & savings tracking dashboard",
                    "Direct Slack / email founder support",
                ],
                "cta": "Request Paid Pilot PACT",
            },
            {
                "name": "Founding Annual",
                "price": "$4,790",
                "period": "/year (Save 20%)",
                "badge": "BEST VALUE",
                "summary": "Lock in founding-partner rate with 14-day ROI guarantee.",
                "features": [
                    "2 months free vs monthly billing",
                    "White-glove concierge migration",
                    "Direct roadmap influence with founders",
                    "100% refund if 14-day pilot goal missed",
                ],
                "cta": "Lock Founding Rate",
            },
        ],
    }


def render_landing_html(cfg: dict[str, Any]) -> str:
    company = html.escape(str(cfg["companyName"]))
    hero_h = html.escape(str(cfg["heroHeadline"]))
    hero_sub = html.escape(str(cfg["heroSubheadline"]))
    secret = html.escape(str(cfg["secretSauce"]))
    impact = html.escape(str(cfg["impactThesis"]))
    ikpi = html.escape(str(cfg["ikpiName"]))
    email = html.escape(str(cfg.get("contactEmail", "founder@company.com")))
    roi = cfg.get("roiDefaults") or {}
    hrs = int(roi.get("hoursWastedPerWeek", 12))
    rate = int(roi.get("hourlyCostUsd", 85))
    gain = int(roi.get("efficiencyGainPct", 75))
    price_mo = int(roi.get("monthlyPriceUsd", 499))

    tier_cards = []
    for t in cfg.get("tiers", []):
        badge = (
            f'<span class="tier-badge">{html.escape(str(t["badge"]))}</span>'
            if t.get("badge")
            else ""
        )
        featured = " featured" if t.get("badge") == "MOST POPULAR" else ""
        feats = "".join(f"<li>{html.escape(str(f))}</li>" for f in t.get("features", []))
        tier_cards.append(
            f'<div class="tier{featured}">'
            f'  <div class="tier-top"><h3>{html.escape(str(t.get("name", "")))}</h3>{badge}</div>'
            f'  <div class="tier-price">{html.escape(str(t.get("price", "")))}<span>{html.escape(str(t.get("period", "")))}</span></div>'
            f'  <p class="tier-sum">{html.escape(str(t.get("summary", "")))}</p>'
            f'  <ul>{feats}</ul>'
            f'  <a href="#pact" class="btn-tier">{html.escape(str(t.get("cta", "Get Started")))}</a>'
            f"</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{company} — Ethical Paid Pilot & ROI Calculator</title>
  <style>
    :root {{
      --bg: #0B1120;
      --surface: #111C33;
      --text: #F8FAFC;
      --muted: #94A3B8;
      --accent: #10B981;
      --accent2: #F59E0B;
      --border: #1E293B;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 24px; }}
    nav {{
      padding: 20px 0;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .logo {{ font-weight: 800; font-size: 19px; letter-spacing: -0.02em; }}
    .logo span {{ color: var(--accent); }}
    .nav-links {{ display: flex; gap: 22px; align-items: center; font-size: 14px; }}
    .nav-links a {{ color: var(--muted); text-decoration: none; }}
    .nav-links a:hover {{ color: var(--text); }}
    .cta-sm {{
      background: var(--accent);
      color: #052e16 !important;
      padding: 8px 16px;
      border-radius: 8px;
      font-weight: 700;
    }}
    .hero {{
      padding: 72px 0 56px;
      text-align: center;
    }}
    .pill {{
      display: inline-block;
      background: rgba(16, 185, 129, 0.14);
      border: 1px solid rgba(16, 185, 129, 0.35);
      color: #34D399;
      padding: 5px 14px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 18px;
    }}
    h1 {{
      font-size: clamp(32px, 5vw, 56px);
      line-height: 1.1;
      font-weight: 900;
      letter-spacing: -0.03em;
      max-width: 840px;
      margin: 0 auto 18px;
    }}
    .hero p {{
      font-size: clamp(16px, 1.9vw, 20px);
      color: var(--muted);
      max-width: 720px;
      margin: 0 auto 28px;
    }}
    .hero-actions {{ display: flex; justify-content: center; gap: 14px; flex-wrap: wrap; }}
    .btn-primary {{
      background: var(--accent);
      color: #052e16;
      padding: 13px 26px;
      border-radius: 10px;
      font-weight: 800;
      text-decoration: none;
      border: none;
      cursor: pointer;
      font-size: 15px;
    }}
    .btn-secondary {{
      background: var(--surface);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 13px 24px;
      border-radius: 10px;
      font-weight: 700;
      text-decoration: none;
      font-size: 15px;
    }}
    section {{ padding: 56px 0; border-top: 1px solid var(--border); }}
    h2 {{ font-size: clamp(24px, 3vw, 34px); font-weight: 800; margin-bottom: 10px; letter-spacing: -0.02em; }}
    .sec-sub {{ color: var(--muted); margin-bottom: 28px; max-width: 680px; }}

    /* ROI Calculator */
    .roi-grid {{
      display: grid;
      grid-template-columns: 1.1fr 1fr;
      gap: 24px;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 28px;
    }}
    .slider-row {{ margin-bottom: 18px; }}
    .slider-row label {{ display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 6px; }}
    .slider-row input[type="range"] {{ width: 100%; accent-color: var(--accent); }}
    .roi-results {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      align-content: center;
    }}
    .roi-stat {{
      background: rgba(11, 17, 32, 0.7);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px;
    }}
    .roi-val {{ font-size: 28px; font-weight: 900; color: var(--accent); }}
    .roi-lbl {{ font-size: 12px; color: var(--muted); margin-top: 4px; }}

    /* Pricing */
    .pricing-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }}
    .tier {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}
    .tier.featured {{ border-color: var(--accent); box-shadow: 0 0 0 1px var(--accent); }}
    .tier-top {{ display: flex; justify-content: space-between; align-items: center; }}
    .tier-badge {{
      font-size: 10px; font-weight: 800; padding: 3px 8px; border-radius: 999px;
      background: rgba(245, 158, 11, 0.18); color: var(--accent2);
    }}
    .tier-price {{ font-size: 34px; font-weight: 900; color: var(--text); }}
    .tier-price span {{ font-size: 14px; font-weight: 500; color: var(--muted); margin-left: 4px; }}
    .tier-sum {{ font-size: 14px; color: var(--muted); }}
    .tier ul {{ list-style: none; display: flex; flex-direction: column; gap: 8px; flex: 1; font-size: 14px; }}
    .tier li::before {{ content: "✓ "; color: var(--accent); font-weight: 800; }}
    .btn-tier {{
      display: block; text-align: center; padding: 11px; border-radius: 8px;
      background: rgba(16, 185, 129, 0.15); color: #34D399; border: 1px solid rgba(16, 185, 129, 0.4);
      font-weight: 700; text-decoration: none;
    }}
    .tier.featured .btn-tier {{ background: var(--accent); color: #052e16; border-color: var(--accent); }}

    /* Ethics Strip */
    .ethics-box {{
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(245, 158, 11, 0.08));
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 24px 28px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
    }}

    /* PACT Form */
    .pact-form {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 28px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }}
    .pact-form .full {{ grid-column: 1 / -1; }}
    .pact-form label {{ display: block; font-size: 13px; color: var(--muted); margin-bottom: 6px; }}
    .pact-form input, .pact-form select, .pact-form textarea {{
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      color: var(--text);
      font-size: 14px;
    }}
    .pact-preview {{
      display: none;
      margin-top: 18px;
      background: #090D16;
      border: 1px solid var(--accent);
      border-radius: 10px;
      padding: 18px;
      font-family: ui-monospace, monospace;
      font-size: 13px;
      white-space: pre-wrap;
    }}
    footer {{
      padding: 32px 0;
      border-top: 1px solid var(--border);
      font-size: 13px;
      color: var(--muted);
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }}
    @media (max-width: 820px) {{
      .roi-grid, .pricing-grid, .ethics-box, .pact-form {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <nav>
      <div class="logo">{company}<span>.</span></div>
      <div class="nav-links">
        <a href="#roi">ROI Calculator</a>
        <a href="#pricing">Transparent Pricing</a>
        <a href="#ethics">For-Progress Charter</a>
        <a href="#pact" class="cta-sm">Book Paid Pilot</a>
      </div>
    </nav>

    <header class="hero">
      <div class="pill">Secret Sauce: {secret}</div>
      <h1>{hero_h}</h1>
      <p>{hero_sub}</p>
      <div class="hero-actions">
        <a href="#pact" class="btn-primary">Sign 14-Day Paid Pilot PACT</a>
        <a href="#roi" class="btn-secondary">Calculate Your ROI</a>
      </div>
    </header>

    <section id="roi">
      <h2>Calculate Your Monthly ROI</h2>
      <p class="sec-sub">Transparent math — adjust the sliders to match your team's current workflow.</p>
      <div class="roi-grid">
        <div>
          <div class="slider-row">
            <label><span>Hours lost per week</span><strong id="hrsLbl">{hrs} hrs/wk</strong></label>
            <input type="range" id="hrsIn" min="2" max="60" value="{hrs}" />
          </div>
          <div class="slider-row">
            <label><span>Loaded hourly cost</span><strong id="rateLbl">${rate}/hr</strong></label>
            <input type="range" id="rateIn" min="25" max="250" step="5" value="{rate}" />
          </div>
          <div class="slider-row">
            <label><span>Expected automation gain</span><strong id="gainLbl">{gain}%</strong></label>
            <input type="range" id="gainIn" min="30" max="90" step="5" value="{gain}" />
          </div>
        </div>
        <div class="roi-results">
          <div class="roi-stat"><div class="roi-val" id="moSave">$0</div><div class="roi-lbl">Estimated Monthly Value</div></div>
          <div class="roi-stat"><div class="roi-val" id="yrSave">$0</div><div class="roi-lbl">Estimated Annual ROI</div></div>
          <div class="roi-stat"><div class="roi-val" id="roiMult">0x</div><div class="roi-lbl">Value-to-Price Multiple</div></div>
          <div class="roi-stat"><div class="roi-val" id="paybackDays">0d</div><div class="roi-lbl">Estimated Payback Period</div></div>
        </div>
      </div>
    </section>

    <section id="pricing">
      <h2>Transparent, Value-Based Pricing</h2>
      <p class="sec-sub">No hidden fees. No fake countdown timers. 1-click cancellation and 100% customer-owned data.</p>
      <div class="pricing-grid">
        {"".join(tier_cards)}
      </div>
    </section>

    <section id="ethics">
      <div class="ethics-box">
        <div>
          <div class="pill" style="margin-bottom:10px;">Mensarius Ethical Guarantee</div>
          <h3>Zero Dark Patterns, Ever</h3>
          <p style="color:var(--muted);font-size:14px;margin-top:6px;">
            Your data stays 100% yours with instant export. Pricing is public and honest. If our 14-day pilot fails to hit the agreed deliverable, you pay $0.
          </p>
        </div>
        <div>
          <div class="pill" style="margin-bottom:10px;">FI For-Progress iKPI</div>
          <h3>{ikpi}</h3>
          <p style="color:var(--muted);font-size:14px;margin-top:6px;">{impact}</p>
        </div>
      </div>
    </section>

    <section id="pact">
      <h2>Start a 14-Day Founding Partner Paid Pilot (PACT)</h2>
      <p class="sec-sub">Generate a crisp, transparent 1-page pilot intent agreement with zero obligation until we both confirm kickoff.</p>
      <form class="pact-form" id="pactForm">
        <div>
          <label for="buyerName">Your Name</label>
          <input id="buyerName" required placeholder="Alex Rivera" />
        </div>
        <div>
          <label for="buyerCompany">Company</label>
          <input id="buyerCompany" required placeholder="Acme Clinic Group" />
        </div>
        <div>
          <label for="buyerEmail">Work Email</label>
          <input id="buyerEmail" type="email" required placeholder="alex@acme.com" />
        </div>
        <div>
          <label for="pilotTier">Selected Tier</label>
          <select id="pilotTier">
            <option value="Growth Pro ($499/mo)">Growth Pro ($499/mo)</option>
            <option value="Starter ($199/mo)">Starter ($199/mo)</option>
            <option value="Founding Annual ($4,790/yr)">Founding Annual ($4,790/yr)</option>
          </select>
        </div>
        <div class="full">
          <label for="pilotGoal">Primary 14-Day Measurable Outcome You Want Solved</label>
          <textarea id="pilotGoal" rows="3" required placeholder="Example: Cut weekly reconciliation time by 75% before month-end close."></textarea>
        </div>
        <div class="full" style="display:flex;gap:12px;flex-wrap:wrap;">
          <button type="submit" class="btn-primary">Generate 1-Page Pilot PACT</button>
          <a id="mailtoLink" class="btn-secondary" style="display:none;" href="#">Send via Email</a>
        </div>
      </form>
      <pre class="pact-preview" id="pactPreview"></pre>
    </section>

    <footer>
      <span>© {company} — Built with Startup Antigravity (Ethical Venture OS)</span>
      <span>Contact: {email}</span>
    </footer>
  </div>

  <script>
    (function () {{
      const PRICE_MO = {price_mo};
      const hrsIn = document.getElementById("hrsIn");
      const rateIn = document.getElementById("rateIn");
      const gainIn = document.getElementById("gainIn");

      function updateROI() {{
        const h = Number(hrsIn.value);
        const r = Number(rateIn.value);
        const g = Number(gainIn.value) / 100;
        document.getElementById("hrsLbl").textContent = h + " hrs/wk";
        document.getElementById("rateLbl").textContent = "$" + r + "/hr";
        document.getElementById("gainLbl").textContent = Math.round(g * 100) + "%";

        const mo = Math.round(h * 4.33 * r * g);
        const yr = mo * 12;
        const mult = (mo / Math.max(PRICE_MO, 1)).toFixed(1);
        const days = Math.max(1, Math.round((PRICE_MO / Math.max(mo, 1)) * 30));

        document.getElementById("moSave").textContent = "$" + mo.toLocaleString();
        document.getElementById("yrSave").textContent = "$" + yr.toLocaleString();
        document.getElementById("roiMult").textContent = mult + "x";
        document.getElementById("paybackDays").textContent = days + "d";
      }}

      [hrsIn, rateIn, gainIn].forEach((el) => el.addEventListener("input", updateROI));
      updateROI();

      document.getElementById("pactForm").addEventListener("submit", function (e) {{
        e.preventDefault();
        const name = document.getElementById("buyerName").value.trim();
        const comp = document.getElementById("buyerCompany").value.trim();
        const mail = document.getElementById("buyerEmail").value.trim();
        const tier = document.getElementById("pilotTier").value;
        const goal = document.getElementById("pilotGoal").value.trim();
        const text = [
          "FOUNDING PARTNER PAID PILOT PACT — {company}",
          "--------------------------------------------------",
          "Customer: " + name + " (" + comp + " | " + mail + ")",
          "Selected Plan: " + tier,
          "14-Day Core Deliverable: " + goal,
          "Ethical Guarantee: 100% customer-owned data; $0 owed if 14-day deliverable is not met.",
        ].join("\\n");
        const pre = document.getElementById("pactPreview");
        pre.textContent = text;
        pre.style.display = "block";
        const ml = document.getElementById("mailtoLink");
        ml.href = "mailto:{email}?subject=" + encodeURIComponent("Paid Pilot PACT — " + comp) + "&body=" + encodeURIComponent(text);
        ml.style.display = "inline-block";
      }});
    }})();
  </script>
</body>
</html>
"""


def build_landing_page(
    workspace_path: str | Path,
    overrides: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate landing/landing.json and deploy-ready landing/index.html."""
    ws = Path(workspace_path).expanduser().resolve()
    state_file = ws / ".startup" / "state.json"
    state = json.loads(state_file.read_text(encoding="utf-8")) if state_file.exists() else {}

    out_dir = ws / "landing"
    out_dir.mkdir(parents=True, exist_ok=True)
    cfg_file = out_dir / "landing.json"

    if cfg_file.exists():
        cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
    else:
        cfg = _default_landing_config(state)

    if overrides:
        cfg.update(overrides)

    cfg_file.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    html_file = out_dir / "index.html"
    html_file.write_text(render_landing_html(cfg), encoding="utf-8")

    return {
        "configPath": str(cfg_file),
        "htmlPath": str(html_file),
        "companyName": cfg["companyName"],
        "deployHint": "Drop landing/ onto Cloudflare Pages, Netlify, or GitHub Pages — zero build step required.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build 48-hour smoke-test landing page")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--email", help="Founder contact email for PACT form")
    args = parser.parse_args()
    overrides = {"contactEmail": args.email} if args.email else None
    print(json.dumps(build_landing_page(args.workspace, overrides), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
