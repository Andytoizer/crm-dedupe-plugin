---
description: Run company dedupe end to end. Validates exports, scores companies, adds web evidence, routes AI review, and runs approved capped merges.
allowed-tools: ["Skill", "Bash", "Read", "Glob", "Grep"]
---

# Company Dedupe Agent

**First action: invoke the `company-dedupe-agent` skill via the Skill tool** so the full SKILL.md instructions load. Pass the user's arguments to it.

User arguments:

```text
$ARGUMENTS
```

Workflow guidance (the skill will refine this):

1. Engine code lives at `${CLAUDE_PLUGIN_ROOT}` — `cd` there before running any Python commands.
2. Confirm the company export path. If the user staged a demo file, look at `${CLAUDE_PLUGIN_ROOT}/demo_exports/companies_prechecked.csv`.
3. Validate expected columns without printing private company rows.
4. Run dry-run commands before any live command.
5. Use `pipeline.scorer.score_companies()` and `pipeline.web_enricher.check_same_company()`.
6. Route medium, low, and unknown web buckets through the bundled AI review path before calling them human-review cases.
7. Invoke the `merge-safety-review` skill before live mode.
8. Require explicit approval and an explicit `--max-merges` cap for live mode.

Preserve:

- domain exact `1.0`
- LinkedIn company page `0.98`
- fuzzy company name capped below auto-merge
- `YES` / `NO` / `UNSURE` review outcomes
