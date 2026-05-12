Use this command to orchestrate a CRM dedupe session.

Arguments from the user:

```text
$ARGUMENTS
```

Workflow:

1. Read `skills/crm-dedupe-orchestrator/SKILL.md`.
2. Work from this repo root unless the user explicitly provides another path.
3. Identify whether the user is asking about contacts, companies, both, backfill exports, safety review, or daily hygiene.
4. Route contact work through `skills/contact-dedupe-agent/SKILL.md`.
5. Route company work through `skills/company-dedupe-agent/SKILL.md`.
6. Use `skills/merge-safety-review/SKILL.md` before any live CRM write.
7. Keep the bundled scoring contract intact. Do not invent alternate scoring.
8. Default to dry-run. Live commands require explicit user approval and an explicit cap.

Output:

- Summarize the intended scope.
- Name the exact repo path and files involved.
- Provide or run the safe dry-run commands.
- Report counts and risk signals without printing raw private CRM rows.
