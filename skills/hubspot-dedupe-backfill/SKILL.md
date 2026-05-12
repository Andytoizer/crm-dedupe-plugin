---
name: hubspot-dedupe-backfill
description: Validate HubSpot duplicate export files and prepare a one-off CRM dedupe backlog cleanup without making live changes.
---

# HubSpot Dedupe Backfill

Use this when the operator has exported duplicate contacts or companies from HubSpot and wants to prepare a safe one-off cleanup.

## Inputs

- HubSpot duplicate contact CSV.
- HubSpot duplicate company CSV.
- Optional HubSpot property list CSVs.
- Repo path for the CRM Dedupe Agent.

## Workflow

1. Locate the CRM Dedupe Agent repo and run commands from that repo root.
2. Locate export files.
3. Copy or reference them under `demo_exports/` with stable names:
   - `contacts_prechecked.csv`
   - `companies_prechecked.csv`
4. Count rows without printing sensitive row data.
5. Validate expected columns:
   - Contacts: `ID_1`, `ID_2`, `FIRSTNAME_1`, `FIRSTNAME_2`, `EMAIL_1`, `EMAIL_2`
   - Companies: `ID_1`, `ID_2`, `NAME_1`, `NAME_2`, `DOMAIN_1`, `DOMAIN_2`
6. Run dry-runs only.
7. Summarize row counts, parse errors, missing IDs, same-ID rows, and obvious risk signals.
8. Confirm the summary used the original repo scoring, master selection, and merge execution path.

## Commands

Use the repo's existing scripts rather than duplicating logic:

```bash
cd "$CRM_DEDUPE_AGENT_REPO"
python3 review/merge_from_csv.py --contacts demo_exports/contacts_prechecked.csv --limit 25
python3 review/merge_from_csv.py --companies demo_exports/companies_prechecked.csv --limit 25
```

## Output

Return:

- Export file paths.
- Total duplicate rows.
- Dry-run result counts.
- Risk rows by number only, not raw contact/company details.
- Next recommended action.
