---
description: Validate HubSpot duplicate export files and prepare a one-off CRM dedupe backlog cleanup without making live changes.
allowed-tools: ["Skill", "Bash", "Read", "Glob", "Grep"]
---

# HubSpot Dedupe Backfill

**First action: invoke the `hubspot-dedupe-backfill` skill via the Skill tool** so the full SKILL.md instructions load. Pass the user's arguments to it.

User arguments:

```text
$ARGUMENTS
```

Workflow guidance (the skill will refine this):

1. Engine code lives at `${CLAUDE_PLUGIN_ROOT}` — `cd` there before running any Python commands.
2. Locate the exported contact and/or company CSV files. Common paths: `~/Downloads/`, the user's project dir, or `${CLAUDE_PLUGIN_ROOT}/demo_exports/`.
3. Count rows and validate expected columns.
4. Never print raw private CRM rows.
5. Run full-pipeline dry-runs only unless the user explicitly asks for live mode and the `merge-safety-review` skill passes.
6. Confirm `review/merge_from_csv.py` scored each pair and routed `REVIEW` rows through AI/web review in the same command.
7. Summarize row counts, parse errors, missing IDs, same-ID rows, scorer decisions, AI decisions, and true human-review residue.
