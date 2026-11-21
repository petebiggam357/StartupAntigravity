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
    #resources-panel {{ display:none; width:100%; height:100%; overflow:auto; padding:24px; max-width:1100px; margin:0 auto; }}
    .search-bar {{ width:100%; padding:12px 14px; border-radius:10px; border:1px solid var(--border); background:var(--nav); color:var(--text); font-size:15px; margin-bottom:18px; }}
    .res-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px; }}
    .res-card {{ background:var(--nav); border:1px solid var(--border); border-radius:12px; padding:16px; display:flex; flex-direction:column; gap:8px; }}
    .res-cat {{ font-size:11px; color:var(--amber); text-transform:uppercase; font-weight:700; letter-spacing:.05em; }}
    .res-card a {{ color:var(--accent); font-weight:700; text-decoration:none; font-size:15px; }}
    .res-card p {{ margin:0; color:var(--muted); font-size:13px; line-height:1.45; }}
    .res-takeaway {{ font-size:12px; color:#e2e8f0; background:#1e293b; padding:8px 10px; border-radius:8px; }}
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
      <button class="tab" data-tab="resources" onclick="selectTab('resources')">48+ Resources</button>
    </nav>
  </header>
  <main>
    <iframe id="viewport" src="/workspace/dashboard/index.html"></iframe>
    <div id="resources-panel">
      <input id="res-search" class="search-bar" placeholder="Search 48+ founder resources (e.g. x402, pmf, mom test, startup grind, ai, quickbooks)..." oninput="renderResources()" />
      <div id="res-grid" class="res-grid"></div>
    </div>
  </main>
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
      document.querySelectorAll('button.tab').forEach(b => b.classList.toggle('active', b.dataset.tab === tab));
      const frame = document.getElementById('viewport');
      const panel = document.getElementById('resources-panel');
      if (tab === 'resources') {{
        frame.style.display = 'none';
        panel.style.display = 'block';
        if (!allResources.length) loadResources();
      }} else {{
        panel.style.display = 'none';
        frame.style.display = 'block';
        frame.src = ROUTES[tab];
      }}
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
        if (lastFp !== null && h.fingerprint !== lastFp && currentTab !== 'resources') {{
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
    ws = workspace.resolve()
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

        def do_GET(self) -> None:  # noqa: N802
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
