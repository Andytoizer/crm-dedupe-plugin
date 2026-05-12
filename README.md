# CRM Dedupe Plugin

A public-ready Codex and Claude Code package for operating the [CRM Dedupe Agent](https://github.com/Andytoizer/crm-dedupe-agent) as focused, reusable agent workflows.

Built by [Andy Toizer](https://www.linkedin.com/in/andy-toizer) — I write [Agent Operator](https://agentoperator.substack.com/), a newsletter about building real systems with coding agents from an operator's seat.

The original dedupe system was built from real RevOps work at [Freckle.io](https://freckle.io/). This repo packages the reusable orchestration layer without shipping private CRM exports, customer records, secrets, or company-specific GTM context.

The original CRM Dedupe Agent owns the CRM integration, deterministic scoring, merge execution, review queue, web enrichment, AI review, Slack digest, and scheduling code. This plugin is the orchestration layer around that repo: it gives Codex and Claude Code smaller, safer roles for running contact dedupe, company dedupe, merge safety review, and daily hygiene.

## What This Package Is

This repo is a packaged agent workflow. It is meant to be cloned, inspected, adapted, and used as a public starting point.

It includes:

- Codex plugin metadata in `.codex-plugin/plugin.json`
- Codex skills in `skills/`
- Claude Code project commands in `.claude/commands/`
- Public-safe helper scripts in `scripts/`
- Packaging docs, `CLAUDE.md`, `.env.example`, and `.gitignore`

It does not include:

- CRM exports
- live customer data
- private GTM notes
- `.env` files or API keys
- databases, logs, or run artifacts

## Skills

- `$crm-dedupe-orchestrator`: routes the dedupe workflow.
- `$contact-dedupe-agent`: owns contact dedupe end to end.
- `$company-dedupe-agent`: owns company dedupe end to end.
- `$hubspot-dedupe-backfill`: validates HubSpot duplicate exports before cleanup.
- `$merge-safety-review`: blocks unsafe live merges.
- `$daily-crm-hygiene`: configures ongoing high-confidence cleanup after backlog work is understood.

## Repository Layout

```text
.claude/commands/
.codex-plugin/plugin.json
skills/
agents/
references/
scripts/
assets/
```

## Universal vs Integration-Specific

This plugin intentionally keeps the original CRM Dedupe Agent's separation between universal logic and integration-specific behavior.

Universal concepts to preserve:

- scoring thresholds and fuzzy caps
- contact and company scoring order
- engagement-weighted master record selection
- review queue routing
- `YES` / `NO` / `UNSURE` review outcomes
- dry-run-first merge safety

Integration-specific pieces live in the original CRM Dedupe Agent repo:

- CRM fetch logic
- CRM merge API calls
- CRM export CSV parsing
- CRM field mapping
- notification channel setup
- credentials and local runtime configuration

If you adapt this for a different CRM, change the integration layer in the original CRM Dedupe Agent repo. Do not rewrite this plugin's scoring guidance into a second source of truth.

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

## Use With Claude Code

This repo includes a `CLAUDE.md` and project slash commands in `.claude/commands/`, so it can also be opened directly in Claude Code.

After cloning this repo and the original CRM Dedupe Agent repo, set:

```bash
export CRM_DEDUPE_AGENT_REPO=/path/to/crm-dedupe-agent
```

Then use the project commands:

- `/crm-dedupe-orchestrator`
- `/contact-dedupe-agent`
- `/company-dedupe-agent`
- `/hubspot-dedupe-backfill`
- `/merge-safety-review`
- `/daily-crm-hygiene`
- `/verify-scoring-contract`

The slash commands mirror the Codex skills and keep Claude Code pointed at the original repo for scoring, AI review, master selection, and merge execution.

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

## Public Packaging Notes

This repo was packaged with the same philosophy as [`cc-package`](https://github.com/Andytoizer/cc-package): keep the reusable workflow, remove private context, and make the repo safe for other people to clone.

Before publishing or forking changes, check:

- no `.env` files
- no CRM exports
- no database files
- no private customer examples
- no local absolute paths
- scoring verifier still passes

## License

MIT — use it, fork it, improve it. If you build something cool, let me know.

## Links

- [Original CRM Dedupe Agent](https://github.com/Andytoizer/crm-dedupe-agent)
- [Andy Toizer on LinkedIn](https://www.linkedin.com/in/andy-toizer)
- [Agent Operator](https://agentoperator.substack.com/)
