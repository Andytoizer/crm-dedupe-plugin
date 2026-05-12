Use this command for contact dedupe end to end.

Arguments from the user:

```text
$ARGUMENTS
```

Workflow:

1. Read `skills/contact-dedupe-agent/SKILL.md`.
2. Work from this repo root.
3. Confirm the contact export path or use `demo_exports/contacts_prechecked.csv` if the user staged it there.
4. Validate expected columns without printing private contact rows.
5. Run dry-run commands before any live command.
6. Flag missing IDs, same-ID rows, different populated emails, and different names.
7. Use `skills/merge-safety-review/SKILL.md` before live mode.
8. Require explicit approval and an explicit cap for live mode.

Preserve:

- `score_contacts()`
- `select_master()`
- `AUTO_MERGE_THRESHOLD = 0.95`
- `REVIEW_THRESHOLD = 0.70`
- fuzzy contact scores capped below auto-merge
