# Lean Stack Defaults & Gross Margin Guardrails

## Boring, High-Velocity Stack Defaults (Ship in Days, Not Months)

| Layer | Default Lean Choice | Avoid Before $25K MRR |
| :--- | :--- | :--- |
| **App / API** | Single modular monolith (Next.js / FastAPI / Rails / Django) | Microservices, Kafka, service meshes |
| **Database** | Managed Postgres (Supabase / Neon / RDS) or SQLite + Litestream | Multi-region sharded clusters, custom DB ops |
| **Hosting** | PaaS / Serverless (Fly.io, Render, Railway, Cloudflare, Vercel) | Self-managed Kubernetes, complex Terraform |
| **Auth** | Off-the-shelf (Clerk, Auth0, Supabase Auth, BetterAuth) | Hand-rolled auth & session crypto |
| **Payments** | Stripe Checkout / Payment Links + Customer Portal | Custom billing engines |
| **Analytics** | PostHog / Plausible + direct SQL queries on Postgres | Custom data warehouses / Snowflake |

## AI & Cloud COGS Margin Rules

1. **Cache aggressively**: Never pay twice for deterministic extraction or repeated prompts.
2. **Model tiering**: Route classification/formatting to fast, low-cost models; reserve frontier models only for high-value reasoning steps.
3. **Hard usage guardrails**: Set per-tenant rate limits and spending alerts on Day 1 so one power user cannot destroy your monthly profit.
4. **Target Gross Margin**: >= 75% for pure SaaS / AI SaaS; >= 60% for hybrid tech-enabled services.
