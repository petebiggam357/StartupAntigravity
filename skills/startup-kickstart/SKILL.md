---
name: startup-kickstart
description: >-
  Day-0 Founder Institute startup onboarding wizard. Use when a founder starts a new
  company or opens an uninitialized workspace without `.startup/state.json`. Runs a
  focused 5-question intake, crafts & lints an FI One-Sentence Madlibs Pitch (+ Secret
  Sauce), defines a For-Progress Impact Thesis & iKPI, and scaffolds the entire company
  operating system (`.startup/`, `docs/`, and an interactive `pitch-deck/`).
---

# Startup Kickstart (Day-0 Founder OS Bootstrap)

Turn a raw idea into an actionable, revenue-first company workspace in under 10 minutes using Founder Institute (`fi.co`) and VC Lab Mensarius Oath discipline.

## Step 1: Run the 5-Question Founder Intake

Ask the founder these 5 sharp questions (keep it conversational, or extract answers from what they already shared):

1. **Company Name & Offering**: What are you calling it (working name is fine) and what concrete product/service are you building?
2. **Hyper-Specific Buyer (ICP)**: Who is the *exact* person with budget who suffers this pain today? (Reject "everyone", "consumers", or "small businesses".)
3. **Quantified Problem & Secret Sauce**: What costly problem do they face today, and what is your unfair **Secret Sauce** (proprietary workflow, data, domain edge, or speed)?
4. **14-Day First-Dollar Path**: What is the fastest ethical offer (paid pilot, pre-order PACT, concierge service, or deposit) someone could pay for within 14 days?
5. **For-Progress Impact Thesis & iKPI**: As this company generates massive profit, what measurable positive outcome (iKPI / UN SDG alignment) compounds alongside revenue? (Call `ikpi_catalog_search` with their industry/keywords to offer 3 concrete UN SDG-aligned iKPIs in 10 seconds!)

## Step 2: Craft & Lint the FI One-Sentence Pitch

Format their answer strictly into the **FI Madlibs Formula**:
> *"My company, **[Company Name]**, is developing **[defined offering]** to help **[defined audience]** **[solve specific problem]** with **[secret sauce]**."*

Call the `fi_pitch_lint` MCP tool on the draft pitch. Rewrite until `passed == true` (zero buzzwords, zero superlatives, zero vague audiences).

## Step 3: Scaffold the Entire Company Workspace

Run the bundled scaffolder script [scaffold_startup.py](./scripts/scaffold_startup.py):

```bash
python3 ./scripts/scaffold_startup.py \
  --workspace "/path/to/founder/workspace" \
  --company "Acme Flow" \
  --offering "an automated invoice reconciliation tool" \
  --audience "independent dental clinic managers" \
  --problem "recover $4,000/month in unbilled insurance claims" \
  --secret-sauce "real-time payer-rule validation trained on regional coding schedules" \
  --impact-thesis "Prevent small healthcare clinics from closing due to administrative billing losses" \
  --ikpi "Dollars recovered for independent community clinics" \
  --archetype "b2b-saas"
```

This creates:
- `.startup/state.json` + `.startup/assumptions.json` (seeded with the 4 Riskiest Assumptions) + empty trackers for experiments, interviews, and PACTs
- `docs/ONE_PAGER.md` (Lean Canvas + 14-Day First-Dollar Sprint)
- `docs/ETHICS_AND_IKPI.md` (Mensarius Oath Founder Charter + For-Progress iKPI)
- `docs/DISCOVERY_SCRIPT.md` (Mom Test interview script)
- `docs/MVP_SPEC.md` (7-day vertical slice & NOT-Building-Yet Cut-List)
- `pitch-deck/deck.json`, `pitch-deck/index.html`, and `pitch-deck/DECK.md`

## Step 4: Verify & Launch Week-1 Sprint

1. Call `startup_get_state` to verify telemetry and stage (`idea` or `validation`).
2. Present the founder with their **3 immediate Week-1 actions**:
   - Book 5–15 Customer Discovery calls using `docs/DISCOVERY_SCRIPT.md` (log each via `interview_manage`).
   - Run the Riskiest Assumption Test (load `revenue-first-validation`).
   - Open `pitch-deck/index.html` and practice the 3-minute FI pitch (`T` key timer).
