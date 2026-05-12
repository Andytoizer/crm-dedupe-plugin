# CRM Dedupe Plugin

Codex plugin that turns the original [CRM Dedupe Agent](https://github.com/Andytoizer/crm-dedupe-agent) workflow into focused, reusable skills.

The original project owns the CRM integration, deterministic scoring, merge execution, review queue, web enrichment, AI review, Slack digest, and scheduling code. This plugin is the orchestration layer around that repo: it gives Codex smaller, safer roles for running contact dedupe, company dedupe, merge safety review, and daily hygiene.

## Skills

- `$crm-dedupe-orchestrator`: routes the dedupe workflow.
- `$contact-dedupe-agent`: owns contact dedupe end to end.
- `$company-dedupe-agent`: owns company dedupe end to end.
- `$hubspot-dedupe-backfill`: validates HubSpot duplicate exports before cleanup.
- `$merge-safety-review`: blocks unsafe live merges.
- `$daily-crm-hygiene`: configures ongoing high-confidence cleanup after backlog work is understood.

## Repository Layout

```text
.codex-plugin/plugin.json
skills/
agents/
references/
scripts/
assets/
```

## Requirements

This plugin expects the CRM Dedupe Agent repo to be available locally:

```bash
git clone https://github.com/Andytoizer/crm-dedupe-agent ../crm-dedupe-agent
```

Set the repo path when running helper scripts:

```bash
export CRM_DEDUPE_AGENT_REPO=/path/to/crm-dedupe-agent
```

The CRM Dedupe Agent repo itself is responsible for CRM credentials such as `HUBSPOT_ACCESS_TOKEN`, `ANTHROPIC_API_KEY`, and Slack settings. Do not store secrets in this plugin repo.

## Install As A Local Codex Plugin

Add this repo to a Codex marketplace file with a local source path:

```json
{
  "name": "crm-dedupe-plugin",
  "source": {
    "source": "local",
    "path": "./crm-dedupe-plugin"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_USE"
  },
  "category": "Productivity"
}
```

## Verify The Scoring Contract

The plugin must not invent replacement dedupe scoring. It preserves the original repo behavior:

- `AUTO_MERGE_THRESHOLD = 0.95`
- `REVIEW_THRESHOLD = 0.70`
- exact contact email/domain signals can auto-merge
- fuzzy matches are capped below auto-merge and route to review
- `YES` / `NO` / `UNSURE` review outcomes come from the original review path

Run:

```bash
python3 scripts/verify_original_scoring_contract.py --repo-root "$CRM_DEDUPE_AGENT_REPO"
```

Expected output:

```text
OK: original scoring contract preserved
```

## Safety Model

- Dry-run before live mode.
- Use explicit live caps.
- Never print secrets or raw private CRM rows.
- Keep original repo scoring, master selection, and merge execution intact.
- Use `$merge-safety-review` before any live CRM write.

## License

MIT
