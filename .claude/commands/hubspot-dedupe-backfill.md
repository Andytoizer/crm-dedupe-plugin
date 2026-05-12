Use this command to prepare a HubSpot duplicate export backfill.

Arguments from the user:

```text
$ARGUMENTS
```

Workflow:

1. Read `skills/hubspot-dedupe-backfill/SKILL.md`.
2. Work from `$CRM_DEDUPE_AGENT_REPO`.
3. Locate the exported contact and/or company CSV files.
4. Count rows and validate expected columns.
5. Do not print raw private CRM rows.
6. Run dry-runs only unless the user explicitly asks for live mode and `$merge-safety-review` passes.
7. Summarize row counts, parse errors, missing IDs, same-ID rows, and risk signals.
