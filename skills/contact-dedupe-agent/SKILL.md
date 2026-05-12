---
name: contact-dedupe-agent
description: Own contact dedupe end to end: validate exports, score contacts with the original repo, dry-run, review risk, and run approved capped merges.
---

# Contact Dedupe Agent

Use this for contact duplicate cleanup from HubSpot exports or the CRM Dedupe Agent pipeline.

This is an entity-owned agent. It owns contact dedupe end to end, not just one phase of the workflow.

## Default Scope

- Default file: `demo_exports/contacts_prechecked.csv` when the operator has staged an export there.
- Default dry-run cap: 25
- Default live cap: 25

## Workflow

1. Confirm the contact CSV exists.
2. Change into the CRM Dedupe Agent repo before running commands.
3. Validate expected contact columns and count rows without printing private row data.
4. Score contacts with the original repo behavior.
5. Run dry-run with the cap.
6. Summarize proposed merges, review candidates, skipped rows, and errors.
7. Scan first capped rows for:
   - missing IDs
   - same ID on both sides
   - different populated emails
   - different full names
8. Use `$merge-safety-review` before live mode.
9. Ask for or confirm operator approval before live mode.
10. Run live only with the same cap.
11. Summarize changes, skips, and errors.

## Safety

- Never live-merge without a successful dry-run in the same session.
- Never remove the cap unless the user explicitly asks after review.
- If different names appear, stop and ask before live mode.
- If different populated emails appear, flag row numbers and recommend manual review.
- Use the original repo's `select_master()` through `review/merge_from_csv.py`; never choose master by CSV order.
- Contact scoring must match the original repo: email exact `1.0`, Gmail dot-insensitive `0.97`, LinkedIn `0.98`, phone `0.92`, fuzzy name+company capped at `0.89`.
- `AUTO_MERGE` contact pairs are candidates for capped merge after safety review.
- `REVIEW` contact pairs go through the original AI review path, not a plugin-local judgment.

## Commands

```bash
cd "$CRM_DEDUPE_AGENT_REPO"
python3 review/merge_from_csv.py --contacts demo_exports/contacts_prechecked.csv --limit 25
python3 review/ai_review.py --type contact --limit 25
python3 review/merge_from_csv.py --contacts demo_exports/contacts_prechecked.csv --live --limit 25
```
