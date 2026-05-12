---
description: Orchestrate a guarded CRM dedupe session. Routes contact, company, backfill, merge safety, and daily hygiene workflows.
allowed-tools: ["Skill", "Bash", "Read", "Glob", "Grep"]
---

# CRM Dedupe Orchestrator

Top-level entry point for a CRM dedupe session. Owns the requested workflow end to end and uses focused dedupe, safety, and hygiene skills as helpers when useful.

**First action: invoke the `crm-dedupe-orchestrator` skill via the Skill tool** so the full SKILL.md instructions load. Pass the user's arguments to it.

User arguments:

```text
$ARGUMENTS
```

Ownership guidance (the skill will refine this):

1. Identify whether the user is asking about contacts, companies, both, backfill exports, safety review, or daily hygiene.
2. For CSV backfills, locate files and run the full pipeline yourself; do not just route and stop.
3. Use contact/company/backfill skills for detailed guidance, then continue orchestration.
4. Use the `merge-safety-review` skill before any live CRM write.
5. Use the `daily-crm-hygiene` skill only after the backlog workflow is understood.

Engine code lives at `${CLAUDE_PLUGIN_ROOT}` — `cd` there before running any Python commands.

Hard rules:

- Keep the bundled scoring contract intact. Do not invent alternate scoring.
- Default to dry-run. Live commands require explicit user approval and an explicit `--max-merges` cap.
- Never print raw private CRM rows.
- CSV backfills must use the full score plus AI/web review path. Do not treat HubSpot's duplicate export as an automatic merge verdict.
- For requests covering both contacts and companies, run both dry-runs and return one combined summary.

Output:

- Summarize the intended scope.
- Name the exact files and commands involved.
- Provide or run the safe full-pipeline dry-run commands.
- Report scorer auto-merge, AI YES, AI NO, AI UNSURE, discard counts, and risk signals without printing raw private CRM rows.
