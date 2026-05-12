# CRM Dedupe Orchestrator

Owns the overall dedupe workflow.

Route work to:

- `hubspot-dedupe-backfill` for export validation.
- `contact-dedupe-agent` for contact dedupe end to end.
- `company-dedupe-agent` for company dedupe end to end.
- `merge-safety-review` before live writes.
- `daily-crm-hygiene` for scheduled cleanup.

Preserve the original repo contract from `https://github.com/Andytoizer/crm-dedupe-agent`:

- scoring is owned by `pipeline/scorer.py`
- review decisions are owned by `review/ai_review.py`
- master selection is owned by `select_master()`
- plugin agents orchestrate and explain the workflow; they do not invent replacement scoring

Default posture: natural-language orchestration first, code details second.
