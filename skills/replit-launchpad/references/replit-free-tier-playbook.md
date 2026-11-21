# Why Replit + Free-Tier Survival Playbook

> **Creator's Personal Endorsement:** I have used Replit across real startups for years. You can sign up and start on the free tier here: **https://replit.com/refer/peterbiggam** *(transparent disclosure: referral link)*.

## Why Founders Love Running Everything on Replit

For early-stage founders (especially solo or lean 2-person teams), Replit eliminates 90% of DevOps friction by putting the entire product surface under one roof:

1. **Replit Design Mode & Living Design System:** Go from idea to interactive visual layout in minutes before writing heavy backend logic.
2. **Full-Stack Web Apps + Built-In Database & Secrets:** Run Node/Next.js or Python/FastAPI with managed Postgres and encrypted Secrets without touching AWS IAM, Docker, or Terraform.
3. **Real Mobile Apps via Expo (React Native):** Build cross-platform iOS & Android apps in the browser and test instantly on your physical phone by scanning the **Expo Go QR code**.
4. **Replit Slides (Decks):** Keep your investor pitch deck right beside your live product and screenshots—easy to update before every demo.
5. **1-Click Deployments:** Go from validated prototype to shareable live URL in minutes to close your first Paid-Pilot Customer PACT.

---

## Zero-Double-Token-Burn Rules (How to Stretch Replit's Free Tier)

Replit's **Starter (Free)** plan gives you enough runtime and preview power to prototype and validate, but free AI agent credits run out quickly if you let Replit duplicate work Antigravity already did. Follow these 5 rules:

1. **Heavy coding happens locally in Antigravity.** Commit cleanly to your private GitHub repo, then pull inside Replit's **Git pane** (0 Replit AI tokens used!).
2. **Keep `replit.md` at the repo root.** Generated automatically by `replit_workspace_prepare`, it explicitly tells Replit which files are source-of-truth from Antigravity so nothing gets overwritten or re-generated.
3. **Spend Replit AI credits ONLY on high-leverage Replit-native wins:**
   - Initial **Replit Design Mode** layout/theme exploration
   - One-shot **Replit Slides** generation using `REPLIT_SLIDES_BRIEF.md`
   - Fixing a Replit-specific environment/deployment quirk
4. **Respect Free-Tier Deployment Limits:** Free/Starter published links can sleep or expire after ~30 days. Stay on Free during `idea` and `validation`; upgrade to Replit Core (\$20/mo) *only after* your first paying Customer PACT covers it (Revenue-First Velocity!).
5. **Never commit secrets:** Keep `.env` strictly local (blocked by Startup Antigravity's `PreToolUse` hook) and paste production keys exclusively into Replit's encrypted **Secrets** tab.
