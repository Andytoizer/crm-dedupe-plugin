Use this command before any live CRM write.

Arguments from the user:

```text
$ARGUMENTS
```

Workflow:

1. Read `skills/merge-safety-review/SKILL.md`.
2. Confirm a successful dry-run happened in the same session.
3. Confirm the live command has an explicit cap.
4. Confirm export path, IDs, same-ID checks, and risk rows.
5. Confirm different contact emails/names or company domains were reviewed.
6. Confirm original repo scoring and `select_master()` were used.
7. Confirm credentials exist but do not print them.
8. Stop if the user has not explicitly approved live mode.

Output:

- `APPROVED FOR LIVE` only if all conditions pass.
- Otherwise return `STOP` with the reasons.
