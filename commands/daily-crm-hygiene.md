---
description: Configure daily live CRM dedupe for high-confidence matches, with fuzzy or uncertain matches routed through AI review and only UNSURE cases sent to humans.
allowed-tools: ["Skill", "Bash", "Read", "Glob", "Grep"]
---

# Daily CRM Hygiene

**First action: invoke the `daily-crm-hygiene` skill via the Skill tool** so the full SKILL.md instructions load. Pass the user's arguments to it.

User arguments:

```text
$ARGUMENTS
```

Workflow guidance (the skill will refine this):

1. Engine code lives at `${CLAUDE_PLUGIN_ROOT}` — `cd` there before running any Python commands.
2. Confirm the backlog cleanup path is understood before scheduling ongoing cleanup.
3. Preserve the original incremental agent, review queue, AI review, Slack digest, and scoring thresholds.
4. Auto-merge only high-confidence deterministic matches.
5. Route fuzzy or uncertain matches through AI review.
6. Send only `UNSURE` cases to human review/digest.

Output:

- Proposed cadence.
- Commands or setup steps.
- Safety assumptions.
- Expected daily summary fields: merged, flagged, skipped, errored.
