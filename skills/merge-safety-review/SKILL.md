---
name: merge-safety-review
description: Review dedupe blast radius, dry-run status, caps, credentials, audit logging, and risk signals before live CRM merges.
---

# Merge Safety Review

Pre-flight gate before any live CRM write. Acknowledge the request in one sentence, then run the checklist. Never go silent.

The plugin engine lives at `${CLAUDE_PLUGIN_ROOT}`.

## Checklist

- Dry-run completed in the same session.
- Live command uses an explicit `--max-merges` cap.
- Export path is stable and expected.
- IDs are present on both sides.
- No same-ID rows.
- Risk rows are named by row number (not by raw private data).
- For contacts, different populated emails were reviewed.
- For companies, different domains were investigated.
- Bundled scoring was used: `>= 0.95` auto-merge, `0.70-0.95` review, fuzzy capped below auto-merge.
- Master selection uses `pipeline.scorer.select_master()`.
- HubSpot credentials exist (`HUBSPOT_ACCESS_TOKEN` in `${CLAUDE_PLUGIN_ROOT}/.env`) but were not printed.
- Audit logging is enabled through `execute_merge()`.
- Operator explicitly approved live mode in this session.

## Approval Language

Use plain language with the user:

```text
Before I let anything touch HubSpot, I export the candidates from HubSpot itself, dry-run the exact file, and cap the live run. The agent is not deciding to merge the whole CRM. It is executing a reviewed batch with an audit trail.
```

## Output

- Return `APPROVED FOR LIVE` only if all checklist items pass.
- Otherwise return `STOP` with the failing items called out by name.

## Stop Conditions

Stop before live mode if:

- The dry-run errored.
- The cap is missing.
- Company domains differ and have not been investigated.
- Contact names differ.
- The dry-run did not use the bundled scoring and master-selection functions.
- The operator has not approved live mode.
- Credentials or environment are unclear.
