---
name: company-dedupe-agent
description: Own company dedupe end to end: validate exports, score companies, add web evidence, route AI review, and run approved capped merges.
---

# Company Dedupe Agent

Use this before live-merging company duplicate exports, especially when domains differ.

This is an entity-owned agent. It owns company dedupe end to end, not just investigation.

## Why This Exists

Company merges are riskier than contact merges. Different domains can mean subsidiaries, rebrands, acquired companies, old domains, or completely different companies.

This skill must preserve the bundled workflow. It is not a replacement
for AI review. The intended company path is:

```text
score pair -> review queue -> fast CRM rules -> web research -> Claude reasoning -> YES / NO / UNSURE
```

Only `UNSURE` is a true human-review outcome. `NO` is an agent decision to reject
or suppress the pair, and `YES` is an agent decision to merge after the operator's
approved live scope.

## Workflow

1. Confirm company CSV exists.
2. Change into this repo root before running commands.
3. Validate expected company columns and count rows without printing private row data.
4. Dry-run the capped batch to verify the export is parseable.
5. Scan risk signals:
   - different populated domains
   - different names
   - missing domains
   - same HubSpot IDs
6. Score company pairs with `pipeline.scorer.score_companies()`. Domain exact is `1.0`, LinkedIn company page exact is `0.98`, and fuzzy company name is capped at `0.89`.
7. For risky pairs, use `pipeline.web_enricher.check_same_company()` as evidence, then route through the repo's AI review logic when the web result is not high-confidence.
8. Separate results into original-repo outcomes:
   - `YES`: merge candidate after operator-approved live scope.
   - `NO`: reject/suppress as known non-duplicate.
   - `UNSURE`: true human review.
9. Use `$merge-safety-review` before live mode.
10. For display, keep the web-evidence bucket too (`SAME_HIGH`, `DIFFERENT_HIGH`, `DIFFERENT_MEDIUM`, `UNKNOWN_LOW`, etc.), but do not treat every medium/low/unknown web bucket as final manual intervention.
11. Never live-merge the whole company batch just because HubSpot exported it.

## Web Evidence Routing

Web fallback buckets are useful evidence, but they are not all final decisions:

- `SAME_HIGH` should become a merge candidate.
- `DIFFERENT_HIGH` should become a reject/suppress candidate.
- `DIFFERENT_MEDIUM`, `UNKNOWN_LOW`, and `SAME_LOW` should continue to Claude reasoning before they are called true human-review cases.

Example: two records can have different canonical domains but matching page title, site name, phone, or redirect evidence. The AI step should reason over that mixed evidence instead of forcing manual review by default.

## Output

Return a compact table with:

- row number
- company/domain pair
- web-evidence bucket
- AI/repo outcome (`YES`, `NO`, or `UNSURE`) when available
- evidence summary
- recommended action

Do not print private company details unless the operator explicitly asks.

## Commands

```bash
cd /path/to/crm-dedupe-plugin
python3 review/merge_from_csv.py --companies demo_exports/companies_prechecked.csv --limit 25
python3 review/ai_review.py --type company --limit 25
python3 scripts/company_fallback_summary.py demo_exports/companies_prechecked.csv --limit 25
python3 review/merge_from_csv.py --companies demo_exports/companies_prechecked.csv --live --limit 25
```
