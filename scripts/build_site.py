#!/usr/bin/env python3
"""Build the public GitHub Pages showcase + live SolarLedger interactive demo into site_dist/."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from generate_demo_workspace import generate_demo_workspace  # noqa: E402

REPO_URL = "https://github.com/petebiggam357/StartupAntigravity"


def build_site(out_dir: Path) -> dict[str, str]:
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    version = str(manifest["version"])
    tag = f"v{version}"
    rel_base = f"{REPO_URL}/releases/download/{tag}"

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / ".nojekyll").write_text("", encoding="utf-8")

    # Copy logo SVG
    shutil.copy2(ROOT / "assets" / "logo.svg", out_dir / "logo.svg")

    # Build live interactive SolarLedger demo inside site_dist/demo/
    demo_dir = out_dir / "demo"
    generate_demo_workspace(demo_dir)

    esc_ver = html.escape(version)
    esc_tag = html.escape(tag)

    index_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Startup Antigravity — Ethical Venture OS ({esc_tag})</title>
  <meta name="description" content="Open-source Founder Operating System for Google Antigravity: 19 skills, 8 advisory subagents, 22 MCP tools, 48 resources, AI margin & x402 calculators, pitch deck engine, and native desktop installers." />
  <link rel="icon" type="image/svg+xml" href="logo.svg" />
  <style>
    :root {{ --bg:#020617; --surface:#0f172a; --card:#111c33; --border:#1e293b; --text:#f8fafc; --muted:#94a3b8; --emerald:#10b981; --amber:#f59e0b; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--text); line-height:1.6; }}
    .wrap {{ max-width:1080px; margin:0 auto; padding:28px 20px 72px; }}
    nav {{ display:flex; align-items:center; justify-content:space-between; gap:16px; padding-bottom:28px; border-bottom:1px solid var(--border); flex-wrap:wrap; }}
    .logo-row {{ display:flex; align-items:center; gap:12px; text-decoration:none; color:var(--text); font-weight:800; font-size:18px; }}
    .logo-row img {{ width:36px; height:36px; }}
    .nav-links {{ display:flex; gap:18px; align-items:center; flex-wrap:wrap; }}
    .nav-links a {{ color:var(--muted); text-decoration:none; font-weight:600; font-size:14px; }}
    .nav-links a:hover {{ color:var(--text); }}
    .hero {{ padding:52px 0 36px; text-align:center; }}
    .pill {{ display:inline-block; padding:4px 12px; border-radius:999px; background:#064e3b; color:#6ee7b7; font-size:12px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; }}
    h1 {{ font-size:clamp(32px,5vw,52px); line-height:1.12; margin:16px auto 14px; max-width:860px; }}
    .sub {{ color:var(--muted); font-size:18px; max-width:740px; margin:0 auto 28px; }}
    .cta-row {{ display:flex; gap:12px; justify-content:center; flex-wrap:wrap; margin-bottom:20px; }}
    .btn {{ display:inline-block; padding:12px 20px; border-radius:10px; font-weight:700; text-decoration:none; border:1px solid #334155; color:var(--text); background:var(--surface); }}
    .btn.primary {{ background:var(--emerald); color:#022c22; border-color:var(--emerald); }}
    .btn.amber {{ background:var(--amber); color:#1c1917; border-color:var(--amber); }}
    .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:12px; margin:32px 0; }}
    .stat {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px; text-align:center; }}
    .stat strong {{ display:block; font-size:26px; color:var(--emerald); }}
    .stat span {{ font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.04em; }}
    h2 {{ font-size:26px; margin:48px 0 14px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; }}
    .card {{ background:var(--card); border:1px solid var(--border); border-radius:14px; padding:20px; }}
    .card h3 {{ margin:0 0 8px; font-size:17px; color:var(--text); }}
    .card p {{ margin:0; color:var(--muted); font-size:14px; }}
    .dl-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin-top:16px; }}
    .dl-card {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:16px; text-decoration:none; color:var(--text); display:flex; flex-direction:column; gap:6px; }}
    .dl-card:hover {{ border-color:var(--emerald); }}
    .dl-card .os {{ font-weight:800; color:var(--emerald); }}
    .dl-card .file {{ font-family:monospace; font-size:12px; color:var(--muted); word-break:break-all; }}
    pre {{ background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:16px; overflow:auto; font-size:13px; color:#e2e8f0; }}
    .notice {{ margin-top:44px; padding:18px; border-radius:12px; background:#0f172a; border:1px solid var(--border); color:var(--muted); font-size:13px; }}
    footer {{ margin-top:32px; text-align:center; color:var(--muted); font-size:13px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <nav>
      <a class="logo-row" href="#">
        <img src="logo.svg" alt="Startup Antigravity Logo" />
        <span>Startup Antigravity</span>
      </a>
      <div class="nav-links">
        <a href="#downloads">Downloads</a>
        <a href="#demo">Live Demo</a>
        <a href="#features">What's Inside</a>
        <a href="{REPO_URL}" target="_blank" rel="noopener">GitHub Repo</a>
      </div>
    </nav>

    <section class="hero">
      <span class="pill">Open Source • {esc_tag} • Zero Dependencies</span>
      <h1>The Ethical Venture OS for Google Antigravity</h1>
      <p class="sub">
        Install one plugin, open an empty folder, and build a high-margin, AI-native, fundable startup from scratch — uniting Founder Institute execution, VC Lab / Mensarius Oath ethics, and x402 programmable finance.
      </p>
      <div class="cta-row">
        <a id="smart-dl" class="btn primary" href="{REPO_URL}/releases/tag/{esc_tag}">Download {esc_tag}</a>
        <a class="btn amber" href="demo/dashboard/index.html">Launch Startup Command Center Demo</a>
        <a class="btn" href="{REPO_URL}" target="_blank" rel="noopener">View on GitHub</a>
      </div>
    </section>

    <section class="stats">
      <div class="stat"><strong>19</strong><span>Startup Skills</span></div>
      <div class="stat"><strong>8</strong><span>Advisory Subagents</span></div>
      <div class="stat"><strong>24</strong><span>Local MCP Tools</span></div>
      <div class="stat"><strong>48+</strong><span>Curated Resources</span></div>
      <div class="stat"><strong>4</strong><span>Safety Hooks</span></div>
      <div class="stat"><strong>$0</strong><span>Dependencies</span></div>
    </section>

    <section id="demo">
      <h2>Explore the Live Startup Command Center Demo (Zero Install)</h2>
      <p style="color:var(--muted);margin-top:0;">Every artifact below was compiled directly by Startup Antigravity's zero-dependency engines:</p>
      <div class="grid">
        <a class="dl-card" href="demo/dashboard/index.html">
          <span class="os">1. Startup Command Center</span>
          <span class="file">FI stage bar, MRR/runway KPIs, Sean Ellis 40% PMF SVG gauge, PACT pipeline &amp; iKPI bar</span>
        </a>
        <a class="dl-card" href="demo/pitch-deck/index.html">
          <span class="os">2. 13-Slide Interactive Pitch Deck</span>
          <span class="file">Researched ClaimPulse Pre-Seed deck with inline SVG charts, 2×2 quadrant, 3-min timer (T) &amp; PDF export</span>
        </a>
        <a class="dl-card" href="demo/data-room/index.html">
          <span class="os">3. Investor Data Room Portal</span>
          <span class="file">100% readiness VC Lab / FI diligence pack with PII-redacted customer proof</span>
        </a>
        <a class="dl-card" href="demo/landing/index.html">
          <span class="os">4. 48-Hour Smoke-Test Landing Page</span>
          <span class="file">Interactive ROI calculator, 3-tier transparent pricing &amp; Paid-Pilot PACT intake</span>
        </a>
      </div>
    </section>

    <section id="downloads">
      <h2>Native Desktop Packages ({esc_tag})</h2>
      <p style="color:var(--muted);margin-top:0;">No terminal required — double-click to install offline, copy starter prompts, or launch the local Web Studio.</p>
      <div class="dl-grid">
        <a class="dl-card" href="{rel_base}/StartupAntigravity-{esc_tag}-x86_64.AppImage">
          <span class="os">Linux Portable (.AppImage)</span>
          <span class="file">StartupAntigravity-{esc_tag}-x86_64.AppImage</span>
        </a>
        <a class="dl-card" href="{rel_base}/startup-antigravity_{esc_ver}_all.deb">
          <span class="os">Ubuntu / Pop!_OS / Debian (.deb)</span>
          <span class="file">startup-antigravity_{esc_ver}_all.deb</span>
        </a>
        <a class="dl-card" href="{rel_base}/StartupAntigravity-{esc_tag}-macos-arm64.dmg">
          <span class="os">macOS (.dmg)</span>
          <span class="file">StartupAntigravity-{esc_tag}-macos-arm64.dmg</span>
        </a>
        <a class="dl-card" href="{rel_base}/StartupAntigravity-{esc_tag}-win64.exe">
          <span class="os">Windows 10 &amp; 11 (.exe)</span>
          <span class="file">StartupAntigravity-{esc_tag}-win64.exe</span>
        </a>
        <a class="dl-card" href="{rel_base}/startup-antigravity-{esc_tag}.zip">
          <span class="os">Universal Plugin Archive (.zip)</span>
          <span class="file">startup-antigravity-{esc_tag}.zip</span>
        </a>
      </div>

      <pre><code># Or install in 1 command from terminal (macOS / Linux):
git clone {REPO_URL}.git &amp;&amp; cd StartupAntigravity &amp;&amp; ./install.sh

# Launch unified local Studio in your browser:
startup-antigravity --serve .</code></pre>
    </section>

    <section id="features">
      <h2>Built for Every Stage &amp; Every Founder Level</h2>
      <div class="grid">
        <div class="card">
          <h3>Revenue-First &amp; PMF Engine</h3>
          <p>7–14 day Paid-Pilot PACTs, Mom Test call-transcript extractor, Sean Ellis 40% Very Disappointed segmentation, and cohort retention checks.</p>
        </div>
        <div class="card">
          <h3>AI-Native &amp; x402 Finance</h3>
          <p>Deterministic AI token COGS &amp; 75% margin modeler, HTTP 402 USDC agent micropayment starter scaffold, stablecoin rails, and Mensarius token guardrails.</p>
        </div>
        <div class="card">
          <h3>Design, Cloud &amp; CFO Bridges</h3>
          <p>Seamless handoffs for Canva, Figma Slides, Replit Free-Tier Launchpad, QuickBooks Online CFO Copilot, Zapier (9,000+ apps), Dipity Studio &amp; Shelled AI.</p>
        </div>
        <div class="card">
          <h3>Hardened Safety Hooks</h3>
          <p>Blocks hardcoded wallet private keys &amp; live API secrets, confirms mainnet broadcasts, guards Data Room PII, and auto-syncs decks &amp; dashboards.</p>
        </div>
      </div>
    </section>

    <div class="notice">
      <strong>Independence &amp; Attribution Notice:</strong> Startup Antigravity is an independent, community-built open-source plugin created by a Previous Founder Institute Director, Current FI Mentor &amp; Advisor, and Former Startup Grind Monterey Bay Chapter Director. It is <strong>not</strong> an official product or release of Founder Institute (fi.co), VC Lab / Decile Group (govclab.com), Startup Grind, or Founders Guild.
    </div>

    <footer>MIT License • <a href="{REPO_URL}" style="color:var(--emerald);text-decoration:none;">petebiggam357/StartupAntigravity</a></footer>
  </div>

  <script>
    (function () {{
      const ua = navigator.userAgent.toLowerCase();
      const btn = document.getElementById('smart-dl');
      const base = "{rel_base}";
      if (ua.includes('win')) {{
        btn.href = base + "/StartupAntigravity-{esc_tag}-win64.exe";
        btn.textContent = "Download for Windows (.exe)";
      }} else if (ua.includes('mac')) {{
        btn.href = base + "/StartupAntigravity-{esc_tag}-macos-arm64.dmg";
        btn.textContent = "Download for macOS (.dmg)";
      }} else if (ua.includes('linux')) {{
        btn.href = base + "/StartupAntigravity-{esc_tag}-x86_64.AppImage";
        btn.textContent = "Download for Linux (.AppImage)";
      }}
    }})();
  </script>
</body>
</html>
"""
    (out_dir / "index.html").write_text(index_html, encoding="utf-8")
    return {"siteDir": str(out_dir), "indexHtml": str(out_dir / "index.html"), "demoDir": str(demo_dir)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build public GitHub Pages site + live demo.")
    parser.add_argument("--out-dir", default=str(ROOT / "site_dist"))
    args = parser.parse_args(argv)
    print(json.dumps(build_site(Path(args.out_dir)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
