#!/usr/bin/env python3
"""Zero-dependency local HTTP Studio server for Startup Antigravity.

Serves a unified tabbed dark-mode web workspace on http://127.0.0.1:<port> combining:
  - Founder Command Center Dashboard (/workspace/dashboard/index.html)
  - Interactive FI Pitch Deck        (/workspace/pitch-deck/index.html)
  - Investor Data Room Portal        (/workspace/data-room/index.html)
  - Smoke-Test Landing Page          (/workspace/landing/index.html)
  - Live 48-Resource Library Search  (/api/resources)
  - Auto-reload workspace state poll (/api/health)
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
    """Return latest mtime across .startup/*.json and compiled artifacts."""
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


def _load_resources(plugin_root: Path) -> list[dict[str, Any]]:
    res_file = plugin_root / "mcp_server" / "founder_resources.json"
    if not res_file.exists():
        return []
    try:
        return json.loads(res_file.read_text(encoding="utf-8"))
    except Exception:
        return []


def render_studio_shell(workspace: Path) -> str:
    state_file = workspace / ".startup" / "state.json"
    company = workspace.name
    stage = "idea"
    if state_file.exists():
        try:
            st = json.loads(state_file.read_text(encoding="utf-8"))
            company = st.get("companyName") or company
            stage = st.get("stage") or stage
        except Exception:
            pass

    esc_company = html.escape(str(company))
    esc_stage = html.escape(str(stage))

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>{esc_company} — Startup Antigravity Studio</title>
  <style>
    :root {{ --bg:#020617; --nav:#0f172a; --card:#1e293b; --border:#334155; --text:#f8fafc; --muted:#94a3b8; --accent:#10b981; --amber:#f59e0b; }}
    * {{ box-sizing:border-box; }}
    html,body {{ margin:0; height:100%; font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif; background:var(--bg); color:var(--text); display:flex; flex-direction:column; }}
    header {{ display:flex; align-items:center; gap:12px; padding:10px 18px; background:var(--nav); border-bottom:1px solid var(--border); flex-wrap:wrap; }}
    .brand {{ font-weight:800; color:var(--accent); letter-spacing:.03em; font-size:15px; }}
    .pill {{ font-size:11px; padding:2px 8px; border-radius:999px; background:#064e3b; color:#6ee7b7; font-weight:700; text-transform:uppercase; }}
    nav {{ display:flex; gap:6px; flex-wrap:wrap; margin-left:auto; }}
    button.tab {{ background:transparent; border:1px solid var(--border); color:var(--muted); padding:6px 12px; border-radius:8px; cursor:pointer; font-weight:600; font-size:13px; }}
    button.tab.active {{ background:var(--accent); color:#022c22; border-color:var(--accent); }}
    main {{ flex:1; position:relative; display:flex; }}
    iframe {{ width:100%; height:100%; border:0; background:#0b1120; }}
    #resources-panel, #board-panel {{ display:none; width:100%; height:100%; overflow:auto; padding:24px; max-width:1100px; margin:0 auto; }}
    .search-bar {{ width:100%; padding:12px 14px; border-radius:10px; border:1px solid var(--border); background:var(--nav); color:var(--text); font-size:15px; margin-bottom:18px; }}
    .res-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px; }}
    .res-card {{ background:var(--nav); border:1px solid var(--border); border-radius:12px; padding:16px; display:flex; flex-direction:column; gap:8px; }}
    .res-cat {{ font-size:11px; color:var(--amber); text-transform:uppercase; font-weight:700; letter-spacing:.05em; }}
    .res-card a {{ color:var(--accent); font-weight:700; text-decoration:none; font-size:15px; }}
    .res-card p {{ margin:0; color:var(--muted); font-size:13px; line-height:1.45; }}
    .res-takeaway {{ font-size:12px; color:#e2e8f0; background:#1e293b; padding:8px 10px; border-radius:8px; }}
    .modal-bg {{ display:none; position:fixed; inset:0; background:rgba(2,6,23,.78); align-items:center; justify-content:center; z-index:99; }}
    .modal {{ background:var(--nav); border:1px solid var(--border); border-radius:14px; padding:22px; width:min(460px,92vw); display:grid; gap:10px; }}
    .modal label {{ font-size:12px; color:var(--muted); font-weight:700; display:grid; gap:4px; }}
    .modal input, .modal select {{ padding:8px 10px; border-radius:8px; border:1px solid var(--border); background:#020617; color:var(--text); font-size:14px; }}
    .score-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:12px; margin:16px 0; }}
    .score-card {{ background:var(--nav); border:1px solid var(--border); border-radius:12px; padding:16px; }}
    .score-val {{ font-size:28px; font-weight:800; color:var(--accent); }}
  </style>
</head>
<body>
  <header>
    <span class="brand">STARTUP ANTIGRAVITY STUDIO</span>
    <span style="color:#cbd5e1;font-weight:700;">{esc_company}</span>
    <span class="pill">{esc_stage}</span>
    <nav>
      <button class="tab active" data-tab="dashboard" onclick="selectTab('dashboard')">Command Center</button>
      <button class="tab" data-tab="deck" onclick="selectTab('deck')">Pitch Deck</button>
      <button class="tab" data-tab="dataroom" onclick="selectTab('dataroom')">Data Room</button>
      <button class="tab" data-tab="landing" onclick="selectTab('landing')">Landing Page</button>
      <button class="tab" data-tab="board" onclick="selectTab('board')">Board Review</button>
      <button class="tab" data-tab="resources" onclick="selectTab('resources')">54+ Resources</button>
      <button class="tab" onclick="openMetricsModal()" style="border-color:#f59e0b;color:#fbbf24;">Edit Metrics</button>
      <button class="tab" onclick="switchWorkspace()" style="border-color:#38bdf8;color:#7dd3fc;">Switch Workspace</button>
    </nav>
  </header>
  <main>
    <iframe id="viewport" src="/workspace/dashboard/index.html"></iframe>
    <div id="board-panel">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
        <h2 style="margin:0;">3-Lens Partner &amp; Mentor Board Review</h2>
        <button class="tab active" onclick="loadBoardReview()">Re-Run Audit</button>
      </div>
      <div id="board-content" style="margin-top:14px;color:var(--muted);">Loading live audit...</div>
    </div>
    <div id="resources-panel">
      <input id="res-search" class="search-bar" placeholder="Search 54+ founder resources (e.g. singularity, 6ds, x402, pmf, mom test, startup grind, ai)..." oninput="renderResources()" />
      <div id="res-grid" class="res-grid"></div>
    </div>
  </main>
  <div id="metrics-modal" class="modal-bg" onclick="if(event.target===this)closeMetricsModal()">
    <div class="modal">
      <h3 style="margin:0;">Update Live Startup Metrics</h3>
      <label>FI Stage
        <select id="m-stage">
          <option value="idea">idea</option>
          <option value="validation">validation</option>
          <option value="mvp">mvp</option>
          <option value="pre_seed_traction">pre_seed_traction</option>
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
    const ROUTES = {{
      dashboard: '/workspace/dashboard/index.html',
      deck: '/workspace/pitch-deck/index.html',
      dataroom: '/workspace/data-room/index.html',
      landing: '/workspace/landing/index.html',
    }};
    let currentTab = 'dashboard';
    let allResources = [];
    let lastFp = null;

    function selectTab(tab) {{
      currentTab = tab;
      document.querySelectorAll('button.tab[data-tab]').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
      const frame = document.getElementById('viewport');
      const resPanel = document.getElementById('resources-panel');
      const boardPanel = document.getElementById('board-panel');
      frame.style.display = 'none';
      resPanel.style.display = 'none';
      boardPanel.style.display = 'none';
      if (tab === 'resources') {{
        resPanel.style.display = 'block';
        if (!allResources.length) loadResources();
      }} else if (tab === 'board') {{
        boardPanel.style.display = 'block';
        loadBoardReview();
      }} else {{
        frame.style.display = 'block';
        frame.src = ROUTES[tab] + '?t=' + Date.now();
      }}
    }}

    async function loadBoardReview() {{
      const box = document.getElementById('board-content');
      box.innerHTML = 'Running 3-lens audit...';
      const r = await fetch('/api/board-review');
      const d = await r.json();
      if (!d.ok) {{ box.innerHTML = 'Error: ' + (d.error || 'unknown'); return; }}
      box.innerHTML = `
        <div class="score-grid">
          <div class="score-card"><div class="res-cat">Overall Readiness</div><div class="score-val">${{d.overallScore}} / 5.0</div><div>${{d.verdict}}</div></div>
          <div class="score-card"><div class="res-cat">FI Mentor</div><div class="score-val">${{d.scores.fiMentor}} / 5.0</div></div>
          <div class="score-card"><div class="res-cat">VC Lab Partner</div><div class="score-val">${{d.scores.vcLabPartner}} / 5.0</div></div>
          <div class="score-card"><div class="res-cat">PMF Truth Auditor</div><div class="score-val">${{d.scores.pmfTruthAuditor}} / 5.0</div></div>
        </div>
        <div class="res-card">
          <div class="res-cat">Top 3 Prioritized 7-Day Actions</div>
          <ol style="margin:4px 0 0 18px;padding:0;color:#e2e8f0;">
            ${{(d.topActions || []).map(a => '<li style="margin:6px 0;">' + a + '</li>').join('')}}
          </ol>
        </div>`;
    }}

    function openMetricsModal() {{ document.getElementById('metrics-modal').style.display = 'flex'; }}
    function closeMetricsModal() {{ document.getElementById('metrics-modal').style.display = 'none'; }}

    async function saveMetrics() {{
      const payload = {{ stage: document.getElementById('m-stage').value }};
      const mrr = document.getElementById('m-mrr').value;
      const gm = document.getElementById('m-gm').value;
      const cash = document.getElementById('m-cash').value;
      const burn = document.getElementById('m-burn').value;
      if (mrr !== '') payload.mrrUsd = Number(mrr);
      if (gm !== '') payload.grossMarginPct = Number(gm);
      if (cash !== '') payload.cashOnHandUsd = Number(cash);
      if (burn !== '') payload.monthlyBurnUsd = Number(burn);
      await fetch('/api/metrics', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify(payload) }});
      closeMetricsModal();
      if (currentTab === 'dashboard' || currentTab === 'dataroom') {{
        document.getElementById('viewport').src = ROUTES[currentTab] + '?t=' + Date.now();
      }}
    }}

    async function switchWorkspace() {{
      const next = prompt('Enter full path to another startup workspace folder:');
      if (!next) return;
      const r = await fetch('/api/workspace', {{ method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{workspace:next}}) }});
      const d = await r.json();
      if (d.ok) location.reload(); else alert(d.error || 'Could not switch workspace');
    }}

    async function loadResources() {{
      const r = await fetch('/api/resources');
      const data = await r.json();
      allResources = data.resources || [];
      renderResources();
    }}

    function renderResources() {{
      const q = (document.getElementById('res-search').value || '').toLowerCase().trim();
      const filtered = allResources.filter(item => {{
        if (!q) return true;
        const blob = [item.title, item.category, item.summary, item.keyTakeaway, (item.tags || []).join(' ')].join(' ').toLowerCase();
        return blob.includes(q);
      }});
      document.getElementById('res-grid').innerHTML = filtered.map(item => `
        <div class="res-card">
          <div class="res-cat">${{item.category}} • ${{item.format}}</div>
          <a href="${{item.url}}" target="_blank" rel="noopener">${{item.title}}</a>
          <p>${{item.summary}}</p>
          <div class="res-takeaway"><strong>Takeaway:</strong> ${{item.keyTakeaway}}</div>
        </div>
      `).join('');
    }}

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


def _rebuild_views(ws: Path, p_root: Path) -> None:
    dash_script = p_root / "skills" / "unit-economics-and-profit-os" / "scripts" / "build_dashboard.py"
    if dash_script.exists():
        subprocess.run([sys.executable, str(dash_script), "--workspace", str(ws)], check=False, capture_output=True)
    dr_script = p_root / "skills" / "vc-lab-fundraising-os" / "scripts" / "build_data_room.py"
    if dr_script.exists() and (ws / "data-room" / "index.html").exists():
        subprocess.run([sys.executable, str(dr_script), "--workspace", str(ws)], check=False, capture_output=True)


def create_studio_server(
    workspace: Path,
    plugin_root: Path | None = None,
    host: str = "127.0.0.1",
    port: int = 4020,
) -> ThreadingHTTPServer:
    ctx = {"workspace": workspace.resolve()}
    p_root = (plugin_root or ROOT).resolve()
    resources = _load_resources(p_root)

    class StudioHandler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            return

        def _send_bytes(self, data: bytes, content_type: str, status: int = 200) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _read_json_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
            return json.loads(raw)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            path = unquote(parsed.path)
            try:
                body = self._read_json_body()
            except Exception as exc:
                self._send_bytes(json.dumps({"ok": False, "error": str(exc)}).encode("utf-8"), "application/json", 400)
                return

            if path == "/api/workspace":
                new_path = Path(str(body.get("workspace", ""))).expanduser().resolve()
                if not new_path.exists() or not new_path.is_dir():
                    self._send_bytes(
                        json.dumps({"ok": False, "error": f"Directory not found: {new_path}"}).encode("utf-8"),
                        "application/json",
                        400,
                    )
                    return
                ctx["workspace"] = new_path
                self._send_bytes(
                    json.dumps({"ok": True, "workspace": str(new_path)}).encode("utf-8"),
                    "application/json",
                )
                return

            if path == "/api/metrics":
                ws = ctx["workspace"]
                sdir = ws / ".startup"
                sdir.mkdir(parents=True, exist_ok=True)
                state_file = sdir / "state.json"
                state: dict[str, Any] = {}
                if state_file.exists():
                    try:
                        state = json.loads(state_file.read_text(encoding="utf-8"))
                    except Exception:
                        state = {}
                if "stage" in body and body["stage"] in ("idea", "validation", "mvp", "pre_seed_traction", "seed_scale"):
                    state["stage"] = body["stage"]
                metrics = state.setdefault("metrics", {})
                for key in ("mrrUsd", "grossMarginPct", "cashOnHandUsd", "monthlyBurnUsd"):
                    if key in body and body[key] is not None:
                        metrics[key] = float(body[key])
                if "ikpiCurrent" in body and body["ikpiCurrent"] is not None:
                    state.setdefault("ikpi", {})["current"] = float(body["ikpiCurrent"])
                state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
                _rebuild_views(ws, p_root)
                self._send_bytes(
                    json.dumps({"ok": True, "state": state}).encode("utf-8"),
                    "application/json",
                )
                return

            self._send_bytes(b"Not Found", "text/plain", 404)

        def do_GET(self) -> None:  # noqa: N802
            ws = ctx["workspace"]
            parsed = urlparse(self.path)
            path = unquote(parsed.path)

            if path in ("/", "/index.html"):
                body = render_studio_shell(ws).encode("utf-8")
                self._send_bytes(body, "text/html; charset=utf-8")
                return

            if path == "/api/health":
                payload = {
                    "ok": True,
                    "workspace": str(ws),
                    "fingerprint": _workspace_fingerprint(ws),
                    "resourceCount": len(resources),
                }
                self._send_bytes(json.dumps(payload).encode("utf-8"), "application/json")
                return

            if path == "/api/board-review":
                board_scripts = p_root / "skills" / "weekly-sprint-review" / "scripts"
                if str(board_scripts) not in sys.path:
                    sys.path.insert(0, str(board_scripts))
                from board_review import run_board_review  # noqa: E402

                res = run_board_review(ws, write_memo=True)
                self._send_bytes(json.dumps(res).encode("utf-8"), "application/json")
                return

            if path == "/api/resources":
                qs = parse_qs(parsed.query)
                q = (qs.get("q") or [""])[0].strip().lower()
                items = resources
                if q:
                    items = [
                        r for r in resources
                        if q in json.dumps(r).lower()
                    ]
                self._send_bytes(
                    json.dumps({"count": len(items), "resources": items}).encode("utf-8"),
                    "application/json",
                )
                return

            if path.startswith("/workspace/"):
                rel = path[len("/workspace/"):].lstrip("/")
                target = (ws / rel).resolve()
                # Strict path-traversal guard
                if not str(target).startswith(str(ws)):
                    self._send_bytes(b"Forbidden", "text/plain", 403)
                    return
                if not target.exists() or not target.is_file():
                    msg = (
                        f"<html><body style='background:#0b1120;color:#94a3b8;font-family:sans-serif;padding:40px;'>"
                        f"<h2 style='color:#f8fafc;'>Not built yet: {html.escape(rel)}</h2>"
                        f"<p>Generate this view in Antigravity or click <strong>Preview Sample Startup</strong> in the Launcher.</p>"
                        f"</body></html>"
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
