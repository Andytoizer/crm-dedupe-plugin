---
name: crm-dedupe-orchestrator
description: Orchestrate a guarded CRM dedupe workflow across HubSpot exports, contact and company dedupe agents, merge safety review, and daily hygiene automation.
---

# CRM Dedupe Orchestrator

Use this as the top-level orchestrator. The human can describe the CRM cleanup goal in natural language while Codex routes the work through focused skills.

## Required First Moves

1. Work from this repo root unless the user explicitly provides another path.
2. Locate the duplicate exports, usually under `demo_exports/`.
3. Never run live merges until a dry-run summary has been inspected.
4. Use `$merge-safety-review` before any live write.
5. Use `$contact-dedupe-agent` for contact dedupe end to end.
6. Use `$company-dedupe-agent` for company dedupe end to end, especially when domains differ, but do not let it replace the repo's AI review pipeline.
7. Use `$daily-crm-hygiene` only after the backfill workflow is understood.
8. Preserve the scoring contract in `references/original-scoring-contract.md`.

## Routing

- HubSpot export validation and backlog setup: `$hubspot-dedupe-backfill`
- Contact dedupe from validation through capped live merge: `$contact-dedupe-agent`
- Company dedupe from validation through web/AI review and capped live merge: `$company-dedupe-agent`
- Pre-live safety check: `$merge-safety-review`
- Daily scheduled cleanup: `$daily-crm-hygiene`

## Orchestrator Pattern

The default workflow is:

1. Show the live CRM duplicate backlog.
2. Use pre-exported HubSpot duplicate CSVs.
3. Route contact duplicates to `$contact-dedupe-agent`.
4. Route company duplicates to `$company-dedupe-agent`.
5. Dry-run capped batches from this repo root.
6. Inspect risk signals and use `$merge-safety-review`.
7. Approve only the safe live scope.
8. Schedule daily high-confidence cleanup.

## Safety Rules

- Default to dry-run.
- Keep live batches capped.
- Do not expose tokens, `.env`, raw sensitive CRM rows, or private customer data.
- Contacts can be live-merged after dry-run and review.
- Companies require extra caution when domains differ, but different domains alone are not proof of different companies.
- Do not invent alternate scoring. Use `pipeline.scorer.score_contacts()`, `pipeline.scorer.score_companies()`, and `pipeline.scorer.select_master()`.
- Keep thresholds unchanged: `AUTO_MERGE_THRESHOLD = 0.95`, `REVIEW_THRESHOLD = 0.70`, and fuzzy scores capped at `0.89`.
- Company decisions should preserve the bundled review contract:
  - `YES` -> approved merge candidate.
  - `NO` -> reject/suppress as a known non-duplicate.
  - `UNSURE` -> queue for human review.
- Do not downgrade all medium/low web-evidence cases directly to manual review. The AI step exists to reason over mixed evidence such as same name, shared phone, same page title, rebrands, or alternate domains.

## Done State

A handled dedupe session has:

- Export files found and row counts summarized.
- Contact dry-run results summarized.
- Risk rows called out.
- Approved live scope clearly capped.
- Company pairs separated into merge candidates, rejection/suppression candidates, and true human-review cases.
- Daily hygiene cadence documented or scheduled.
- The commands, output, or summary confirm the bundled scoring and review path were used.
