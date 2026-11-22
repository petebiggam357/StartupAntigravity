#!/usr/bin/env python3
"""Zero-dependency local HTTP Studio server for Startup Antigravity (v0.3.0-beta).

Serves a unified, 10-language tabbed dark-mode web workspace on http://127.0.0.1:<port> combining:
  - Startup Command Center Dashboard  (/workspace/dashboard/index.html)
  - 13-Slide Interactive Pitch Deck   (/workspace/pitch-deck/index.html)
  - Investor Data Room Portal         (/workspace/data-room/index.html)
  - Smoke-Test Landing Page           (/workspace/landing/index.html)
  - Live Voice Pitch Coach & VC Q&A   (POST /api/voice-coach + Web Speech API)
  - Autonomous 4-Exec Startup War Room(POST /api/war-room)
  - Metered x402 Agent Storefront     (POST /api/x402/agent-call & GET /api/x402/ledger)
  - 3-Lens Board Review               (GET /api/board-review)
  - Live 54+ Resource Library Search  (GET /api/resources)
  - Live Metric Editor & Switcher     (POST /api/metrics & POST /api/workspace)
"""

from __future__ import annotations

import html
import json
import mimetypes
import subprocess
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent


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
    locales_json = json.dumps(all_locales, ensure_ascii=False)
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
      <button class="tab" data-tab="resources" data-i18n="nav.resources" onclick="selectTab('resources')">54+ Resources</button>
      <button class="tab" data-i18n="nav.editMetrics" onclick="openMetricsModal()" style="border-color:#f59e0b;color:#fbbf24;">Edit Metrics</button>
      <select id="studio-lang" class="lang" aria-label="Language" onchange="applyStudioLang(this.value)">{lang_opts}</select>
    </nav>
  </header>
  <main>
    <iframe id="viewport" src="/workspace/dashboard/index.html"></iframe>

    <div id="voice-panel" class="panel">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:12px;">
        <h2 style="margin:0;">Live Voice Pitch Coach &amp; VC Lab Partner Q&amp;A</h2>
        <div style="display:flex;gap:8px;align-items:center;">
          <span id="vc-timer" class="pill" style="font-size:14px;padding:6px 12px;">03:00</span>
          <button id="vc-mic-btn" class="tab active" onclick="toggleVoiceMic()">Start 3-Min Mic Pitch</button>
          <button class="tab" onclick="scoreVoicePitch()">Analyze Transcript</button>
          <button class="tab" onclick="downloadReport('voice-coach-scorecard.md', lastVoiceMd)">Download .md</button>
        </div>
      </div>
      <textarea id="vc-transcript" class="box" rows="5" placeholder="Click 'Start 3-Min Mic Pitch' (Web Speech API) or paste your 3-minute FI pitch transcript here..."></textarea>
      <div id="vc-results" style="color:var(--muted);">Speak or paste your pitch to get live WPM pace, filler-word count, FI buzzword check, and 5 Partner grilling questions.</div>
    </div>

    <div id="warroom-panel" class="panel">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:10px;">
        <h2 style="margin:0;">Autonomous 4-Executive Startup War Room</h2>
        <button class="tab" onclick="downloadReport('WAR_ROOM_DECISION_MEMO.md', lastWarRoomMd)">Download .md</button>
      </div>
      <div style="display:flex;gap:8px;margin-bottom:14px;">
        <input id="wr-question" class="box" style="margin:0;" placeholder="Ask a hard strategic question (e.g. Should we raise $750K Pre-Seed now or bootstrap to $30K MRR?)" />
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
          <button class="tab" onclick="downloadReport('BOARD_REVIEW_MEMO.md', lastBoardMd)">Download .md</button>
          <button class="tab active" onclick="loadBoardReview()">Re-Run Audit</button>
        </div>
      </div>
      <div id="board-content" style="margin-top:14px;color:var(--muted);">Loading live audit...</div>
    </div>

    <div id="resources-panel" class="panel">
      <input id="res-search" class="search-bar" placeholder="Search 54+ founder resources (singularity, 6ds, x402, pmf, mom test, startup grind, ai)..." oninput="renderResources()" />
      <div id="res-grid" class="grid"></div>
    </div>
  </main>

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
    let recognition = null, vcStart = null, vcTimerId = null;
    let lastVoiceMd = '', lastWarRoomMd = '', lastBoardMd = '';

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
      }}
    }}

    function toggleVoiceMic() {{
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      const btn = document.getElementById('vc-mic-btn');
      if (!SR) {{ alert('Web Speech API not supported in this browser — paste your transcript and click Analyze Transcript.'); return; }}
      if (recognition) {{
        recognition.stop(); recognition = null; clearInterval(vcTimerId);
        btn.textContent = 'Start 3-Min Mic Pitch'; scoreVoicePitch(); return;
      }}
      recognition = new SR(); recognition.continuous = true; recognition.interimResults = true;
      recognition.lang = document.getElementById('studio-lang').value || 'en-US';
      vcStart = Date.now();
      btn.textContent = 'Stop & Score Pitch';
      vcTimerId = setInterval(() => {{
        const rem = Math.max(0, 180 - Math.floor((Date.now() - vcStart) / 1000));
        document.getElementById('vc-timer').textContent = String(Math.floor(rem/60)).padStart(2,'0') + ':' + String(rem%60).padStart(2,'0');
      }}, 500);
      recognition.onresult = (ev) => {{
        let txt = ''; for (let i = 0; i < ev.results.length; i++) txt += ev.results[i][0].transcript + ' ';
        document.getElementById('vc-transcript').value = txt.trim();
      }};
      recognition.start();
    }}

    async function scoreVoicePitch() {{
      const transcript = document.getElementById('vc-transcript').value.trim();
      if (!transcript) return;
      const dur = vcStart ? Math.max(10, (Date.now() - vcStart) / 1000) : 150;
      const r = await fetch('/api/voice-coach', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{transcript, duration_seconds: dur}}) }});
      const d = await r.json();
      if (!d.ok) {{ document.getElementById('vc-results').innerHTML = d.error; return; }}
      lastVoiceMd = `# Voice Pitch Coach Scorecard\\n\\n- **Clarity Score:** ${{d.clarityScore}}/100 (${{d.verdict}})\\n- **Pace:** ${{d.wordsPerMinute}} WPM (${{d.wordCount}} words)\\n- **Fillers:** ${{d.totalFillers}} • **Buzzwords:** ${{d.buzzwordsFound.join(', ') || 'None'}}\\n\\n## Feedback\\n` + d.coachingFeedback.map(f => '- ' + f).join('\\n');
      document.getElementById('vc-results').innerHTML = `
        <div class="grid" style="margin-bottom:14px;">
          <div class="card"><div class="cat">Clarity Score</div><div class="score-val">${{d.clarityScore}} / 100</div><div>${{d.verdict}}</div></div>
          <div class="card"><div class="cat">Pace (WPM)</div><div class="score-val">${{d.wordsPerMinute}}</div><div>${{d.wordCount}} words</div></div>
          <div class="card"><div class="cat">Fillers &amp; Buzzwords</div><div class="score-val">${{d.totalFillers + d.buzzwordsFound.length}}</div><div>Fillers: ${{d.totalFillers}} • Buzz: ${{d.buzzwordsFound.length}}</div></div>
        </div>
        <div class="card" style="margin-bottom:14px;"><div class="cat">Coaching Feedback</div>${{d.coachingFeedback.map(f => '<p>• '+f+'</p>').join('')}}</div>
        <div class="grid">${{d.partnerGrillingQuestions.map(q => '<div class="card"><div class="cat">'+q.role+' Q&amp;A</div><p style="color:#e2e8f0;">'+q.question+'</p></div>').join('')}}</div>`;
    }}

    async function runWarRoom() {{
      const q = document.getElementById('wr-question').value.trim();
      if (!q) return;
      const box = document.getElementById('wr-results');
      box.innerHTML = 'Convening 4 executive lenses...';
      const r = await fetch('/api/war-room', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{question:q}}) }});
      const d = await r.json();
      lastWarRoomMd = `# Startup War Room Decision Memo\\n\\n- **Question:** ${{d.question}}\\n- **Decision:** ${{d.decision}}\\n\\n` + (d.perspectives||[]).map(p => `## ${{p.role}} (${{p.stance}})\\n${{p.argument}}\\n`).join('\\n');
      box.innerHTML = `
        <div class="card" style="margin-bottom:14px;"><div class="cat">Unified Decision</div><div class="score-val" style="font-size:20px;">${{d.decision}}</div><p>Saved to docs/WAR_ROOM_DECISION_MEMO.md</p></div>
        <div class="grid" style="margin-bottom:14px;">${{d.perspectives.map(p => '<div class="card"><div class="cat">'+p.role+' • '+p.stance+'</div><p style="color:#e2e8f0;">'+p.argument+'</p></div>').join('')}}</div>
        <div class="card"><div class="cat">Immediate 7-Day Action Plan</div><ol style="margin:4px 0 0 18px;padding:0;color:#e2e8f0;">${{d.nextSteps.map(s => '<li>'+s+'</li>').join('')}}</ol></div>`;
    }}

    async function loadX402() {{
      const r = await fetch('/api/x402/ledger');
      const d = await r.json();
      document.getElementById('x402-results').innerHTML = `
        <div class="grid" style="margin-bottom:14px;">
          <div class="card"><div class="cat">Network</div><div class="score-val" style="font-size:20px;">${{d.network}}</div></div>
          <div class="card"><div class="cat">Paid Agent Calls</div><div class="score-val">${{d.totalCalls}}</div></div>
          <div class="card"><div class="cat">Total USDC Revenue</div><div class="score-val">$${{Number(d.totalRevenueUsdc).toFixed(2)}}</div></div>
        </div>
        <div class="card"><div class="cat">Recent Metered Agent Calls</div>${{(d.events||[]).slice(-6).reverse().map(e => '<p>'+e.timestamp+' — <strong>'+e.agentId+'</strong> paid $'+e.amountUsdc+' USDC on '+e.network+'</p>').join('') || '<p>No paid calls yet.</p>'}}</div>`;
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
          <div class="card"><div class="cat">Overall Readiness</div><div class="score-val">${{d.overallScore}} / 5.0</div><div>${{d.verdict}}</div></div>
          <div class="card"><div class="cat">FI Mentor</div><div class="score-val">${{d.scores.fiMentor}} / 5.0</div></div>
          <div class="card"><div class="cat">VC Lab Partner</div><div class="score-val">${{d.scores.vcLabPartner}} / 5.0</div></div>
          <div class="card"><div class="cat">PMF Truth Auditor</div><div class="score-val">${{d.scores.pmfTruthAuditor}} / 5.0</div></div>
        </div>
        <div class="card"><div class="cat">Top 3 Prioritized 7-Day Actions</div><ol style="margin:4px 0 0 18px;padding:0;color:#e2e8f0;">${{(d.topActions||[]).map(a => '<li>'+a+'</li>').join('')}}</ol></div>`;
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
        <div class="card"><div class="cat">${{item.category}} • ${{item.format}}</div><a href="${{item.url}}" target="_blank" rel="noopener">${{item.title}}</a><p>${{item.summary}}</p><div class="takeaway"><strong>Takeaway:</strong> ${{item.keyTakeaway}}</div></div>
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
    from voice_pitch_coach import analyze_voice_pitch  # noqa: E402
    from war_room import run_war_room  # noqa: E402
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

        def _read_json_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
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

            if path == "/api/x402/ledger":
                self._send_bytes(json.dumps(load_x402_ledger(ws)).encode("utf-8"), "application/json")
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
                if not str(target).startswith(str(ws)):
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
