---
description: Pre-flight gate before any live CRM merge write. Checks dry-run status, caps, credentials, audit logging, and risk signals.
allowed-tools: ["Skill", "Bash", "Read", "Glob", "Grep"]
---

# Merge Safety Review

**First action: invoke the `merge-safety-review` skill via the Skill tool** so the full SKILL.md instructions load. Pass the user's arguments to it.

User arguments:

```text
$ARGUMENTS
```

Workflow guidance (the skill will refine this):

1. Confirm a successful dry-run happened in the same session.
2. Confirm the live command has an explicit `--max-merges` cap.
3. Confirm export path, IDs, same-ID checks, and risk rows.
4. Confirm different contact emails/names or company domains were reviewed.
5. Confirm bundled scoring and `select_master()` were used.
6. Confirm credentials exist but never print them.
7. Stop if the user has not explicitly approved live mode in this session.

Output:

- `APPROVED FOR LIVE` only if all conditions pass.
- Otherwise return `STOP` with the reasons.
