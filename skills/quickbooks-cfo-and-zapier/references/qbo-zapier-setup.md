# QuickBooks Online & Zapier Setup Guide (Novice to Technical)

Choose the connection method that matches your comfort level:

## Option 1: Official Zapier Antigravity Plugin (Easiest — Best for Non-Technical Founders)

Connects **QuickBooks Online + 9,000+ business apps** (Stripe, Gmail, Slack, HubSpot, Notion, Google Sheets, Calendly) via 1-click OAuth with zero developer portal setup:

1. Install **Zapier** (`antigravity-plugins-partners/plugin/zapier`) from the Antigravity Agent Marketplace.
2. Sign in to your Zapier account and enable the specific QuickBooks Online / Stripe / CRM actions you want Antigravity to access (start with read-only report/search actions first!).
3. Ask Antigravity: *"Pull my last 30 days of QuickBooks revenue, expenses, and unpaid invoices, and update `.startup/state.json`."*

---

## Option 2: Intuit Official QuickBooks Online MCP Server (Best for Full 140+ QBO Tools)

Intuit maintains an official open-source `stdio` MCP server (`intuit/quickbooks-online-mcp-server`, Apache-2.0) exposing 140+ tools and 11 core reports (P&L, Balance Sheet, Cash Flow, AR/AP Aging).

1. Create a free app at https://developer.intuit.com/ and note your OAuth credentials.
2. Add the server to your global Antigravity `~/.gemini/config/mcp_config.json` (enable read-only mode first until comfortable!):

```json
{
  "mcpServers": {
    "quickbooks-online": {
      "command": "npx",
      "args": ["-y", "@intuit/quickbooks-online-mcp-server"],
      "env": {
        "QUICKBOOKS_CLIENT_ID": "your-client-id",
        "QUICKBOOKS_CLIENT_SECRET": "your-client-secret",
        "QUICKBOOKS_ENVIRONMENT": "production",
        "QUICKBOOKS_READ_ONLY": "true"
      }
    }
  }
}
```

3. Click **Additional Options (`...`) > MCP Servers > Refresh** in Antigravity.

---

## Option 3: Intuit Official CLI (`intuit-cli-for-quickbooks`)

Great for terminal workflows with encrypted OAuth token storage, structured JSON output, and built-in `--dry-run` / `--idempotency-tag` write safety:

- Install per Intuit's official repository (`intuit-cli-for-quickbooks`), authenticate once, and verify via `ai_connectors_manage(action="detect")` (which auto-detects the `intuit` binary).
- Always run mutating commands with `--dry-run` first so the founder previews every dollar before posting.
