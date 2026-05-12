---
name: crm-dedupe-orchestrator
description: Orchestrate a guarded CRM dedupe workflow across HubSpot exports, contact and company dedupe agents, merge safety review, and daily hygiene automation.
---

# CRM Dedupe Orchestrator

Top-level entry point for a CRM dedupe session. The user describes the CRM cleanup goal in natural language; you route the work through focused sub-skills.

The plugin engine lives at `${CLAUDE_PLUGIN_ROOT}`. Always `cd` there before running Python commands.

## First Response

Always start by acknowledging the user's request in 1-2 sentences. Then take action. Never go silent.

## Locating Exports

1. Check if the user named specific CSV paths in their message.
2. If not, check `${CLAUDE_PLUGIN_ROOT}/demo_exports/contacts_prechecked.csv` and `${CLAUDE_PLUGIN_ROOT}/demo_exports/companies_prechecked.csv`.
3. If not staged there, check `~/Downloads/` for recently exported HubSpot CSVs (look for filenames containing "contact", "company", "duplicate", or "dedup").
4. **If you cannot find them, ASK the user** for the absolute paths. Do not assume or proceed silently.

## Routing

- HubSpot export validation and one-off backlog setup → invoke the `hubspot-dedupe-backfill` skill via the Skill tool.
- Contact dedupe from validation through capped live merge → invoke the `contact-dedupe-agent` skill.
- Company dedupe from validation through web/AI review and capped live merge → invoke the `company-dedupe-agent` skill.
- Pre-live safety check → invoke the `merge-safety-review` skill.
- Daily scheduled cleanup setup → invoke the `daily-crm-hygiene` skill.

## Default Workflow

1. Acknowledge the request.
2. Locate the CSVs (or ask the user).
3. Route contact CSV to `contact-dedupe-agent` and company CSV to `company-dedupe-agent`.
4. Dry-run capped batches from `${CLAUDE_PLUGIN_ROOT}`.
5. Inspect risk signals and run `merge-safety-review` before any live write.
6. Approve only the safe live scope.
7. Optionally schedule daily high-confidence cleanup via `daily-crm-hygiene`.

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
- Company pairs separated into merge candidates, rejection/suppression candidates, and true human-review cases.
- Daily hygiene cadence documented or scheduled if requested.
- The commands, output, or summary confirm the bundled scoring and review path were used.
