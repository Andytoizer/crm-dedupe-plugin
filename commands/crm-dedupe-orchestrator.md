---
description: Orchestrate a guarded CRM dedupe session — routes contact, company, backfill, merge safety, and daily hygiene workflows.
allowed-tools: ["Skill", "Bash", "Read", "Glob", "Grep"]
---

# CRM Dedupe Orchestrator

Top-level entry point for a CRM dedupe session. Routes the user's request to the focused dedupe, safety, and hygiene skills.

**First action: invoke the `crm-dedupe-orchestrator` skill via the Skill tool** so the full SKILL.md instructions load. Pass the user's arguments to it.

User arguments:

```text
$ARGUMENTS
```

Routing guidance (the skill will refine this):

1. Identify whether the user is asking about contacts, companies, both, backfill exports, safety review, or daily hygiene.
2. Route contact work through the `contact-dedupe-agent` skill.
3. Route company work through the `company-dedupe-agent` skill.
4. Use the `merge-safety-review` skill before any live CRM write.
5. Use the `hubspot-dedupe-backfill` skill for one-off CSV-based backlogs.
6. Use the `daily-crm-hygiene` skill only after the backlog workflow is understood.

Engine code lives at `${CLAUDE_PLUGIN_ROOT}` — `cd` there before running any Python commands.

Hard rules:

- Keep the bundled scoring contract intact. Do not invent alternate scoring.
- Default to dry-run. Live commands require explicit user approval and an explicit `--max-merges` cap.
- Never print raw private CRM rows.

Output:

- Summarize the intended scope.
- Name the exact files and commands involved.
- Provide or run the safe dry-run commands.
- Report counts and risk signals without printing raw private CRM rows.
