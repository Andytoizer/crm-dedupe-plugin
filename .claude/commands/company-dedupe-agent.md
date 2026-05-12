Use this command for company dedupe end to end.

Arguments from the user:

```text
$ARGUMENTS
```

Workflow:

1. Read `skills/company-dedupe-agent/SKILL.md`.
2. Work from `$CRM_DEDUPE_AGENT_REPO`.
3. Confirm the company export path or use `demo_exports/companies_prechecked.csv` if the user staged it there.
4. Validate expected columns without printing private company rows.
5. Run dry-run commands before any live command.
6. Use `pipeline.scorer.score_companies()` and `pipeline.web_enricher.check_same_company()` from the original repo.
7. Route medium, low, and unknown web buckets through the original AI review path before calling them human-review cases.
8. Use `skills/merge-safety-review/SKILL.md` before live mode.
9. Require explicit approval and an explicit cap for live mode.

Preserve:

- domain exact `1.0`
- LinkedIn company page `0.98`
- fuzzy company name capped below auto-merge
- `YES` / `NO` / `UNSURE` review outcomes
