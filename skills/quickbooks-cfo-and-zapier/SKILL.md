---
name: quickbooks-cfo-and-zapier
description: >-
  Connect QuickBooks Online and 9,000+ startup apps (via Zapier's official Antigravity
  plugin, Intuit's official QuickBooks Online MCP server, or Intuit's CLI) so Antigravity
  acts as a safe, read-first AI Bookkeeper, Fractional CFO, and workflow automation hub.
  Use when a founder wants to ask plain-English questions about QuickBooks P&L/cash/invoices,
  sync verified financials into `.startup/state.json` and `docs/INVESTOR_UPDATE.md`, draft
  invoices for signed Customer PACTs, or wire ethical Zapier startup automations.
---

# QuickBooks Online CFO Copilot & Zapier Automation Hub

Turn Antigravity into your **read-first Fractional CFO & ethical operations hub** by pairing Startup Antigravity with **QuickBooks Online** (Intuit official MCP/CLI) and **Zapier** (`antigravity-plugins-partners/plugin/zapier` — 9,000+ apps via 1-click OAuth).

See [qbo-zapier-setup.md](./references/qbo-zapier-setup.md) for novice-friendly 1-click Zapier OAuth setup, Intuit official MCP `mcp_config.json` snippets, and `intuit-cli-for-quickbooks` installation.

## Non-Negotiable Accounting Safety Rules (Mensarius Financial Stewardship)

1. **Read-First by Default:** Reading Profit & Loss, Balance Sheet, Cash Flow, AR/AP Aging, and customer lists is always safe.
2. **Preview & Explicit Approval Before Any Write:** Before creating an invoice, categorizing an expense, or recording a bill in QuickBooks (via MCP, Zapier, or `intuit --dry-run`), ALWAYS present a clear summary table (`Entity`, `Customer/Vendor`, `Amount`, `Category`, `Date`) and wait for explicit founder confirmation.
3. **Never Silently Void or Delete:** Refuse to delete or void posted financial entries without explicit written confirmation and an audit note.
4. **CPA Boundary:** AI bookkeeping accelerates clarity and due-diligence prep—it is **not** a licensed CPA or tax advisor. Always have a qualified accountant review tax filings, payroll, and official period closes.

## Workflow A: Plain-English QuickBooks Q&A & Live Telemetry Sync

1. Query QuickBooks (via active **Zapier** MCP actions, **Intuit QBO MCP** reports, or `intuit` CLI JSON output) for:
   - Monthly Profit & Loss (Revenue, COGS, Gross Margin %, Operating Burn)
   - Current Cash Balance & Overdue Accounts Receivable (30+ days)
2. Sync verified numbers into `.startup/state.json` via `startup_update_stage(mrrUsd=..., monthlyBurnUsd=..., cashOnHandUsd=..., grossMarginPct=...)`.
3. Recompute **Default-Alive runway** deterministically via `financial_calc(mode="runway", ...)`.
4. Refresh `docs/INVESTOR_UPDATE.md` (`sprint_manage(action="investor_update")`) so every investor/mentor update reflects verified QuickBooks truth.

## Workflow B: Customer Paid-Pilot PACT -> Draft QuickBooks Invoice

1. Pull signed Customer PACTs via `pact_pipeline_manage(action="summary", kind="customer")`.
2. Draft the matching QuickBooks invoice (customer name, pilot fee, transparent net-7 or upfront terms, 14-day ROI guarantee note).
3. Show the exact draft to the founder for confirmation before creating/sending via QuickBooks MCP or Zapier.

## Workflow C: High-Leverage Ethical Zapier Automations (9,000+ Apps)

When the official **Zapier** Marketplace plugin (`antigravity-plugins-partners/plugin/zapier`) is installed:
- **Cash Velocity Loop:** Stripe payment succeeds -> auto-sync receipt to QuickBooks Online + post milestone ping in Slack/Discord.
- **Discovery & PACT Intake:** New `landing/index.html` Paid-Pilot inquiry -> create CRM lead (HubSpot / Bigin / Google Sheets) + book founder onboarding call.
- **Zero Dark Patterns:** Refuse to wire unsolicited cold-spam blasts, scraped contact lists, or deceptive billing automations through Zapier.
