Use this command to configure or review ongoing CRM dedupe hygiene.

Arguments from the user:

```text
$ARGUMENTS
```

Workflow:

1. Read `skills/daily-crm-hygiene/SKILL.md`.
2. Work from this repo root.
3. Confirm the backlog cleanup path is understood before scheduling ongoing cleanup.
4. Preserve the original incremental agent, review queue, AI review, Slack digest, and scoring thresholds.
5. Auto-merge only high-confidence deterministic matches.
6. Route fuzzy or uncertain matches through AI review.
7. Send only `UNSURE` cases to human review/digest.

Output:

- Proposed cadence.
- Commands or setup steps.
- Safety assumptions.
- Expected daily summary fields: merged, flagged, skipped, errored.
