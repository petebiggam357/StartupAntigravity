#!/usr/bin/env python3
"""Zero-dependency local HTTP Studio server for Startup Antigravity (v0.5.0-beta).

Serves a unified, 10-language tabbed dark-mode web workspace on http://127.0.0.1:<port> combining:
  - Startup Command Center Dashboard  (/workspace/dashboard/index.html)
  - 13-Slide Interactive Pitch Deck   (/workspace/pitch-deck/index.html)
  - Single-File Investor Data Room    (/workspace/data-room/index.html)
  - Browser Voice Pitch Rehearsal     (POST /api/voice-coach + live Web Speech API telemetry)
  - 4-Exec War Room + Scenario Presets(POST /api/war-room)
  - Metered x402 Agent Storefront     (POST /api/x402/agent-call & GET /api/x402/ledger)
  - 3-Lens Board Review               (GET /api/board-review)
  - Embedded Cohort Portfolio View    (GET /api/portfolio)
  - Visual Slide Editor + Live Themes (GET/POST /api/deck)
  - 1-Click Snapshot Export & Restore (GET /api/export-snapshot & POST /api/import-snapshot)
  - Live 54+ Resource Library Search  (GET /api/resources)
  - Live Metric Editor & Switcher     (POST /api/metrics & POST /api/workspace)
"""

from __future__ import annotations

import html
import json
import mimetypes
import re
import subprocess
import sys
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
MAX_JSON_BODY_BYTES = 10 * 1024 * 1024  # 10 MB safety limit for local Studio API requests
THEME_PALETTE_KEYS = ("bg", "surface", "text", "muted", "accent", "accent2", "border")
_SAFE_STARTUP_JSON_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.json$")


def _workspace_fingerprint(workspace: Path) -> float:
    latest = 0.0
    for rel in (".startup", "dashboard", "pitch-deck", "data-room", "landing"):
        d = workspace / rel
        if d.exists():
            for p in d.rglob("*"):
                if p.is_file():
                    try:
                        m = p.stat().st_mtime
                        if m > latest:
                            latest = m
                    except OSError:
                        pass
    return round(latest, 3)


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _build_snapshot_dict(ws: Path) -> dict[str, Any]:
    snap: dict[str, Any] = {
        "ok": True,
        "schemaVersion": "1.0",
        "exportedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workspace": ws.name,
        "startup": {},
        "deck": None,
    }
    sdir = ws / ".startup"
    if sdir.exists():
        for jf in sorted(sdir.glob("*.json")):
            snap["startup"][jf.name] = _load_json(jf, {})
    deck_file = ws / "pitch-deck" / "deck.json"
    if deck_file.exists():
        snap["deck"] = _load_json(deck_file, None)
    return snap


def validate_snapshot_payload(body: Any) -> tuple[bool, str]:
    """Validate an imported workspace snapshot JSON before restoring."""
    if not isinstance(body, dict):
        return False, "Snapshot payload must be a JSON object."

    startup = body.get("startup")
    deck = body.get("deck")

    if startup is not None and not isinstance(startup, dict):
        return False, "'startup' must be a JSON object mapping filenames to JSON data."

    startup_map: dict[str, Any] = startup or {}
    for fname, content in startup_map.items():
        if not isinstance(fname, str) or not fname.endswith(".json"):
            return False, f"Invalid startup filename: {fname!r} (must end with .json)."
        if Path(fname).name != fname or ".." in fname or "/" in fname or "\\" in fname or not _SAFE_STARTUP_JSON_RE.match(fname):
            return False, f"Unsafe startup filename rejected: {fname!r}."
        if fname == "state.json" and not isinstance(content, dict):
            return False, "'startup.state.json' must be a JSON object."
        if not isinstance(content, (dict, list)):
            return False, f"Startup file {fname!r} must contain a JSON object or array."

    if deck is not None:
        if not isinstance(deck, dict):
            return False, "'deck' must be a JSON object or null."
        if "slides" in deck:
            slides = deck["slides"]
            if not isinstance(slides, list) or not all(isinstance(s, dict) for s in slides):
                return False, "'deck.slides' must be a list of slide objects."

    if not startup_map and deck is None:
        return False, "Snapshot must include at least one '.startup/*.json' file or a 'deck' object."

    return True, ""


def _rebuild_views(ws: Path, p_root: Path) -> None:
    dash_script = p_root / "skills" / "unit-economics-and-profit-os" / "scripts" / "build_dashboard.py"
    if dash_script.exists():
        subprocess.run([sys.executable, str(dash_script), "--workspace", str(ws)], check=False, capture_output=True)
    dr_script = p_root / "skills" / "vc-lab-fundraising-os" / "scripts" / "build_data_room.py"
    if dr_script.exists() and (ws / "data-room" / "index.html").exists():
        subprocess.run([sys.executable, str(dr_script), "--workspace", str(ws)], check=False, capture_output=True)


def render_studio_shell(workspace: Path, plugin_root: Path) -> str:
    state = _load_json(workspace / ".startup" / "state.json", {})
    company = state.get("companyName") or workspace.name
    stage = state.get("stage") or "idea"
    default_locale = str(state.get("locale") or "en")

    all_locales = _load_json(plugin_root / "i18n" / "locales.json", {})
    if default_locale not in all_locales:
        default_locale = "en"
    locales_json = json.dumps(all_locales, ensure_ascii=False).replace("</", "<\\/")
    lang_opts = "".join(
        f'<option value="{code}"{" selected" if code == default_locale else ""}>{html.escape(data.get("nativeName", code))}</option>'
        for code, data in all_locales.items()
    )

    esc_company = html.escape(str(company))
    esc_stage = html.escape(str(stage))

    return f"""<!doctype html>
<html lang="{html.escape(default_locale)}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{esc_company} — Startup Antigravity Studio</title>
  <style>
    :root {{ --bg:#020617; --nav:#0f172a; --card:#1e293b; --border:#334155; --text:#f8fafc; --muted:#94a3b8; --accent:#10b981; --amber:#f59e0b; }}
    * {{ box-sizing:border-box; }}
    html,body {{ margin:0; height:100%; font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--text); display:flex; flex-direction:column; }}
    header {{ display:flex; align-items:center; gap:10px; padding:10px 16px; background:var(--nav); border-bottom:1px solid var(--border); flex-wrap:wrap; }}
    .brand {{ font-weight:800; color:var(--accent); letter-spacing:.03em; font-size:14px; }}
    .pill {{ font-size:11px; padding:2px 8px; border-radius:999px; background:#064e3b; color:#6ee7b7; font-weight:700; text-transform:uppercase; }}
    nav {{ display:flex; gap:5px; flex-wrap:wrap; margin-left:auto; align-items:center; }}
    button.tab, select.lang {{ background:transparent; border:1px solid var(--border); color:var(--muted); padding:5px 10px; border-radius:8px; cursor:pointer; font-weight:600; font-size:12px; }}
    select.lang {{ background:#020617; color:var(--text); }}
    button.tab.active {{ background:var(--accent); color:#022c22; border-color:var(--accent); }}
    main {{ flex:1; position:relative; display:flex; overflow:hidden; }}
    iframe {{ width:100%; height:100%; border:0; background:#0b1120; }}
    .panel {{ display:none; width:100%; height:100%; overflow:auto; padding:24px; max-width:1100px; margin:0 auto; }}
    .search-bar, textarea.box, input.box {{ width:100%; padding:11px 13px; border-radius:10px; border:1px solid var(--border); background:var(--nav); color:var(--text); font-size:14px; margin-bottom:14px; font-family:inherit; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:14px; }}
    .card {{ background:var(--nav); border:1px solid var(--border); border-radius:12px; padding:16px; display:flex; flex-direction:column; gap:8px; }}
    .cat {{ font-size:11px; color:var(--amber); text-transform:uppercase; font-weight:700; letter-spacing:.05em; }}
    .card a {{ color:var(--accent); font-weight:700; text-decoration:none; font-size:15px; }}
    .card p {{ margin:0; color:var(--muted); font-size:13px; line-height:1.45; }}
    .takeaway {{ font-size:12px; color:#e2e8f0; background:#1e293b; padding:8px 10px; border-radius:8px; }}
    .score-val {{ font-size:28px; font-weight:800; color:var(--accent); }}
    .modal-bg {{ display:none; position:fixed; inset:0; background:rgba(2,6,23,.78); align-items:center; justify-content:center; z-index:99; }}
    .modal {{ background:var(--nav); border:1px solid var(--border); border-radius:14px; padding:22px; width:min(460px,92vw); display:grid; gap:10px; }}
    .modal label {{ font-size:12px; color:var(--muted); font-weight:700; display:grid; gap:4px; }}
    .modal input, .modal select {{ padding:8px 10px; border-radius:8px; border:1px solid var(--border); background:#020617; color:var(--text); font-size:14px; }}
  </style>
</head>
<body>
  <header>
    <span class="brand" id="studio-brand">STARTUP ANTIGRAVITY STUDIO</span>
    <span style="color:#cbd5e1;font-weight:700;">{esc_company}</span>
    <span class="pill">{esc_stage}</span>
    <nav>
      <button class="tab active" data-tab="dashboard" data-i18n="nav.dashboard" onclick="selectTab('dashboard')">Command Center</button>
      <button class="tab" data-tab="deck" data-i18n="nav.deck" onclick="selectTab('deck')">Pitch Deck</button>
      <button class="tab" data-tab="dataroom" data-i18n="nav.dataroom" onclick="selectTab('dataroom')">Data Room</button>
      <button class="tab" data-tab="voice" data-i18n="nav.voice" onclick="selectTab('voice')">Voice Coach</button>
      <button class="tab" data-tab="warroom" data-i18n="nav.warroom" onclick="selectTab('warroom')">War Room</button>
      <button class="tab" data-tab="x402" data-i18n="nav.x402" onclick="selectTab('x402')">x402 Storefront</button>
      <button class="tab" data-tab="board" data-i18n="nav.board" onclick="selectTab('board')">Board Review</button>
      <button class="tab" data-tab="portfolio" onclick="selectTab('portfolio')">Portfolio</button>
      <button class="tab" data-tab="rhythm" onclick="selectTab('rhythm')">Weekly Rhythm</button>
      <button class="tab" data-tab="resources" data-i18n="nav.resources" onclick="selectTab('resources')">54+ Resources</button>
      <button class="tab" data-tab="editor" onclick="selectTab('editor')" style="border-color:#a855f7;color:#d8b4fe;">Slide Editor</button>
      <button class="tab" onclick="openOnboardModal()" style="border-color:#10b981;color:#6ee7b7;">Setup Wizard</button>
      <button class="tab" data-i18n="nav.editMetrics" onclick="openMetricsModal()" style="border-color:#f59e0b;color:#fbbf24;">Edit Metrics</button>
      <button class="tab" onclick="exportSnapshot()" style="border-color:#64748b;color:#cbd5e1;">Export Snapshot</button>
      <button class="tab" onclick="triggerImportSnapshot()" style="border-color:#64748b;color:#cbd5e1;">Import Snapshot</button>
      <input id="import-snap-file" type="file" accept=".json,application/json" style="display:none" onchange="importSnapshotFile(this)" />
      <button class="tab" onclick="publishLive()" style="border-color:#38bdf8;color:#7dd3fc;">Publish Live</button>
      <select id="studio-lang" class="lang" aria-label="Language" onchange="applyStudioLang(this.value)">{lang_opts}</select>
    </nav>
  </header>
  <main>
    <iframe id="viewport" src="/workspace/dashboard/index.html"></iframe>

    <div id="voice-panel" class="panel">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px;">
        <h2 style="margin:0;">Browser Voice Pitch Rehearsal Studio &amp; VC Lab Partner Q&amp;A</h2>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
          <span id="vc-status" class="pill" style="background:#1e293b;color:#94a3b8;">READY</span>
          <span id="vc-timer" class="pill" style="font-size:14px;padding:6px 12px;">03:00</span>
          <button id="vc-mic-btn" class="tab active" onclick="toggleVoiceMic()">Start 3-Min Mic Pitch</button>
          <button class="tab" onclick="scoreVoicePitch()">Analyze Transcript</button>
          <button class="tab" onclick="resetVoiceRehearsal()">Reset</button>
          <button class="tab" onclick="downloadReport('voice-coach-scorecard.md', lastVoiceMd)">Download .md</button>
        </div>
      </div>
      <div class="grid" style="margin-bottom:14px;">
        <div class="card"><div class="cat">Live Pace (Target 125–165 WPM)</div><div id="vc-live-wpm" class="score-val">0 WPM</div><div id="vc-live-words" style="color:var(--muted);font-size:12px;">0 words • 0s elapsed</div></div>
        <div class="card"><div class="cat">Live Filler Words</div><div id="vc-live-fillers" class="score-val" style="color:var(--amber);">0</div><div id="vc-live-filler-list" style="color:var(--muted);font-size:12px;">um, uh, like, you know, basically...</div></div>
        <div class="card"><div class="cat">Live FI Buzzwords</div><div id="vc-live-buzz" class="score-val" style="color:#f43f5e;">0</div><div id="vc-live-buzz-list" style="color:var(--muted);font-size:12px;">Clean — zero empty superlatives</div></div>
      </div>
      <textarea id="vc-transcript" class="box" rows="5" oninput="updateLiveVoiceTelemetry()" placeholder="Click 'Start 3-Min Mic Pitch' (Web Speech API) or paste your 3-minute FI pitch transcript here..."></textarea>
      <div id="vc-results" style="color:var(--muted);">Speak or paste your pitch to track live WPM + filler words in real time, then pipe straight into <code>voice_pitch_coach</code> for Partner Q&amp;A.</div>
    </div>

    <div id="warroom-panel" class="panel">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:10px;">
        <h2 style="margin:0;">Autonomous 4-Executive Startup War Room</h2>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <button class="tab" onclick="selectTab('board')">Open 3-Lens Board Review</button>
          <button class="tab" onclick="downloadReport('WAR_ROOM_DECISION_MEMO.md', lastWarRoomMd)">Download .md</button>
        </div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px;">
        <button class="tab" style="border-color:#f59e0b;color:#fbbf24;" onclick="runWarRoomPreset('pricing_shock')">Scenario: Pricing Shock</button>
        <button class="tab" style="border-color:#f43f5e;color:#fda4af;" onclick="runWarRoomPreset('runway_crunch')">Scenario: Runway Crunch</button>
        <button class="tab" style="border-color:#38bdf8;color:#7dd3fc;" onclick="runWarRoomPreset('pivot_audit')">Scenario: Pivot Audit</button>
      </div>
      <div style="display:flex;gap:8px;margin-bottom:14px;">
        <input id="wr-question" class="box" style="margin:0;" placeholder="Ask a hard strategic question or pick a scenario preset above..." />
        <button class="tab active" style="white-space:nowrap;" onclick="runWarRoom()">Convene War Room</button>
      </div>
      <div id="wr-results" style="color:var(--muted);">Convene Lean CTO, Fractional CFO, PMF Truth Auditor, and Exponential Growth Strategist on live workspace telemetry.</div>
    </div>

    <div id="x402-panel" class="panel">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px;">
        <h2 style="margin:0;">Live Metered x402 (HTTP 402) Agent Storefront</h2>
        <div style="display:flex;gap:8px;">
          <button class="tab" onclick="testUnpaid402()">Test Unpaid (Expect HTTP 402)</button>
          <button class="tab active" onclick="simulatePaidAgent()">Simulate Paid Agent Call (+$0.05 USDC)</button>
        </div>
      </div>
      <div id="x402-results" style="color:var(--muted);">Loading x402 Base Sepolia ledger...</div>
    </div>

    <div id="board-panel" class="panel">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
        <h2 style="margin:0;">3-Lens Partner &amp; Mentor Board Review</h2>
        <div style="display:flex;gap:8px;">
          <button class="tab" onclick="selectTab('warroom')">Open War Room</button>
          <button class="tab" onclick="downloadReport('BOARD_REVIEW_MEMO.md', lastBoardMd)">Download .md</button>
          <button class="tab active" onclick="loadBoardReview()">Re-Run Audit</button>
        </div>
      </div>
      <div id="board-content" style="margin-top:14px;color:var(--muted);">Loading live audit...</div>
    </div>

    <div id="portfolio-panel" class="panel">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px;">
        <h2 style="margin:0;">Mentor &amp; Accelerator Cohort Portfolio</h2>
        <button class="tab active" onclick="loadPortfolio(true)">Scan Cohort Folder</button>
      </div>
      <div style="display:flex;gap:8px;margin-bottom:14px;">
        <input id="pf-dir" class="box" style="margin:0;" placeholder="Parent directory containing startup workspaces (leave blank to auto-scan parent folder)..." onkeydown="if(event.key==='Enter')loadPortfolio(true)" />
      </div>
      <div id="pf-kpis" class="grid" style="margin-bottom:14px;"></div>
      <div id="pf-table" style="color:var(--muted);">Loading Cohort Portfolio...</div>
    </div>

    <div id="resources-panel" class="panel">
      <input id="res-search" class="search-bar" placeholder="Search 54+ founder resources (singularity, 6ds, x402, pmf, mom test, startup grind, ai)..." oninput="renderResources()" />
      <div id="res-grid" class="grid"></div>
    </div>

    <div id="rhythm-panel" class="panel">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px;">
        <h2 style="margin:0;">Weekly Founder Rhythm (Monday Focus &amp; Friday Digest)</h2>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <button class="tab active" onclick="runRhythm('monday_focus')">Monday Top-3 Focus</button>
          <button class="tab active" style="background:#f59e0b;border-color:#f59e0b;" onclick="runRhythm('friday_digest')">Friday Mentor Digest</button>
          <button class="tab" onclick="copyRhythm()">Copy Text</button>
          <button class="tab" onclick="downloadReport(lastRhythmFile, lastRhythmMd)">Download .md</button>
        </div>
      </div>
      <pre id="rhythm-out" style="background:var(--nav);border:1px solid var(--border);border-radius:12px;padding:18px;white-space:pre-wrap;color:#e2e8f0;font-size:13px;line-height:1.55;">Click 'Monday Top-3 Focus' or 'Friday Mentor Digest' to generate your weekly report from live .startup/ telemetry.</pre>
    </div>

    <div id="editor-panel" class="panel">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:14px;">
        <h2 style="margin:0;">Visual Pitch Deck Slide Editor (Zero JSON)</h2>
        <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
          <select id="ed-theme" class="lang" aria-label="Deck Theme" onchange="switchDeckTheme(this.value)">
            <option value="midnight">Theme: Midnight</option>
            <option value="ivory">Theme: Ivory</option>
            <option value="emerald">Theme: Emerald</option>
            <option value="crimson">Theme: Crimson</option>
            <option value="obsidian-gold">Theme: Obsidian Gold</option>
            <option value="midnight-emerald">Theme: Midnight Emerald</option>
            <option value="editorial-light">Theme: Editorial Light</option>
            <option value="cobalt-velocity">Theme: Cobalt Velocity</option>
          </select>
          <span id="ed-score" class="pill">FI Score: —</span>
          <span id="ed-status" style="font-size:12px;color:var(--muted);"></span>
          <button class="tab" onclick="addEditorSlide()">+ Add Slide</button>
          <button class="tab" onclick="selectTab('deck')">View Live Deck</button>
          <button class="tab active" onclick="saveDeckEdits()">Save &amp; Recompile Deck</button>
        </div>
      </div>
      <div id="ed-slides" style="display:grid;gap:12px;"></div>
    </div>
  </main>

  <div id="onboard-modal" class="modal-bg" onclick="if(event.target===this)closeOnboardModal()">
    <div class="modal">
      <h3 style="margin:0;">90-Second Zero-JSON Startup Wizard</h3>
      <label>Company Name<input id="ob-name" placeholder="e.g. ClaimPulse" oninput="updateOnboardPreview()" /></label>
      <label>Defined Offering<input id="ob-offer" placeholder="e.g. automated pre-submission claim scrubbing software" oninput="updateOnboardPreview()" /></label>
      <label>Specific Target Audience<input id="ob-aud" placeholder="e.g. independent multi-chair dental practices" oninput="updateOnboardPreview()" /></label>
      <label>Specific Problem Solved<input id="ob-prob" placeholder="e.g. cut insurance claim denials below 3%" oninput="updateOnboardPreview()" /></label>
      <label>Secret Sauce<input id="ob-sauce" placeholder="e.g. payer-specific CDT rule checks" oninput="updateOnboardPreview()" /></label>
      <div id="ob-preview" class="takeaway" style="border:1px solid var(--border);font-size:12px;">
        <strong>Live FI One-Sentence Pitch Preview:</strong> Fill the 5 fields above to preview and buzzword-lint live.
      </div>
      <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:6px;">
        <button class="tab" onclick="closeOnboardModal()">Cancel</button>
        <button class="tab active" onclick="submitOnboard()">Generate My Startup OS</button>
      </div>
    </div>
  </div>

  <div id="metrics-modal" class="modal-bg" onclick="if(event.target===this)closeMetricsModal()">
    <div class="modal">
      <h3 style="margin:0;">Update Live Startup Metrics</h3>
      <label>FI Stage
        <select id="m-stage">
          <option value="idea">idea</option><option value="validation">validation</option>
          <option value="mvp">mvp</option><option value="pre_seed_traction">pre_seed_traction</option>
          <option value="seed_scale">seed_scale</option>
        </select>
      </label>
      <label>MRR (USD)<input id="m-mrr" type="number" step="100" placeholder="14400" /></label>
      <label>Gross Margin (%)<input id="m-gm" type="number" step="1" placeholder="84" /></label>
      <label>Cash on Hand (USD)<input id="m-cash" type="number" step="1000" placeholder="215000" /></label>
      <label>Monthly Burn (USD)<input id="m-burn" type="number" step="500" placeholder="14800" /></label>
      <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:6px;">
        <button class="tab" onclick="closeMetricsModal()">Cancel</button>
        <button class="tab active" onclick="saveMetrics()">Save &amp; Rebuild</button>
      </div>
    </div>
  </div>

  <script>
    const I18N = {locales_json};
    const ROUTES = {{
      dashboard: '/workspace/dashboard/index.html',
      deck: '/workspace/pitch-deck/index.html',
      dataroom: '/workspace/data-room/index.html',
      landing: '/workspace/landing/index.html',
    }};
    let currentTab = 'dashboard';
    let allResources = [];
    let lastFp = null;
    let recognition = null, vcStart = null, vcElapsedSec = null, vcTimerId = null;
    let lastVoiceMd = '', lastWarRoomMd = '', lastBoardMd = '';
    const THEME_PALETTE_KEYS = ['bg', 'surface', 'text', 'muted', 'accent', 'accent2', 'border'];
    const SPEECH_LOCALES = {{
      en: 'en-US', es: 'es-ES', zh: 'zh-CN', hi: 'hi-IN', ar: 'ar-SA',
      pt: 'pt-BR', fr: 'fr-FR', de: 'de-DE', ja: 'ja-JP', ko: 'ko-KR'
    }};

    function escHtml(v) {{
      return String(v === null || v === undefined ? '' : v)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }}

    function downloadReport(filename, content) {{
      if (!content) {{ alert('Run the report first before downloading.'); return; }}
      const blob = new Blob([content], {{ type: 'text/markdown;charset=utf-8' }});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = filename; a.click();
    }}

    function applyStudioLang(code) {{
      const L = I18N[code] || I18N.en;
      if (!L) return;
      document.documentElement.lang = code;
      document.documentElement.dir = L.rtl ? 'rtl' : 'ltr';
      const brand = document.getElementById('studio-brand');
      if (brand && L.studioTitle) brand.textContent = L.studioTitle;
      document.querySelectorAll('[data-i18n]').forEach(el => {{
        const parts = el.dataset.i18n.split('.');
        let cur = L;
        for (const p of parts) cur = cur && cur[p];
        if (typeof cur === 'string') el.textContent = cur;
      }});
      try {{ localStorage.setItem('sa_lang', code); }} catch (e) {{}}
    }}

    function selectTab(tab) {{
      currentTab = tab;
      document.querySelectorAll('button.tab[data-tab]').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
      document.getElementById('viewport').style.display = 'none';
      document.querySelectorAll('.panel').forEach(p => p.style.display = 'none');
      if (ROUTES[tab]) {{
        const f = document.getElementById('viewport');
        f.style.display = 'block';
        f.src = ROUTES[tab] + '?t=' + Date.now();
      }} else {{
        const p = document.getElementById(tab + '-panel');
        if (p) p.style.display = 'block';
        if (tab === 'resources' && !allResources.length) loadResources();
        if (tab === 'board') loadBoardReview();
        if (tab === 'x402') loadX402();
        if (tab === 'editor') loadDeckEditor();
        if (tab === 'portfolio') loadPortfolio(false);
      }}
    }}

    let currentDeckObj = null;
    function renderDeckEditor() {{
      if (!currentDeckObj) return;
      document.getElementById('ed-slides').innerHTML = (currentDeckObj.slides || []).map((s, i) => {{
        const bulletsHtml = Array.isArray(s.bullets) ? s.bullets.map((b, bi) => {{
          const txt = typeof b === 'string' ? b : ((b.label ? b.label + ': ' : '') + (b.text || ''));
          return `<div style="display:flex;gap:6px;align-items:center;"><input class="box" style="margin:0;font-size:12px;flex:1;" value="${{escHtml(txt)}}" onchange="updateSlideBullet(${{i}}, ${{bi}}, this.value)" /><button class="tab" style="padding:3px 8px;font-size:11px;border-color:#7f1d1d;color:#fca5a5;" onclick="removeSlideBullet(${{i}}, ${{bi}})" title="Remove bullet">×</button></div>`;
        }}).join('') : '';
        return `
          <div class="card">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;">
              <div class="cat">Slide ${{i+1}} • ${{escHtml(s.type || 'bullets')}} • ${{escHtml(s.kicker || '')}}</div>
              <div style="display:flex;gap:4px;">
                <button class="tab" style="padding:2px 7px;font-size:11px;" onclick="addSlideBullet(${{i}})" title="Add Bullet">+ Bullet</button>
                <button class="tab" style="padding:2px 7px;font-size:11px;" onclick="moveEditorSlide(${{i}}, -1)" title="Move Up">↑</button>
                <button class="tab" style="padding:2px 7px;font-size:11px;" onclick="moveEditorSlide(${{i}}, 1)" title="Move Down">↓</button>
                <button class="tab" style="padding:2px 8px;font-size:11px;border-color:#7f1d1d;color:#fca5a5;" onclick="removeEditorSlide(${{i}})">Remove</button>
              </div>
            </div>
            <input class="box" style="margin:0;" value="${{escHtml(s.headline || '')}}" onchange="currentDeckObj.slides[${{i}}].headline = this.value" />
            ${{bulletsHtml}}
            <textarea class="box" rows="2" style="margin:0;" placeholder="Speaker notes..." onchange="currentDeckObj.slides[${{i}}].notes = this.value">${{escHtml(s.notes || '')}}</textarea>
          </div>`;
      }}).join('');
    }}

    function updateSlideBullet(si, bi, val) {{
      const s = currentDeckObj.slides[si];
      if (!s || !Array.isArray(s.bullets)) return;
      if (typeof s.bullets[bi] === 'object' && s.bullets[bi] !== null) {{
        const idx = val.indexOf(':');
        if (idx > 0 && idx < 32) {{ s.bullets[bi].label = val.slice(0, idx).trim(); s.bullets[bi].text = val.slice(idx + 1).trim(); }}
        else {{ s.bullets[bi].text = val; }}
      }} else {{ s.bullets[bi] = val; }}
    }}

    function addSlideBullet(si) {{
      const s = currentDeckObj && currentDeckObj.slides && currentDeckObj.slides[si];
      if (!s) return;
      if (!Array.isArray(s.bullets)) s.bullets = [];
      s.bullets.push({{ label: 'Proof', text: 'Add concise verified evidence [HYPOTHESIS]' }});
      renderDeckEditor();
    }}

    function removeSlideBullet(si, bi) {{
      const s = currentDeckObj && currentDeckObj.slides && currentDeckObj.slides[si];
      if (!s || !Array.isArray(s.bullets)) return;
      s.bullets.splice(bi, 1);
      renderDeckEditor();
    }}

    function addEditorSlide() {{
      if (!currentDeckObj) return;
      if (!Array.isArray(currentDeckObj.slides)) currentDeckObj.slides = [];
      const n = currentDeckObj.slides.length + 1;
      currentDeckObj.slides.push({{
        id: 'slide-' + n, type: 'bullets', kicker: String(n).padStart(2, '0') + ' / NEW SLIDE',
        headline: 'Concise 10-Word Takeaway Headline [HYPOTHESIS]',
        bullets: [{{ label: 'Key Point', text: 'Add verified proof or customer quote [HYPOTHESIS]' }}],
        notes: '15 seconds. Deliver the core takeaway cleanly.'
      }});
      renderDeckEditor();
    }}

    function removeEditorSlide(idx) {{
      if (!currentDeckObj || (currentDeckObj.slides || []).length <= 1) return;
      currentDeckObj.slides.splice(idx, 1);
      renderDeckEditor();
    }}

    function moveEditorSlide(idx, delta) {{
      if (!currentDeckObj || !Array.isArray(currentDeckObj.slides)) return;
      const target = idx + delta;
      if (target < 0 || target >= currentDeckObj.slides.length) return;
      const tmp = currentDeckObj.slides[idx];
      currentDeckObj.slides[idx] = currentDeckObj.slides[target];
      currentDeckObj.slides[target] = tmp;
      renderDeckEditor();
    }}

    function _applyThemePresetToDeck(preset) {{
      if (!currentDeckObj) return;
      const prevPreset = currentDeckObj.theme && currentDeckObj.theme.preset;
      currentDeckObj.theme = currentDeckObj.theme || {{}};
      if (prevPreset !== preset) {{
        for (const k of THEME_PALETTE_KEYS) delete currentDeckObj.theme[k];
      }}
      currentDeckObj.theme.preset = preset;
    }}

    async function switchDeckTheme(preset) {{
      if (!currentDeckObj) return;
      _applyThemePresetToDeck(preset);
      const st = document.getElementById('ed-status');
      if (st) st.textContent = 'Applying ' + preset + '...';
      const r = await fetch('/api/deck', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{deck: currentDeckObj}}) }});
      const d = await r.json();
      if (d.ok) {{
        document.getElementById('ed-score').textContent = 'FI Score: ' + d.lint.readinessScore + '/100';
        if (st) st.textContent = 'Theme live: ' + preset;
      }} else if (st) {{
        st.textContent = 'Error: ' + (d.error || 'Theme update failed');
      }}
    }}

    let lastRhythmMd = '', lastRhythmFile = 'MONDAY_FOCUS.md';
    async function runRhythm(action) {{
      const r = await fetch('/api/weekly-rhythm', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{action}}) }});
      const d = await r.json();
      if (!d.ok) {{ document.getElementById('rhythm-out').textContent = 'Error: ' + (d.error || 'failed'); return; }}
      lastRhythmMd = d.markdown || '';
      lastRhythmFile = action === 'friday_digest' ? 'FRIDAY_DIGEST.md' : 'MONDAY_FOCUS.md';
      document.getElementById('rhythm-out').textContent = lastRhythmMd;
    }}

    async function copyRhythm() {{
      if (!lastRhythmMd) {{ alert('Generate Monday Focus or Friday Digest first.'); return; }}
      try {{ await navigator.clipboard.writeText(lastRhythmMd); alert('Copied to clipboard!'); }} catch (e) {{}}
    }}

    async function exportSnapshot() {{
      const r = await fetch('/api/export-snapshot');
      const d = await r.json();
      const blob = new Blob([JSON.stringify(d, null, 2)], {{ type: 'application/json' }});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob); a.download = 'startup-antigravity-snapshot.json'; a.click();
    }}

    function triggerImportSnapshot() {{
      const inp = document.getElementById('import-snap-file');
      if (inp) {{ inp.value = ''; inp.click(); }}
    }}

    async function importSnapshotFile(input) {{
      const file = input && input.files && input.files[0];
      if (!file) return;
      try {{
        const text = await file.text();
        const payload = JSON.parse(text);
        const r = await fetch('/api/import-snapshot', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(payload) }});
        const d = await r.json();
        if (!d.ok) {{ alert('Snapshot import rejected: ' + (d.error || 'Invalid schema')); return; }}
        alert('Workspace restored (' + (d.restoredStartupFiles || []).length + ' state files' + (d.deckRestored ? ' + pitch deck' : '') + ').\\nPre-restore backup saved to:\\n' + d.backupPath);
        location.reload();
      }} catch (e) {{
        alert('Could not import snapshot: ' + e.message);
      }}
    }}

    async function loadDeckEditor() {{
      const r = await fetch('/api/deck');
      const d = await r.json();
      if (!d.ok) {{ document.getElementById('ed-slides').innerHTML = '<p>No pitch-deck/deck.json yet — click Setup Wizard first.</p>'; return; }}
      currentDeckObj = d.deck;
      document.getElementById('ed-score').textContent = 'FI Score: ' + d.lint.readinessScore + '/100';
      const sel = document.getElementById('ed-theme');
      if (currentDeckObj.theme && currentDeckObj.theme.preset && Array.from(sel.options).some(o => o.value === currentDeckObj.theme.preset)) {{
        sel.value = currentDeckObj.theme.preset;
      }}
      renderDeckEditor();
    }}

    const FI_BANNED = ['revolutionary','disruptive','world-class','game-changing','synergy','unprecedented','best-in-class'];
    const VOICE_FILLERS = ['um','uh','like','you know','basically','actually','literally','sort of','kind of','so yeah'];
    function updateOnboardPreview() {{
      const c = document.getElementById('ob-name').value.trim() || '[Company]';
      const o = document.getElementById('ob-offer').value.trim() || '[defined offering]';
      const a = document.getElementById('ob-aud').value.trim() || '[target audience]';
      const p = document.getElementById('ob-prob').value.trim() || '[solve specific problem]';
      const s = document.getElementById('ob-sauce').value.trim() || '[secret sauce]';
      const sentence = `My company, ${{c}}, is developing ${{o}} to help ${{a}} ${{p}} with ${{s}}.`;
      const found = FI_BANNED.filter(b => new RegExp('\\\\b' + b + '\\\\b', 'i').test(sentence));
      const box = document.getElementById('ob-preview');
      if (found.length) {{
        box.style.borderColor = '#f59e0b';
        box.innerHTML = `<strong style="color:#fbbf24;">Buzzword Warning (${{escHtml(found.join(', '))}}):</strong> ${{escHtml(sentence)}}`;
      }} else {{
        box.style.borderColor = '#10b981';
        box.innerHTML = `<strong style="color:#34d399;">FI Pitch Lint Clean:</strong> ${{escHtml(sentence)}}`;
      }}
    }}

    async function saveDeckEdits() {{
      if (!currentDeckObj) return;
      _applyThemePresetToDeck(document.getElementById('ed-theme').value);
      const r = await fetch('/api/deck', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{deck: currentDeckObj}}) }});
      const d = await r.json();
      if (d.ok) {{
        document.getElementById('ed-score').textContent = 'FI Score: ' + d.lint.readinessScore + '/100';
        const st = document.getElementById('ed-status');
        if (st) st.textContent = 'Saved & recompiled';
        alert('Pitch deck recompiled!');
      }} else {{
        alert('Could not save deck: ' + (d.error || 'Unknown error'));
      }}
    }}

    function openOnboardModal() {{ document.getElementById('onboard-modal').style.display = 'flex'; }}
    function closeOnboardModal() {{ document.getElementById('onboard-modal').style.display = 'none'; }}

    async function submitOnboard() {{
      const payload = {{
        companyName: document.getElementById('ob-name').value.trim(),
        offering: document.getElementById('ob-offer').value.trim(),
        audience: document.getElementById('ob-aud').value.trim(),
        problem: document.getElementById('ob-prob').value.trim(),
        secretSauce: document.getElementById('ob-sauce').value.trim(),
      }};
      const r = await fetch('/api/onboard', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(payload) }});
      const d = await r.json();
      if (d.ok) {{ closeOnboardModal(); location.reload(); }} else {{ alert(d.error || 'Onboarding failed'); }}
    }}

    async function publishLive() {{
      const r = await fetch('/api/publish', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{include_data_room: false}}) }});
      const d = await r.json();
      if (d.ok) alert('Static deploy bundle ready in:\\n' + d.publishDir + '\\n\\nDrag-and-drop publish/ onto Netlify Drop or run: npx wrangler pages deploy publish');
    }}

    function updateLiveVoiceTelemetry() {{
      const txt = (document.getElementById('vc-transcript').value || '').trim();
      const words = txt ? txt.split(/\\s+/).filter(Boolean).length : 0;
      const elapsedSec = vcStart
        ? Math.max(1, Math.round((Date.now() - vcStart) / 1000))
        : (vcElapsedSec !== null ? Math.max(1, vcElapsedSec) : Math.max(1, Math.round(words / 2.4)));
      const wpm = words ? Math.round((words / elapsedSec) * 60) : 0;
      const wpmEl = document.getElementById('vc-live-wpm');
      if (wpmEl) {{
        wpmEl.textContent = wpm + ' WPM';
        wpmEl.style.color = (wpm >= 125 && wpm <= 165) ? 'var(--accent)' : (wpm === 0 ? 'var(--muted)' : 'var(--amber)');
      }}
      const wEl = document.getElementById('vc-live-words');
      if (wEl) wEl.textContent = words + ' words • ' + (vcStart ? elapsedSec + 's live' : (vcElapsedSec !== null ? elapsedSec + 's recorded' : 'est. ' + elapsedSec + 's'));

      let fillerTotal = 0;
      const fillerHits = [];
      for (const f of VOICE_FILLERS) {{
        const m = txt.match(new RegExp('\\\\b' + f.replace(/ /g, '\\\\s+') + '\\\\b', 'gi'));
        if (m && m.length) {{ fillerTotal += m.length; fillerHits.push(f + '×' + m.length); }}
      }}
      const fEl = document.getElementById('vc-live-fillers');
      if (fEl) fEl.textContent = String(fillerTotal);
      const flEl = document.getElementById('vc-live-filler-list');
      if (flEl) flEl.textContent = fillerHits.length ? fillerHits.join(', ') : 'Clean — zero filler words detected';

      const buzzHits = FI_BANNED.filter(b => new RegExp('\\\\b' + b + '\\\\b', 'i').test(txt));
      const bEl = document.getElementById('vc-live-buzz');
      if (bEl) bEl.textContent = String(buzzHits.length);
      const blEl = document.getElementById('vc-live-buzz-list');
      if (blEl) blEl.textContent = buzzHits.length ? buzzHits.join(', ') : 'Clean — zero empty superlatives';
    }}

    function _stopVoiceMic(shouldScore, statusText) {{
      if (vcStart) {{
        vcElapsedSec = Math.max(1, Math.round((Date.now() - vcStart) / 1000));
        vcStart = null;
      }}
      if (vcTimerId) {{ clearInterval(vcTimerId); vcTimerId = null; }}
      if (recognition) {{
        const activeRec = recognition;
        recognition = null;
        try {{ activeRec.stop(); }} catch (e) {{}}
      }}
      const btn = document.getElementById('vc-mic-btn');
      if (btn) btn.textContent = 'Start 3-Min Mic Pitch';
      const st = document.getElementById('vc-status');
      if (st) {{
        st.textContent = statusText || (shouldScore ? 'SCORING' : 'READY');
        st.style.background = shouldScore ? '#064e3b' : '#1e293b';
        st.style.color = shouldScore ? '#6ee7b7' : '#94a3b8';
      }}
      updateLiveVoiceTelemetry();
      if (shouldScore) scoreVoicePitch();
    }}

    function resetVoiceRehearsal() {{
      _stopVoiceMic(false, 'READY');
      vcElapsedSec = null;
      document.getElementById('vc-transcript').value = '';
      const tEl = document.getElementById('vc-timer');
      if (tEl) {{ tEl.textContent = '03:00'; tEl.style.background = '#064e3b'; }}
      updateLiveVoiceTelemetry();
    }}

    function toggleVoiceMic() {{
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      const btn = document.getElementById('vc-mic-btn');
      const st = document.getElementById('vc-status');
      if (!SR) {{ alert('Web Speech API not supported in this browser — paste your transcript and click Analyze Transcript.'); return; }}
      if (recognition) {{
        _stopVoiceMic(true, 'SCORING');
        return;
      }}
      const rec = new SR();
      rec.continuous = true;
      rec.interimResults = true;
      const langCode = document.getElementById('studio-lang').value || 'en';
      rec.lang = SPEECH_LOCALES[langCode] || langCode || 'en-US';
      recognition = rec;
      vcStart = Date.now();
      vcElapsedSec = null;
      btn.textContent = 'Stop & Score Pitch';
      if (st) {{ st.textContent = 'LIVE REC'; st.style.background = '#7f1d1d'; st.style.color = '#fecaca'; }}
      vcTimerId = setInterval(() => {{
        if (!vcStart) return;
        const rem = Math.max(0, 180 - Math.floor((Date.now() - vcStart) / 1000));
        const tEl = document.getElementById('vc-timer');
        tEl.textContent = String(Math.floor(rem/60)).padStart(2,'0') + ':' + String(rem%60).padStart(2,'0');
        tEl.style.background = rem <= 15 ? '#7f1d1d' : (rem <= 30 ? '#78350f' : '#064e3b');
        updateLiveVoiceTelemetry();
        if (rem === 0) _stopVoiceMic(true, 'TIME UP');
      }}, 500);
      rec.onresult = (ev) => {{
        let txt = ''; for (let i = 0; i < ev.results.length; i++) txt += ev.results[i][0].transcript + ' ';
        document.getElementById('vc-transcript').value = txt.trim();
        updateLiveVoiceTelemetry();
      }};
      rec.onerror = (ev) => {{
        _stopVoiceMic(false, 'MIC ERROR: ' + (ev && ev.error ? ev.error : 'unavailable'));
      }};
      rec.onend = () => {{
        if (recognition === rec) _stopVoiceMic(false, 'STOPPED');
      }};
      rec.start();
    }}

    async function scoreVoicePitch() {{
      const transcript = document.getElementById('vc-transcript').value.trim();
      if (!transcript) return;
      updateLiveVoiceTelemetry();
      const dur = vcStart
        ? Math.max(10, (Date.now() - vcStart) / 1000)
        : (vcElapsedSec !== null ? Math.max(10, vcElapsedSec) : 150);
      const r = await fetch('/api/voice-coach', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{transcript, duration_seconds: dur}}) }});
      const d = await r.json();
      if (!d.ok) {{ document.getElementById('vc-results').innerHTML = '<div class="card"><p style="color:#fca5a5;">' + escHtml(d.error || 'Voice scoring failed') + '</p></div>'; return; }}
      lastVoiceMd = `# Voice Pitch Coach Scorecard\\n\\n- **Clarity Score:** ${{d.clarityScore}}/100 (${{d.verdict}})\\n- **Pace:** ${{d.wordsPerMinute}} WPM (${{d.wordCount}} words)\\n- **Fillers:** ${{d.totalFillers}} • **Buzzwords:** ${{(d.buzzwordsFound || []).join(', ') || 'None'}}\\n\\n## Feedback\\n` + (d.coachingFeedback || []).map(f => '- ' + f).join('\\n');
      document.getElementById('vc-results').innerHTML = `
        <div class="grid" style="margin-bottom:14px;">
          <div class="card"><div class="cat">Clarity Score</div><div class="score-val">${{escHtml(d.clarityScore)}} / 100</div><div>${{escHtml(d.verdict)}}</div></div>
          <div class="card"><div class="cat">Pace (WPM)</div><div class="score-val">${{escHtml(d.wordsPerMinute)}}</div><div>${{escHtml(d.wordCount)}} words</div></div>
          <div class="card"><div class="cat">Fillers &amp; Buzzwords</div><div class="score-val">${{escHtml((d.totalFillers || 0) + (d.buzzwordsFound || []).length)}}</div><div>Fillers: ${{escHtml(d.totalFillers)}} • Buzz: ${{escHtml((d.buzzwordsFound || []).length)}}</div></div>
        </div>
        <div class="card" style="margin-bottom:14px;"><div class="cat">Coaching Feedback</div>${{(d.coachingFeedback || []).map(f => '<p>• ' + escHtml(f) + '</p>').join('')}}</div>
        <div class="grid">${{(d.partnerGrillingQuestions || []).map(q => '<div class="card"><div class="cat">' + escHtml(q.role) + ' Q&amp;A</div><p style="color:#e2e8f0;">' + escHtml(q.question) + '</p></div>').join('')}}</div>`;
    }}

    const WAR_ROOM_PRESETS = {{
      pricing_shock: 'Pricing Shock: Should we raise ACV by 35% to protect >=80% gross margin, or respond to a competitor undercutting us by 30%?',
      runway_crunch: 'Runway Crunch: Cash runway drops below 9 months — should we trim 25% burn, push annual-prepay Customer PACTs, or raise a bridge SAFE?',
      pivot_audit: 'Pivot Audit: Should we narrow strictly to our highest-PMF HXC niche segment or pivot toward an adjacent ICP?'
    }};

    function runWarRoomPreset(key) {{
      const prompt = WAR_ROOM_PRESETS[key];
      if (!prompt) return;
      document.getElementById('wr-question').value = prompt;
      runWarRoom();
    }}

    async function runWarRoom() {{
      const q = document.getElementById('wr-question').value.trim();
      if (!q) return;
      const box = document.getElementById('wr-results');
      box.innerHTML = 'Convening 4 executive lenses...';
      const r = await fetch('/api/war-room', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{question:q}}) }});
      const d = await r.json();
      if (!d.ok) {{
        box.innerHTML = '<div class="card"><p style="color:#fca5a5;">' + escHtml(d.error || 'War Room failed') + '</p></div>';
        return;
      }}
      lastWarRoomMd = `# Startup War Room Decision Memo\\n\\n- **Question:** ${{d.question}}\\n- **Decision:** ${{d.decision}}\\n\\n` + (d.perspectives||[]).map(p => `## ${{p.role}} (${{p.stance}})\\n${{p.argument}}\\n`).join('\\n');
      box.innerHTML = `
        <div class="card" style="margin-bottom:14px;"><div class="cat">Unified Decision</div><div class="score-val" style="font-size:20px;">${{escHtml(d.decision)}}</div><p>Saved to docs/WAR_ROOM_DECISION_MEMO.md</p></div>
        <div class="grid" style="margin-bottom:14px;">${{(d.perspectives || []).map(p => '<div class="card"><div class="cat">' + escHtml(p.role) + ' • ' + escHtml(p.stance) + '</div><p style="color:#e2e8f0;">' + escHtml(p.argument) + '</p></div>').join('')}}</div>
        <div class="card"><div class="cat">Immediate 7-Day Action Plan</div><ol style="margin:4px 0 0 18px;padding:0;color:#e2e8f0;">${{(d.nextSteps || []).map(s => '<li>' + escHtml(s) + '</li>').join('')}}</ol></div>`;
    }}

    async function loadPortfolio(useInput) {{
      const inp = document.getElementById('pf-dir');
      const dir = (useInput && inp && inp.value.trim()) ? ('?dir=' + encodeURIComponent(inp.value.trim())) : '';
      const r = await fetch('/api/portfolio' + dir);
      const d = await r.json();
      if (!d.ok) {{
        document.getElementById('pf-kpis').innerHTML = '';
        document.getElementById('pf-table').innerHTML = '<div class="card"><p style="color:#fca5a5;">' + escHtml(d.error || 'Could not scan portfolio folder') + '</p></div>';
        return;
      }}
      if (inp && !inp.value.trim()) inp.value = d.portfolioDir || '';
      document.getElementById('pf-kpis').innerHTML = `
        <div class="card"><div class="cat">Tracked Startups</div><div class="score-val">${{escHtml(d.startupCount)}}</div><p>${{escHtml(d.portfolioDir)}}</p></div>
        <div class="card"><div class="cat">Combined Cohort MRR</div><div class="score-val">$${{Number(d.totalMrrUsd || 0).toLocaleString()}}</div></div>
        <div class="card"><div class="cat">Avg 3-Lens Board Score</div><div class="score-val">${{escHtml(d.avgBoardScore)}} / 5.0</div></div>`;
      const rows = (d.companies || []).map(c => `
        <tr>
          <td style="padding:10px;border-bottom:1px solid var(--border);"><strong>${{escHtml(c.name)}}</strong></td>
          <td style="padding:10px;border-bottom:1px solid var(--border);"><span class="pill">${{escHtml(c.stage)}}</span></td>
          <td style="padding:10px;border-bottom:1px solid var(--border);">$${{Number(c.mrrUsd || 0).toLocaleString()}}</td>
          <td style="padding:10px;border-bottom:1px solid var(--border);">${{Number(c.grossMarginPct || 0).toFixed(0)}}%</td>
          <td style="padding:10px;border-bottom:1px solid var(--border);">${{c.pmfPct !== null && c.pmfPct !== undefined ? escHtml(c.pmfPct) + '%' : '—'}}</td>
          <td style="padding:10px;border-bottom:1px solid var(--border);"><strong>${{escHtml(c.boardScore)}} / 5.0</strong></td>
          <td style="padding:10px;border-bottom:1px solid var(--border);color:var(--muted);font-size:12px;">${{escHtml(c.topAction)}}</td>
          <td style="padding:10px;border-bottom:1px solid var(--border);"><button class="tab" style="padding:3px 9px;font-size:11px;" data-ws="${{escHtml(c.path || '')}}" onclick="switchWorkspace(this.dataset.ws)">Open</button></td>
        </tr>`).join('');
      document.getElementById('pf-table').innerHTML = `
        <table style="width:100%;border-collapse:collapse;background:var(--nav);border:1px solid var(--border);border-radius:12px;overflow:hidden;font-size:13px;">
          <thead><tr style="background:#111c33;color:var(--muted);text-align:left;">
            <th style="padding:10px;">Startup</th><th style="padding:10px;">Stage</th><th style="padding:10px;">MRR</th><th style="padding:10px;">Margin</th><th style="padding:10px;">PMF</th><th style="padding:10px;">Board</th><th style="padding:10px;">#1 Bottleneck</th><th style="padding:10px;">Studio</th>
          </tr></thead>
          <tbody>${{rows || '<tr><td colspan="8" style="padding:18px;text-align:center;color:var(--muted);">No .startup/state.json workspaces found in this folder.</td></tr>'}}</tbody>
        </table>`;
    }}

    async function switchWorkspace(wsPath) {{
      if (!wsPath) return;
      const r = await fetch('/api/workspace', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{workspace: wsPath}}) }});
      const d = await r.json();
      if (d.ok) location.reload(); else alert(d.error || 'Could not switch workspace');
    }}

    async function loadX402() {{
      const r = await fetch('/api/x402/ledger');
      const d = await r.json();
      document.getElementById('x402-results').innerHTML = `
        <div class="grid" style="margin-bottom:14px;">
          <div class="card"><div class="cat">Network</div><div class="score-val" style="font-size:20px;">${{escHtml(d.network)}}</div></div>
          <div class="card"><div class="cat">Paid Agent Calls</div><div class="score-val">${{escHtml(d.totalCalls)}}</div></div>
          <div class="card"><div class="cat">Total USDC Revenue</div><div class="score-val">$${{Number(d.totalRevenueUsdc).toFixed(2)}}</div></div>
        </div>
        <div class="card"><div class="cat">Recent Metered Agent Calls</div>${{(d.events||[]).slice(-6).reverse().map(e => '<p>' + escHtml(e.timestamp) + ' — <strong>' + escHtml(e.agentId) + '</strong> paid $' + escHtml(e.amountUsdc) + ' USDC on ' + escHtml(e.network) + '</p>').join('') || '<p>No paid calls yet.</p>'}}</div>`;
    }}

    async function testUnpaid402() {{
      const r = await fetch('/api/x402/agent-call', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{query:'test'}}) }});
      alert('HTTP ' + r.status + ' Payment Required!\\nX-PAYMENT-REQUIRED: ' + r.headers.get('X-PAYMENT-REQUIRED'));
    }}

    async function simulatePaidAgent() {{
      await fetch('/api/x402/agent-call', {{ method:'POST', headers:{{'Content-Type':'application/json','X-PAYMENT':'base-sepolia-demo-usdc-proof','X-AGENT-ID':'antigravity-demo-agent'}}, body:JSON.stringify({{query:'claim-scrub'}}) }});
      loadX402();
    }}

    async function loadBoardReview() {{
      const box = document.getElementById('board-content');
      const r = await fetch('/api/board-review');
      const d = await r.json();
      lastBoardMd = `# Board Review Memo\\n\\n- **Overall:** ${{d.overallScore}}/5.0 (${{d.verdict}})\\n- **FI Mentor:** ${{d.scores.fiMentor}} • **VC Lab:** ${{d.scores.vcLabPartner}} • **PMF:** ${{d.scores.pmfTruthAuditor}}\\n\\n## Top 3 Actions\\n` + (d.topActions||[]).map((a,i) => (i+1)+'. '+a).join('\\n');
      box.innerHTML = `
        <div class="grid" style="margin-bottom:14px;">
          <div class="card"><div class="cat">Overall Readiness</div><div class="score-val">${{escHtml(d.overallScore)}} / 5.0</div><div>${{escHtml(d.verdict)}}</div></div>
          <div class="card"><div class="cat">FI Mentor</div><div class="score-val">${{escHtml(d.scores.fiMentor)}} / 5.0</div></div>
          <div class="card"><div class="cat">VC Lab Partner</div><div class="score-val">${{escHtml(d.scores.vcLabPartner)}} / 5.0</div></div>
          <div class="card"><div class="cat">PMF Truth Auditor</div><div class="score-val">${{escHtml(d.scores.pmfTruthAuditor)}} / 5.0</div></div>
        </div>
        <div class="card"><div class="cat">Top 3 Prioritized 7-Day Actions</div><ol style="margin:4px 0 0 18px;padding:0;color:#e2e8f0;">${{(d.topActions||[]).map(a => '<li>' + escHtml(a) + '</li>').join('')}}</ol></div>`;
    }}

    function openMetricsModal() {{ document.getElementById('metrics-modal').style.display = 'flex'; }}
    function closeMetricsModal() {{ document.getElementById('metrics-modal').style.display = 'none'; }}

    async function saveMetrics() {{
      const payload = {{ stage: document.getElementById('m-stage').value }};
      for (const [id, key] of [['m-mrr','mrrUsd'],['m-gm','grossMarginPct'],['m-cash','cashOnHandUsd'],['m-burn','monthlyBurnUsd']]) {{
        const v = document.getElementById(id).value; if (v !== '') payload[key] = Number(v);
      }}
      await fetch('/api/metrics', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(payload) }});
      closeMetricsModal();
      if (ROUTES[currentTab]) document.getElementById('viewport').src = ROUTES[currentTab] + '?t=' + Date.now();
    }}

    async function loadResources() {{
      const r = await fetch('/api/resources');
      const data = await r.json();
      allResources = data.resources || [];
      renderResources();
    }}

    function renderResources() {{
      const q = (document.getElementById('res-search').value || '').toLowerCase().trim();
      const filtered = allResources.filter(item => !q || [item.title, item.category, item.summary, item.keyTakeaway, (item.tags || []).join(' ')].join(' ').toLowerCase().includes(q));
      document.getElementById('res-grid').innerHTML = filtered.map(item => `
        <div class="card"><div class="cat">${{escHtml(item.category)}} • ${{escHtml(item.format)}}</div><a href="${{escHtml(item.url)}}" target="_blank" rel="noopener">${{escHtml(item.title)}}</a><p>${{escHtml(item.summary)}}</p><div class="takeaway"><strong>Takeaway:</strong> ${{escHtml(item.keyTakeaway)}}</div></div>
      `).join('');
    }}

    (function () {{
      let saved = "{html.escape(default_locale)}";
      try {{ saved = localStorage.getItem('sa_lang') || saved; }} catch (e) {{}}
      const sel = document.getElementById('studio-lang');
      if (sel && I18N[saved]) {{ sel.value = saved; applyStudioLang(saved); }}
    }})();

    setInterval(async () => {{
      try {{
        const r = await fetch('/api/health');
        const h = await r.json();
        if (lastFp !== null && h.fingerprint !== lastFp && ROUTES[currentTab]) {{
          document.getElementById('viewport').src = ROUTES[currentTab] + '?t=' + Date.now();
        }}
        lastFp = h.fingerprint;
      }} catch (e) {{}}
    }}, 3000);
  </script>
</body>
</html>
"""


def create_studio_server(
    workspace: Path,
    plugin_root: Path | None = None,
    host: str = "127.0.0.1",
    port: int = 4020,
) -> ThreadingHTTPServer:
    ctx = {"workspace": workspace.resolve()}
    p_root = (plugin_root or ROOT).resolve()
    resources = _load_json(p_root / "mcp_server" / "founder_resources.json", [])

    for sub in (
        Path(__file__).resolve().parent,
        p_root / "skills" / "pitch-deck-builder" / "scripts",
        p_root / "skills" / "weekly-sprint-review" / "scripts",
    ):
        if str(sub) not in sys.path:
            sys.path.insert(0, str(sub))

    from board_review import run_board_review  # noqa: E402
    from build_deck import build_deck, lint_deck  # noqa: E402
    from portfolio import build_portfolio  # noqa: E402
    from voice_pitch_coach import analyze_voice_pitch  # noqa: E402
    from war_room import run_war_room  # noqa: E402
    from weekly_rhythm import build_publish_bundle, run_weekly_rhythm  # noqa: E402
    from x402_storefront import build_402_challenge, load_x402_ledger, record_x402_payment  # noqa: E402

    class StudioHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            return

        def _send_bytes(
            self,
            data: bytes,
            content_type: str,
            status: int = 200,
            extra_headers: dict[str, str] | None = None,
        ) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (extra_headers or {}).items():
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(data)

        def _read_json_body(self) -> Any:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 0:
                raise ValueError("Invalid negative Content-Length.")
            if length > MAX_JSON_BODY_BYTES:
                raise ValueError(f"Request body exceeds maximum size of {MAX_JSON_BODY_BYTES // (1024 * 1024)} MB.")
            raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            return json.loads(raw)

        def do_POST(self) -> None:  # noqa: N802
            ws = ctx["workspace"]
            path = unquote(urlparse(self.path).path)
            try:
                body = self._read_json_body()
            except Exception as exc:
                self._send_bytes(json.dumps({"ok": False, "error": str(exc)}).encode("utf-8"), "application/json", 400)
                return

            if path == "/api/import-snapshot":
                valid, err = validate_snapshot_payload(body)
                if not valid:
                    self._send_bytes(json.dumps({"ok": False, "error": err}).encode("utf-8"), "application/json", 400)
                    return

                # Automatic pre-restore backup
                sdir = ws / ".startup"
                backup_dir = sdir / "backups"
                backup_dir.mkdir(parents=True, exist_ok=True)
                ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                backup_snap = _build_snapshot_dict(ws)
                backup_path = backup_dir / f"pre-restore-{ts}.json"
                backup_path.write_text(json.dumps(backup_snap, indent=2), encoding="utf-8")

                try:
                    # Restore validated .startup/*.json files and remove stale top-level JSON files
                    restored_files: list[str] = []
                    incoming_startup = body.get("startup")
                    if isinstance(incoming_startup, dict) and incoming_startup:
                        incoming_names = set(incoming_startup.keys())
                        for existing_jf in sorted(sdir.glob("*.json")):
                            if existing_jf.name not in incoming_names:
                                existing_jf.unlink()
                        for fname, content in incoming_startup.items():
                            (sdir / fname).write_text(json.dumps(content, indent=2), encoding="utf-8")
                            restored_files.append(fname)

                    # Restore pitch-deck/deck.json & recompile if provided
                    deck_restored = False
                    if isinstance(body.get("deck"), dict):
                        pdir = ws / "pitch-deck"
                        pdir.mkdir(parents=True, exist_ok=True)
                        deck_file = pdir / "deck.json"
                        deck_file.write_text(json.dumps(body["deck"], indent=2), encoding="utf-8")
                        build_deck(deck_file)
                        deck_restored = True

                    _rebuild_views(ws, p_root)
                except Exception as exc:
                    # Roll back workspace from pre-restore backup on failure
                    prev_startup = backup_snap.get("startup") or {}
                    for existing_jf in sorted(sdir.glob("*.json")):
                        if existing_jf.name not in prev_startup:
                            existing_jf.unlink()
                    for fname, content in prev_startup.items():
                        (sdir / fname).write_text(json.dumps(content, indent=2), encoding="utf-8")
                    if isinstance(backup_snap.get("deck"), dict):
                        deck_file = ws / "pitch-deck" / "deck.json"
                        deck_file.parent.mkdir(parents=True, exist_ok=True)
                        deck_file.write_text(json.dumps(backup_snap["deck"], indent=2), encoding="utf-8")
                        try:
                            build_deck(deck_file)
                        except Exception:
                            pass
                    self._send_bytes(
                        json.dumps({"ok": False, "error": f"Snapshot restore failed and was rolled back: {exc}"}).encode("utf-8"),
                        "application/json",
                        400,
                    )
                    return

                self._send_bytes(
                    json.dumps(
                        {
                            "ok": True,
                            "restoredStartupFiles": restored_files,
                            "deckRestored": deck_restored,
                            "backupPath": str(backup_path),
                        }
                    ).encode("utf-8"),
                    "application/json",
                )
                return

            if not isinstance(body, dict):
                self._send_bytes(json.dumps({"ok": False, "error": "JSON object body required"}).encode("utf-8"), "application/json", 400)
                return

            if path == "/api/workspace":
                new_path = Path(str(body.get("workspace", ""))).expanduser().resolve()
                if not new_path.exists() or not new_path.is_dir():
                    self._send_bytes(json.dumps({"ok": False, "error": f"Directory not found: {new_path}"}).encode("utf-8"), "application/json", 400)
                    return
                ctx["workspace"] = new_path
                self._send_bytes(json.dumps({"ok": True, "workspace": str(new_path)}).encode("utf-8"), "application/json")
                return

            if path == "/api/metrics":
                sdir = ws / ".startup"
                sdir.mkdir(parents=True, exist_ok=True)
                state_file = sdir / "state.json"
                state = _load_json(state_file, {})
                if "stage" in body and body["stage"] in ("idea", "validation", "mvp", "pre_seed_traction", "seed_scale"):
                    state["stage"] = body["stage"]
                metrics = state.setdefault("metrics", {})
                for key in ("mrrUsd", "grossMarginPct", "cashOnHandUsd", "monthlyBurnUsd"):
                    if key in body and body[key] is not None:
                        metrics[key] = float(body[key])
                state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
                _rebuild_views(ws, p_root)
                self._send_bytes(json.dumps({"ok": True, "state": state}).encode("utf-8"), "application/json")
                return

            if path == "/api/voice-coach":
                try:
                    res = analyze_voice_pitch(
                        transcript=str(body.get("transcript", "")),
                        duration_seconds=float(body.get("duration_seconds", 180.0)),
                    )
                    self._send_bytes(json.dumps(res).encode("utf-8"), "application/json")
                except Exception as exc:
                    self._send_bytes(json.dumps({"ok": False, "error": str(exc)}).encode("utf-8"), "application/json", 400)
                return

            if path == "/api/war-room":
                try:
                    res = run_war_room(ws, str(body.get("question", "")), write_memo=True)
                    self._send_bytes(json.dumps(res).encode("utf-8"), "application/json")
                except Exception as exc:
                    self._send_bytes(json.dumps({"ok": False, "error": str(exc)}).encode("utf-8"), "application/json", 400)
                return

            if path == "/api/x402/agent-call":
                payment = self.headers.get("X-PAYMENT")
                if not payment:
                    challenge = build_402_challenge(ws)
                    self._send_bytes(
                        json.dumps({"error": "Payment Required", "paymentRequirements": challenge}).encode("utf-8"),
                        "application/json",
                        status=402,
                        extra_headers={"X-PAYMENT-REQUIRED": json.dumps(challenge)},
                    )
                    return
                agent_id = self.headers.get("X-AGENT-ID") or "autonomous-agent"
                rec = record_x402_payment(ws, agent_id=agent_id, payment_proof=payment)
                _rebuild_views(ws, p_root)
                self._send_bytes(json.dumps(rec).encode("utf-8"), "application/json", status=200)
                return

            if path == "/api/publish":
                res = build_publish_bundle(ws, include_data_room=bool(body.get("include_data_room", False)))
                self._send_bytes(json.dumps(res).encode("utf-8"), "application/json")
                return

            if path == "/api/weekly-rhythm":
                try:
                    res = run_weekly_rhythm(ws, action=str(body.get("action", "monday_focus")))
                    res["markdown"] = Path(res["path"]).read_text(encoding="utf-8")
                    self._send_bytes(json.dumps(res).encode("utf-8"), "application/json")
                except Exception as exc:
                    self._send_bytes(json.dumps({"ok": False, "error": str(exc)}).encode("utf-8"), "application/json", 400)
                return

            if path == "/api/deck":
                deck_obj = body.get("deck")
                if not isinstance(deck_obj, dict):
                    self._send_bytes(json.dumps({"ok": False, "error": "'deck' object required"}).encode("utf-8"), "application/json", 400)
                    return
                pdir = ws / "pitch-deck"
                pdir.mkdir(parents=True, exist_ok=True)
                deck_file = pdir / "deck.json"
                # If theme.preset changed from previous deck.json, drop stale palette overrides so the new preset takes effect
                prev_deck = _load_json(deck_file, {})
                prev_preset = (prev_deck.get("theme") or {}).get("preset") if isinstance(prev_deck, dict) else None
                new_theme = deck_obj.get("theme")
                if isinstance(new_theme, dict) and new_theme.get("preset") and new_theme.get("preset") != prev_preset:
                    for key in THEME_PALETTE_KEYS:
                        new_theme.pop(key, None)
                deck_file.write_text(json.dumps(deck_obj, indent=2), encoding="utf-8")
                lint_res = lint_deck(deck_obj)
                build_deck(deck_file)
                _rebuild_views(ws, p_root)
                self._send_bytes(json.dumps({"ok": True, "lint": lint_res}).encode("utf-8"), "application/json")
                return

            if path == "/api/onboard":
                cname = str(body.get("companyName", "")).strip()
                offer = str(body.get("offering", "")).strip()
                aud = str(body.get("audience", "")).strip()
                prob = str(body.get("problem", "")).strip()
                sauce = str(body.get("secretSauce", "")).strip()
                if not cname or not offer or not aud or not prob:
                    self._send_bytes(json.dumps({"ok": False, "error": "Company, offering, audience, and problem are required."}).encode("utf-8"), "application/json", 400)
                    return
                fi_pitch = f"My company, {cname}, is developing {offer} to help {aud} {prob} with {sauce or 'our proprietary workflow'}."
                sdir = ws / ".startup"
                sdir.mkdir(parents=True, exist_ok=True)
                state = _load_json(sdir / "state.json", {})
                state.update({"companyName": cname, "stage": state.get("stage", "validation"), "fiOneSentencePitch": fi_pitch, "oneSentencePitch": fi_pitch, "secretSauce": sauce})
                (sdir / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")
                # Seed starter deck if missing
                deck_file = ws / "pitch-deck" / "deck.json"
                if not deck_file.exists():
                    tpl_path = p_root / "skills" / "pitch-deck-builder" / "resources" / "deck.problem-solution.json"
                    if tpl_path.exists():
                        deck_data = json.loads(tpl_path.read_text(encoding="utf-8"))
                        deck_data.setdefault("meta", {})["companyName"] = cname
                        deck_data["meta"]["fiOneSentencePitch"] = fi_pitch
                        if deck_data.get("slides"):
                            deck_data["slides"][0]["headline"] = f"{cname}: {prob[:55]}"
                            deck_data["slides"][0]["subheadline"] = fi_pitch
                        deck_file.parent.mkdir(parents=True, exist_ok=True)
                        deck_file.write_text(json.dumps(deck_data, indent=2), encoding="utf-8")
                        build_deck(deck_file)
                _rebuild_views(ws, p_root)
                self._send_bytes(json.dumps({"ok": True, "companyName": cname, "fiOneSentencePitch": fi_pitch}).encode("utf-8"), "application/json")
                return

            self._send_bytes(b"Not Found", "text/plain", 404)

        def do_GET(self) -> None:  # noqa: N802
            ws = ctx["workspace"]
            parsed = urlparse(self.path)
            path = unquote(parsed.path)

            if path in ("/", "/index.html"):
                self._send_bytes(render_studio_shell(ws, p_root).encode("utf-8"), "text/html; charset=utf-8")
                return

            if path == "/api/health":
                payload = {"ok": True, "workspace": str(ws), "fingerprint": _workspace_fingerprint(ws), "resourceCount": len(resources)}
                self._send_bytes(json.dumps(payload).encode("utf-8"), "application/json")
                return

            if path == "/api/board-review":
                self._send_bytes(json.dumps(run_board_review(ws, write_memo=True)).encode("utf-8"), "application/json")
                return

            if path == "/api/portfolio":
                qs = parse_qs(parsed.query)
                req_dir = (qs.get("dir") or [""])[0].strip()
                target_dir = Path(req_dir).expanduser().resolve() if req_dir else ws.parent.resolve()
                try:
                    res = build_portfolio(target_dir, write_html=False)
                    self._send_bytes(json.dumps(res).encode("utf-8"), "application/json")
                except Exception as exc:
                    self._send_bytes(json.dumps({"ok": False, "error": str(exc)}).encode("utf-8"), "application/json", 400)
                return

            if path == "/api/x402/ledger":
                self._send_bytes(json.dumps(load_x402_ledger(ws)).encode("utf-8"), "application/json")
                return

            if path == "/api/deck":
                deck_file = ws / "pitch-deck" / "deck.json"
                if not deck_file.exists():
                    self._send_bytes(json.dumps({"ok": False, "error": "No pitch-deck/deck.json found"}).encode("utf-8"), "application/json", 404)
                    return
                deck_obj = json.loads(deck_file.read_text(encoding="utf-8"))
                self._send_bytes(json.dumps({"ok": True, "deck": deck_obj, "lint": lint_deck(deck_obj)}).encode("utf-8"), "application/json")
                return

            if path == "/api/export-snapshot":
                self._send_bytes(json.dumps(_build_snapshot_dict(ws), indent=2).encode("utf-8"), "application/json")
                return

            if path == "/api/resources":
                qs = parse_qs(parsed.query)
                q = (qs.get("q") or [""])[0].strip().lower()
                items = [r for r in resources if not q or q in json.dumps(r).lower()]
                self._send_bytes(json.dumps({"count": len(items), "resources": items}).encode("utf-8"), "application/json")
                return

            if path.startswith("/workspace/"):
                rel = path[len("/workspace/"):].lstrip("/")
                target = (ws / rel).resolve()
                if not target.is_relative_to(ws.resolve()):
                    self._send_bytes(b"Forbidden", "text/plain", 403)
                    return
                if not target.exists() or not target.is_file():
                    msg = (
                        f"<html><body style='background:#0b1120;color:#94a3b8;font-family:sans-serif;padding:40px;'>"
                        f"<h2 style='color:#f8fafc;'>Not built yet: {html.escape(rel)}</h2></body></html>"
                    ).encode("utf-8")
                    self._send_bytes(msg, "text/html; charset=utf-8", 200)
                    return
                ctype, _ = mimetypes.guess_type(str(target))
                self._send_bytes(target.read_bytes(), ctype or "application/octet-stream")
                return

            self._send_bytes(b"Not Found", "text/plain", 404)

    return ThreadingHTTPServer((host, port), StudioHandler)


def serve_studio(
    workspace: Path,
    plugin_root: Path | None = None,
    port: int = 4020,
    open_browser: bool = True,
) -> None:
    server = create_studio_server(workspace, plugin_root=plugin_root, port=port)
    actual_port = server.server_address[1]
    url = f"http://127.0.0.1:{actual_port}/"
    print(f"Startup Antigravity Studio running at {url} (Ctrl+C to stop)", flush=True)
    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
