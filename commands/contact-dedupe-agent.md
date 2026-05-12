---
description: Run contact dedupe end to end. Validates exports, scores contacts, dry-runs, reviews risk, and runs approved capped merges.
allowed-tools: ["Skill", "Bash", "Read", "Glob", "Grep"]
---

# Contact Dedupe Agent

**First action: invoke the `contact-dedupe-agent` skill via the Skill tool** so the full SKILL.md instructions load. Pass the user's arguments to it.

User arguments:

```text
$ARGUMENTS
```

Workflow guidance (the skill will refine this):

1. Engine code lives at `${CLAUDE_PLUGIN_ROOT}` — `cd` there before running any Python commands.
2. Confirm the contact export path. If the user staged a demo file, look at `${CLAUDE_PLUGIN_ROOT}/demo_exports/contacts_prechecked.csv`.
3. Validate expected columns without printing private contact rows.
4. Run full-pipeline dry-run commands before any live command.
5. Use `review/merge_from_csv.py` for CSV backfills so each pair is scored with `score_contacts()` and scorer `REVIEW` rows go through AI review in the same command.
6. Flag missing IDs, same-ID rows, different populated emails, different names, AI `NO`, and AI `UNSURE`.
7. Invoke the `merge-safety-review` skill before live mode.
8. Require explicit approval and an explicit `--max-merges` cap for live mode.

Preserve:

- `score_contacts()`
- `select_master()`
- `AUTO_MERGE_THRESHOLD = 0.95`
- `REVIEW_THRESHOLD = 0.70`
- fuzzy contact scores capped below auto-merge
