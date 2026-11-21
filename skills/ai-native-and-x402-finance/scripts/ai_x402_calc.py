#!/usr/bin/env python3
"""Deterministic AI Economics, x402 Micropayment Modeler, and Tokenization Readiness Engine.

Zero external dependencies (Python 3.10+ standard library only).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def calc_ai_cogs_margin(args: dict[str, Any]) -> dict[str, Any]:
    """Deterministically model per-customer AI inference COGS and gross margin %."""
    arpu = float(args.get("monthly_arpu_usd", 99.0))
    reqs_per_user = float(args.get("monthly_requests_per_user", 500.0))
    avg_in_tokens = float(args.get("avg_input_tokens", 1500.0))
    avg_out_tokens = float(args.get("avg_output_tokens", 600.0))
    cache_hit_pct = max(0.0, min(95.0, float(args.get("cache_hit_pct", 30.0))))
    fast_share_pct = max(0.0, min(100.0, float(args.get("fast_model_share_pct", 80.0))))
    # Blended USD per 1M tokens (conservative public defaults; callers can override)
    fast_in_per_m = float(args.get("fast_input_usd_per_1m", 0.15))
    fast_out_per_m = float(args.get("fast_output_usd_per_1m", 0.60))
    frontier_in_per_m = float(args.get("frontier_input_usd_per_1m", 3.00))
    frontier_out_per_m = float(args.get("frontier_output_usd_per_1m", 15.00))
    non_ai_cogs = float(args.get("other_monthly_cogs_usd", 3.0))

    fast_ratio = fast_share_pct / 100.0
    frontier_ratio = 1.0 - fast_ratio
    effective_in_tokens = avg_in_tokens * (1.0 - (cache_hit_pct / 100.0) * 0.75)

    blended_in_rate = (fast_ratio * fast_in_per_m) + (frontier_ratio * frontier_in_per_m)
    blended_out_rate = (fast_ratio * fast_out_per_m) + (frontier_ratio * frontier_out_per_m)

    cost_per_req = (
        (effective_in_tokens / 1_000_000.0) * blended_in_rate
        + (avg_out_tokens / 1_000_000.0) * blended_out_rate
    )
    monthly_ai_cogs = cost_per_req * reqs_per_user
    total_cogs = monthly_ai_cogs + non_ai_cogs
    gross_profit = arpu - total_cogs
    gross_margin_pct = (gross_profit / arpu * 100.0) if arpu > 0 else 0.0

    meets_floor = gross_margin_pct >= 75.0
    recommendations: list[str] = []
    if not meets_floor:
        recommendations.append(
            "Gross margin is below Startup Antigravity's 75% floor — route more routine extraction/classification traffic to fast/local models or raise value-based ARPU."
        )
    if fast_share_pct < 70.0:
        recommendations.append(
            f"Fast-model routing is {fast_share_pct:.0f}%. Routing 75-85% of routine calls to Flash/Mini/Haiku typically cuts AI COGS by 50-75%."
        )
    if cache_hit_pct < 25.0:
        recommendations.append(
            "Enable system-prompt / context caching to cut repeated input token costs up to 75%."
        )
    if not recommendations:
        recommendations.append(
            "Healthy AI unit economics (>=75% gross margin). Lock in a 30-case golden eval suite before changing models."
        )

    return {
        "action": "ai_cogs_margin",
        "monthlyArpuUsd": round(arpu, 2),
        "costPerRequestUsd": round(cost_per_req, 6),
        "monthlyAiCogsPerUserUsd": round(monthly_ai_cogs, 2),
        "totalMonthlyCogsPerUserUsd": round(total_cogs, 2),
        "monthlyGrossProfitPerUserUsd": round(gross_profit, 2),
        "grossMarginPct": round(gross_margin_pct, 2),
        "meets75PctMarginFloor": meets_floor,
        "assumptions": {
            "monthlyRequestsPerUser": reqs_per_user,
            "fastModelSharePct": fast_share_pct,
            "cacheHitPct": cache_hit_pct,
        },
        "recommendations": recommendations,
    }


def calc_x402_micropayment_model(
    args: dict[str, Any],
    workspace: Path | None = None,
) -> dict[str, Any]:
    """Compare legacy card rails vs x402 USDC settlement for AI agent pay-per-call traffic."""
    price_per_call = float(args.get("price_per_call_usd", 0.05))
    monthly_calls = int(args.get("monthly_paid_calls", 50000))
    l2_fee_per_tx = float(args.get("x402_settlement_fee_usd", 0.0005))
    card_pct = float(args.get("card_fee_pct", 2.9)) / 100.0
    card_fixed = float(args.get("card_fixed_fee_usd", 0.30))
    endpoint_path = str(args.get("endpoint_path", "/api/v1/agent-query")).strip()
    network = str(args.get("network", "base-mainnet (USDC)")).strip()
    write_spec = bool(args.get("write_spec", False))

    gross_rev = price_per_call * monthly_calls
    card_fees = monthly_calls * (price_per_call * card_pct + card_fixed)
    card_net = gross_rev - card_fees
    card_viable = card_net > 0 and (card_fees / gross_rev < 0.15 if gross_rev > 0 else False)

    x402_fees = monthly_calls * l2_fee_per_tx
    x402_net = gross_rev - x402_fees
    x402_keep_pct = (x402_net / gross_rev * 100.0) if gross_rev > 0 else 0.0
    monthly_savings = x402_net - card_net

    spec_path_str: str | None = None
    if write_spec and workspace is not None:
        docs_dir = workspace / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        spec_file = docs_dir / "X402_AGENT_MONETIZATION_SPEC.md"
        spec_md = f"""# x402 Agent-Economy Monetization Spec

> Generated by Startup Antigravity (`ai_x402_calc`) • Protocol: HTTP `402 Payment Required` (`x402.org`)

## 1. Pay-Per-Call Endpoint Economics (`[TARGET]`)
- **Protected Endpoint:** `{endpoint_path}`
- **Settlement Rail:** `{network}`
- **Unit Price:** `${price_per_call:.4f}` USDC per call
- **Projected Volume:** `{monthly_calls:,}` paid calls / month
- **Gross Revenue:** `${gross_rev:,.2f}` / month
- **x402 Net Revenue (after ~`${l2_fee_per_tx:.4f}`/tx L2 fee):** `${x402_net:,.2f}` / month (**{x402_keep_pct:.2f}%** kept)
- **Legacy Card Net Revenue (`2.9% + $0.30/tx`):** `${card_net:,.2f}` / month ({"Viable" if card_viable else "Unviable for micropayments"})

## 2. Standard HTTP 402 Handshake Flow
1. **Client / AI Agent** sends `POST {endpoint_path}` without payment header.
2. **Your API** responds `HTTP/1.1 402 Payment Required` with an `X-PAYMENT-REQUIRED` JSON payload specifying:
   - `scheme`: `"exact"`
   - `network`: `"{network}"`
   - `asset`: `"USDC"`
   - `maxAmountRequired`: `"{price_per_call:.4f}"`
   - `payTo`: `"<YOUR_TREASURY_WALLET_ADDRESS>"` *(never commit private keys!)*
3. **Client / AI Agent** signs an exact-amount USDC payment authorization and retries `POST {endpoint_path}` with `X-PAYMENT: <signed-payload>`.
4. **Facilitator / Verifier** validates signature & settles USDC in ~2 seconds; your API returns `200 OK` + response payload.

## 3. Mensarius Oath & Accounting Hygiene
- **Zero Hidden Fees:** Always return exact per-call pricing in the `402` challenge before charging an agent.
- **Bookkeeping:** Sync realized USDC receipts into fiat-denominated QuickBooks Online revenue accounts daily/monthly for clean tax reporting.
- **Security:** Keep treasury signing keys in hardware/multisig custody; never store private keys in `.env` or Git.
"""
        spec_file.write_text(spec_md, encoding="utf-8")
        spec_path_str = str(spec_file)

    return {
        "action": "x402_micropayment_model",
        "pricePerCallUsd": price_per_call,
        "monthlyPaidCalls": monthly_calls,
        "grossMonthlyRevenueUsd": round(gross_rev, 2),
        "legacyCard": {
            "totalFeesUsd": round(card_fees, 2),
            "netRevenueUsd": round(card_net, 2),
            "viableForMicropayments": card_viable,
        },
        "x402Usdc": {
            "network": network,
            "totalFeesUsd": round(x402_fees, 2),
            "netRevenueUsd": round(x402_net, 2),
            "founderKeepPct": round(x402_keep_pct, 2),
        },
        "monthlyAdvantageOverCardsUsd": round(monthly_savings, 2),
        "specPath": spec_path_str,
    }


def eval_tokenization_readiness(args: dict[str, Any]) -> dict[str, Any]:
    """Deterministic 'Do You Even Need a Token?' ethical & regulatory readiness scorecard."""
    use_case = str(args.get("use_case", "")).strip()
    needs_micropayments = bool(args.get("needs_agent_micropayments", False))
    needs_cross_border = bool(args.get("needs_cross_border_settlement", False))
    represents_regulated_rwa = bool(args.get("represents_regulated_rwa", False))
    has_paying_customers = bool(args.get("has_paying_fiat_customers", False))
    plans_public_speculative_token = bool(args.get("plans_public_speculative_token", False))

    warnings: list[str] = []
    if plans_public_speculative_token:
        warnings.append(
            "HIGH RISK (Mensarius Oath & Securities Law): Never launch a speculative public token to raise capital or substitute for PMF. This triggers severe Howey Test / unregistered-securities liability."
        )
    if not has_paying_customers and represents_regulated_rwa:
        warnings.append(
            "Validate paying demand with a simple fiat/SPV pilot before spending legal/engineering cycles on ERC-3643 RWA tokenization."
        )

    if plans_public_speculative_token:
        verdict = "DO_NOT_LAUNCH_SPECULATIVE_TOKEN"
        recommended_rail = "Fiat (Stripe) or regulated USDC payment rails (x402) only — no custom coin."
    elif needs_micropayments or needs_cross_border:
        verdict = "USE_STABLECOIN_AND_X402_RAILS"
        recommended_rail = "Use USDC via x402 (HTTP 402) and/or Circle/Stripe stablecoin rails — zero custom token needed!"
    elif represents_regulated_rwa and has_paying_customers:
        verdict = "COMPLIANT_RWA_EVALUATION"
        recommended_rail = "Explore permissioned ERC-3643 tokenization with a licensed transfer agent and qualified securities counsel."
    else:
        verdict = "STAY_FIAT_FIRST"
        recommended_rail = "Standard Stripe / QuickBooks Online fiat billing is faster, simpler, and higher-velocity right now."

    return {
        "action": "tokenization_readiness",
        "useCase": use_case or "Unspecified",
        "verdict": verdict,
        "recommendedRail": recommended_rail,
        "warnings": warnings,
        "legalDisclaimer": (
            "Educational business framework only — NOT legal, tax, or securities advice. "
            "Always consult qualified startup and securities counsel before issuing any digital asset or tokenized instrument."
        ),
    }


def scaffold_x402_starter(
    args: dict[str, Any],
    workspace: Path | None = None,
) -> dict[str, Any]:
    """Generate a runnable HTTP 402 (x402) pay-per-call starter defaulting safely to Base Sepolia testnet."""
    ws = (workspace or Path.cwd()).resolve()
    stack = str(args.get("stack", "python-fastapi")).strip().lower()
    if stack not in ("python-fastapi", "node-express"):
        raise ValueError("stack must be 'python-fastapi' or 'node-express'.")
    price_usdc = float(args.get("price_per_call_usd", 0.05))
    endpoint_path = str(args.get("endpoint_path", "/api/v1/agent-query")).strip()
    if not endpoint_path.startswith("/"):
        endpoint_path = "/" + endpoint_path
    network = str(args.get("network", "base-sepolia")).strip()

    out_dir = ws / "x402-starter"
    out_dir.mkdir(parents=True, exist_ok=True)
    created: list[str] = []

    env_example = (
        "# Startup Antigravity x402 Starter — NEVER commit real private keys to Git!\n"
        f"X402_NETWORK={network}\n"
        f"X402_PRICE_USDC={price_usdc:.4f}\n"
        "X402_PAY_TO_ADDRESS=0xYOUR_TESTNET_OR_TREASURY_ADDRESS\n"
        "X402_FACILITATOR_URL=https://x402.org/facilitator\n"
        "PORT=8402\n"
    )
    (out_dir / ".env.example").write_text(env_example, encoding="utf-8")
    created.append(str(out_dir / ".env.example"))

    if stack == "python-fastapi":
        server_code = f'''#!/usr/bin/env python3
"""Runnable x402 HTTP 402 Pay-Per-Call Starter (Python stdlib — zero pip installs required to test!).

Swap the simulated facilitator verifier for the official Coinbase x402 facilitator SDK
before moving from {network} testnet to production mainnet.
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

NETWORK = os.environ.get("X402_NETWORK", "{network}")
PRICE_USDC = os.environ.get("X402_PRICE_USDC", "{price_usdc:.4f}")
PAY_TO = os.environ.get("X402_PAY_TO_ADDRESS", "0xYOUR_TESTNET_OR_TREASURY_ADDRESS")
ENDPOINT = "{endpoint_path}"


class X402Handler(BaseHTTPRequestHandler):
    def _json(self, status: int, body: dict, extra_headers: dict[str, str] | None = None) -> None:
        raw = json.dumps(body, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        for k, v in (extra_headers or {{}}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != ENDPOINT:
            self._json(404, {{"error": "Not found", "expectedEndpoint": ENDPOINT}})
            return

        payment_header = self.headers.get("X-PAYMENT")
        if not payment_header:
            challenge = {{
                "x402Version": 1,
                "accepts": [
                    {{
                        "scheme": "exact",
                        "network": NETWORK,
                        "asset": "USDC",
                        "maxAmountRequired": PRICE_USDC,
                        "payTo": PAY_TO,
                        "resource": ENDPOINT,
                    }}
                ],
            }}
            self._json(
                402,
                {{"error": "Payment Required", "paymentRequirements": challenge}},
                extra_headers={{"X-PAYMENT-REQUIRED": json.dumps(challenge)}},
            )
            return

        # In production: verify & settle `payment_header` via X402_FACILITATOR_URL before fulfilling
        length = int(self.headers.get("Content-Length", "0"))
        req_body = self.rfile.read(length).decode("utf-8") if length > 0 else "{{}}"
        self._json(
            200,
            {{
                "ok": True,
                "settledNetwork": NETWORK,
                "chargedUsdc": PRICE_USDC,
                "paymentProofReceived": payment_header[:32] + "...",
                "result": {{"echo": req_body, "message": "Paid AI-agent call fulfilled cleanly."}},
            }},
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8402"))
    print(f"x402 starter listening on http://127.0.0.1:{{port}}{{ENDPOINT}} (network={{NETWORK}})")
    HTTPServer(("127.0.0.1", port), X402Handler).serve_forever()
'''
        (out_dir / "server.py").write_text(server_code, encoding="utf-8")
        created.append(str(out_dir / "server.py"))

        client_code = f'''#!/usr/bin/env python3
"""Local test client demonstrating the 2-step HTTP 402 -> X-PAYMENT retry handshake."""

import json
import urllib.error
import urllib.request

URL = "http://127.0.0.1:8402{endpoint_path}"
BODY = json.dumps({{"query": "Analyze solar EPC churn signals"}}).encode("utf-8")

req1 = urllib.request.Request(URL, data=BODY, headers={{"Content-Type": "application/json"}}, method="POST")
try:
    urllib.request.urlopen(req1)
except urllib.error.HTTPError as err:
    print("Step 1 — Received expected HTTP", err.code)
    print("X-PAYMENT-REQUIRED:", err.headers.get("X-PAYMENT-REQUIRED"))

req2 = urllib.request.Request(
    URL,
    data=BODY,
    headers={{
        "Content-Type": "application/json",
        "X-PAYMENT": "demo-signed-base-sepolia-usdc-authorization",
    }},
    method="POST",
)
with urllib.request.urlopen(req2) as resp:
    print("Step 2 — Paid retry HTTP", resp.status)
    print(resp.read().decode("utf-8"))
'''
        (out_dir / "test_agent_client.py").write_text(client_code, encoding="utf-8")
        created.append(str(out_dir / "test_agent_client.py"))
    else:
        server_js = f'''// Runnable x402 HTTP 402 Pay-Per-Call Starter (Node.js 18+ built-in http — zero npm install!)
const http = require("http");

const NETWORK = process.env.X402_NETWORK || "{network}";
const PRICE_USDC = process.env.X402_PRICE_USDC || "{price_usdc:.4f}";
const PAY_TO = process.env.X402_PAY_TO_ADDRESS || "0xYOUR_TESTNET_OR_TREASURY_ADDRESS";
const ENDPOINT = "{endpoint_path}";
const PORT = Number(process.env.PORT || 8402);

const server = http.createServer((req, res) => {{
  if (req.method !== "POST" || req.url !== ENDPOINT) {{
    res.writeHead(404, {{ "Content-Type": "application/json" }});
    return res.end(JSON.stringify({{ error: "Not found", expectedEndpoint: ENDPOINT }}));
  }}
  const payment = req.headers["x-payment"];
  if (!payment) {{
    const challenge = {{
      x402Version: 1,
      accepts: [{{ scheme: "exact", network: NETWORK, asset: "USDC", maxAmountRequired: PRICE_USDC, payTo: PAY_TO, resource: ENDPOINT }}],
    }};
    res.writeHead(402, {{
      "Content-Type": "application/json",
      "X-PAYMENT-REQUIRED": JSON.stringify(challenge),
    }});
    return res.end(JSON.stringify({{ error: "Payment Required", paymentRequirements: challenge }}));
  }}
  res.writeHead(200, {{ "Content-Type": "application/json" }});
  res.end(JSON.stringify({{ ok: true, settledNetwork: NETWORK, chargedUsdc: PRICE_USDC, message: "Paid AI-agent call fulfilled cleanly." }}));
}});

server.listen(PORT, "127.0.0.1", () => {{
  console.log(`x402 starter listening on http://127.0.0.1:${{PORT}}${{ENDPOINT}} (network=${{NETWORK}})`);
}});
'''
        (out_dir / "server.js").write_text(server_js, encoding="utf-8")
        created.append(str(out_dir / "server.js"))

    readme = f"""# x402 Pay-Per-Call Agent Starter (`{stack}`)

> Safe default network: **`{network}`** (testnet). Never deploy to mainnet without verifying facilitator settlement and hardware/multisig treasury custody.

## Quickstart
1. Copy `.env.example` to `.env` and set your testnet `X402_PAY_TO_ADDRESS`.
2. Start the server: `{"python3 server.py" if stack == "python-fastapi" else "node server.js"}`
3. Test the HTTP `402` -> `X-PAYMENT` retry handshake: `{"python3 test_agent_client.py" if stack == "python-fastapi" else f"curl -i -X POST http://127.0.0.1:8402{endpoint_path}"}`

## Mensarius Oath & Accounting Hygiene
- Keep exact pricing transparent in every `402` challenge before charging an agent.
- Sync realized USDC receipts into QuickBooks Online (fiat-denominated) for clean tax compliance.
- Consult qualified legal/tax counsel before launching production digital-asset rails.
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")
    created.append(str(out_dir / "README.md"))

    return {
        "ok": True,
        "action": "x402_starter_scaffold",
        "stack": stack,
        "network": network,
        "pricePerCallUsdc": price_usdc,
        "endpointPath": endpoint_path,
        "outputDir": str(out_dir),
        "createdFiles": created,
    }


def run_ai_x402_calc(args: dict[str, Any], workspace: Path | None = None) -> dict[str, Any]:
    action = str(args.get("action", "ai_cogs_margin")).strip()
    if action == "ai_cogs_margin":
        return calc_ai_cogs_margin(args)
    if action == "x402_micropayment_model":
        return calc_x402_micropayment_model(args, workspace=workspace)
    if action == "tokenization_readiness":
        return eval_tokenization_readiness(args)
    if action == "x402_starter_scaffold":
        return scaffold_x402_starter(args, workspace=workspace)
    raise ValueError(
        f"Unknown ai_x402_calc action '{action}'. Use 'ai_cogs_margin', 'x402_micropayment_model', 'tokenization_readiness', or 'x402_starter_scaffold'."
    )


if __name__ == "__main__":
    import sys

    payload = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {"action": "ai_cogs_margin"}
    print(json.dumps(run_ai_x402_calc(payload, Path.cwd()), indent=2))
