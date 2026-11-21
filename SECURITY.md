# Security Policy

## Supported Versions
Security fixes are applied to the latest pre-release / release on the `main` branch (`0.0.5-alpha` and newer).

## Built-In Safety Guardrails
Startup Antigravity ships with local `PreToolUse` safety hooks (`hooks/pre_tool_guard.py`) designed to:
- Block committing `.env`, `.pem`, `.key`, or raw investor/customer PII files to Git.
- Block writing hardcoded live API keys (`sk_live_...`, `AKIA...`, `sk-ant-...`, `xai-...`), PEM private keys, or hex wallet `PRIVATE_KEY=0x...` values into source files.
- Require explicit founder confirmation before broadcasting onchain mainnet transactions (`forge script --broadcast`, `cast send`, `solana transfer`) or writing raw email addresses into `data-room/`.
- Bind the local Web Studio HTTP server (`launcher/studio_server.py`) strictly to `127.0.0.1` with path-traversal protection.

## Reporting a Vulnerability
If you discover a security vulnerability (such as path traversal, Zip Slip, secret-guard bypass, or unsafe command execution):
1. **Do not** open a public issue with exploit details.
2. Report it privately via GitHub's **Security -> Advisories -> Report a vulnerability** tab on `petebiggam357/StartupAntigravity`.
3. Include reproduction steps and affected file paths; we will acknowledge within 48 hours and coordinate a fix.
