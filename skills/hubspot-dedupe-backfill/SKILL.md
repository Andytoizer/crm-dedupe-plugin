---
name: hubspot-dedupe-backfill
description: Validate HubSpot duplicate export files and prepare a one-off CRM dedupe backlog cleanup without making live changes.
---

# HubSpot Dedupe Backfill

Use this when the operator has exported duplicate contacts or companies from HubSpot and wants to prepare a safe one-off cleanup.

The plugin engine lives at `${CLAUDE_PLUGIN_ROOT}`.

## First Response

Acknowledge the request in one sentence. Then act. Never go silent.

## Inputs

- HubSpot duplicate contact CSV.
- HubSpot duplicate company CSV.
- Optional HubSpot property list CSVs.

## Locating Exports

1. Use the paths the user named, if any.
2. Otherwise check `${CLAUDE_PLUGIN_ROOT}/demo_exports/`.
3. Otherwise check `~/Downloads/` for recent HubSpot exports.
4. **If not found, ASK the user** for absolute paths.

## Workflow

1. `cd ${CLAUDE_PLUGIN_ROOT}` before running commands.
2. Locate export files (or confirm paths with user).
3. Optionally copy or reference them under `${CLAUDE_PLUGIN_ROOT}/demo_exports/` with stable names:
   - `contacts_prechecked.csv`
   - `companies_prechecked.csv`
4. Count rows without printing sensitive row data.
5. Validate expected columns:
   - Contacts: `ID_1`, `ID_2`, `FIRSTNAME_1`, `FIRSTNAME_2`, `EMAIL_1`, `EMAIL_2`
   - Companies: `ID_1`, `ID_2`, `NAME_1`, `NAME_2`, `DOMAIN_1`, `DOMAIN_2`
6. Run dry-runs only.
7. Summarize row counts, parse errors, missing IDs, same-ID rows, and obvious risk signals.
8. Confirm the summary used bundled scoring, master selection, and merge execution path.

## Commands

```bash
cd "${CLAUDE_PLUGIN_ROOT}"
python3 review/merge_from_csv.py --contacts <path-to-contacts-csv> --limit 25
python3 review/merge_from_csv.py --companies <path-to-companies-csv> --limit 25
```

Substitute `<path-to-...-csv>` with the user's actual file paths.

## Output

- Export file paths.
- Total duplicate rows.
- Dry-run result counts.
- Risk rows by number only, not raw contact/company details.
- Next recommended action.
