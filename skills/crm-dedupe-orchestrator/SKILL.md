---
name: crm-dedupe-orchestrator
description: Orchestrate a guarded CRM dedupe workflow across HubSpot exports, contact and company dedupe agents, merge safety review, and daily hygiene automation.
---

# CRM Dedupe Orchestrator

Top-level entry point for a CRM dedupe session. The user describes the CRM cleanup goal in natural language; you own the session end to end and may use focused sub-skills as helpers. Do not hand off and stop.

The plugin engine lives at `${CLAUDE_PLUGIN_ROOT}`. Always `cd` there before running Python commands.

## First Response

Always start by acknowledging the user's request in 1-2 sentences. Then take action. Never go silent.

## Locating Exports

1. Check if the user named specific CSV paths in their message.
2. If not, check `${CLAUDE_PLUGIN_ROOT}/demo_exports/contacts_prechecked.csv` and `${CLAUDE_PLUGIN_ROOT}/demo_exports/companies_prechecked.csv`.
3. If not staged there, check `~/Downloads/` for recently exported HubSpot CSVs (look for filenames containing "contact", "company", "duplicate", or "dedup").
4. **If you cannot find them, ASK the user** for the absolute paths. Do not assume or proceed silently.

## Ownership

The orchestrator is responsible for finishing the requested workflow, not merely routing to another skill.

Use focused sub-skills only when their detailed guidance is needed, then continue driving the session yourself:

- HubSpot export validation and one-off backlog setup → `hubspot-dedupe-backfill`.
- Contact-specific risk review → `contact-dedupe-agent`.
- Company-specific risk review → `company-dedupe-agent`.
- Pre-live safety check → `merge-safety-review`.
- Daily scheduled cleanup setup → `daily-crm-hygiene`.

For the common request "I exported duplicate contact and company CSVs; dry-run the first N rows of each", do not stop after invoking a sub-skill. Locate both files, run both full-pipeline dry-runs, wait for both outputs, and return one combined summary.

## Default Workflow

1. Acknowledge the request.
2. Locate the CSVs (or ask the user).
3. Validate row counts and required ID columns without printing raw rows.
4. Run capped dry-runs sequentially from `${CLAUDE_PLUGIN_ROOT}` using the full CSV pipeline:
   `python3 review/merge_from_csv.py --contacts <contact-csv> --limit <N>`
   `python3 review/merge_from_csv.py --companies <company-csv> --limit <N>`
5. Confirm the output includes scorer auto-merge, AI YES, AI NO, AI UNSURE, and discard buckets. If it does not, stop and fix the command path before summarizing.
6. Return one combined summary covering both contacts and companies.
7. Inspect true `UNSURE` residue and run `merge-safety-review` before any live write.
8. Approve only the safe live scope.
9. Optionally schedule daily high-confidence cleanup via `daily-crm-hygiene`.

## Safety Rules

- Default to dry-run.
- Keep live batches capped with explicit `--max-merges`.
- Do not expose tokens, `.env`, raw sensitive CRM rows, or private customer data.
- Contacts can be live-merged after dry-run and review.
- Companies require extra caution when domains differ, but different domains alone are not proof of different companies.
- Do not invent alternate scoring. Use `pipeline.scorer.score_contacts()`, `pipeline.scorer.score_companies()`, and `pipeline.scorer.select_master()`.
- Keep thresholds unchanged: `AUTO_MERGE_THRESHOLD = 0.95`, `REVIEW_THRESHOLD = 0.70`, and fuzzy scores capped at `0.89`.
- Company decisions preserve the bundled review contract:
  - `YES` → approved merge candidate.
  - `NO` → reject/suppress as a known non-duplicate.
  - `UNSURE` → queue for human review.
- Do not downgrade all medium/low web-evidence cases directly to manual review. The AI step exists to reason over mixed evidence such as same name, shared phone, same page title, rebrands, or alternate domains.

## Done State

A handled dedupe session has:

- Export files found (or paths confirmed by the user) and row counts summarized.
- Contact dry-run results summarized.
- Risk rows called out by row number, not by raw private data.
- Approved live scope clearly capped.
- Contact and company pairs separated into scorer auto-merge candidates, AI-approved merge candidates, AI rejection/suppression candidates, and true human-review cases.
- Daily hygiene cadence documented or scheduled if requested.
- The commands, output, or summary confirm the bundled scoring and AI/web review path were used, not just HubSpot's duplicate-export verdict.
