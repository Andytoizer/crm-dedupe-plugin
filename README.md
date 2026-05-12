# CRM Dedupe Plugin

A standalone Codex and Claude Code plugin for finding, reviewing, and safely merging duplicate CRM contacts and companies.

Built by [Andy Toizer](https://www.linkedin.com/in/andy-toizer) — I write [Agent Operator](https://agentoperator.substack.com/), a newsletter about building real systems with coding agents from an operator's seat.

This started from real RevOps work at [Freckle.io](https://freckle.io/) and is packaged so other people can use, fork, and adapt it without private CRM exports, customer records, secrets, or company-specific GTM context.

## What It Does

- Finds duplicate contacts and companies.
- Auto-merges high-confidence matches.
- Routes fuzzy matches through AI review.
- Picks the surviving master record using engagement-weighted scoring.
- Writes an audit log for merge decisions.
- Sends or prepares review digests for cases that still need human eyes.
- Gives Codex and Claude Code one orchestrator that routes the focused dedupe, safety, and hygiene steps for you.

## Install The Plugin

In Codex, install this plugin from the Git URL:

```text
https://github.com/Andytoizer/crm-dedupe-plugin
```

Then start with the orchestrator:

```text
Use $crm-dedupe-orchestrator to clean up my HubSpot duplicate backlog safely.
```

## Use With Claude Code

Install the plugin globally so the commands work in any Claude Code session:

```text
/plugin marketplace add Andytoizer/crm-dedupe-plugin
/plugin install crm-dedupe@crm-dedupe-plugin
```

You'll get these slash commands everywhere:

- `/crm-dedupe-orchestrator` — main entry point
- `/contact-dedupe-agent`, `/company-dedupe-agent`
- `/hubspot-dedupe-backfill`, `/merge-safety-review`
- `/daily-crm-hygiene`, `/verify-scoring-contract`

Plus the six bundled skills the orchestrator routes through.

You can also install from a local clone instead of GitHub:

```bash
git clone https://github.com/Andytoizer/crm-dedupe-plugin
```

```text
/plugin marketplace add /absolute/path/to/crm-dedupe-plugin
/plugin install crm-dedupe@crm-dedupe-plugin
```

Or just clone and open the repo in Claude Code without installing. The plugin commands live in `commands/`, and the Claude Code plugin metadata lives in `.claude-plugin/`.

The orchestrator routes contact, company, backfill, merge safety, and daily hygiene workflows for you, so most users should not need to pick a lower-level command directly.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your CRM and AI credentials.

Run the safety checks:

```bash
python3 scripts/verify_original_scoring_contract.py
python3 -m pytest tests/ -q
```

Run a dry-run first:

```bash
python3 agents/bulk_dedup_agent.py --limit 500
```

Start small when going live:

```bash
python3 agents/bulk_dedup_agent.py --live --max-merges 10
```

## Main Entry Point

Use `$crm-dedupe-orchestrator` in Codex or `/crm-dedupe-orchestrator` in Claude Code. It will validate exports, route contact and company work, run merge-safety checks before live writes, and set up daily hygiene only after the backlog workflow is understood.

## Repository Layout

```text
.claude-plugin/           Claude Code plugin + marketplace manifests
.codex-plugin/            Codex plugin manifest
commands/                 Claude Code plugin slash commands
skills/                   Skill instructions (shared between Codex and Claude Code)
agents/                   bulk and incremental dedupe agents
config/                   environment and field settings
db/                       SQLite models and session setup
pipeline/                 blocking, scoring, fetching, merging, web enrichment
review/                   AI review, queue actions, Slack digest, CSV merge
scheduler/                schedule registration helper
tests/                    scoring and blocking tests
references/               workflow and scoring contract notes
scripts/                  packaging/helper checks
assets/                   plugin icon and logo
```

## Universal vs Integration-Specific

Universal logic to preserve:

- scoring thresholds and fuzzy caps
- contact and company scoring order
- engagement-weighted master record selection
- review queue routing
- `YES` / `NO` / `UNSURE` review outcomes
- dry-run-first merge safety

HubSpot-specific pieces to adapt for another CRM:

- `pipeline/fetcher.py`
- `pipeline/merger.py`
- `config/settings.py`
- `review/merge_from_csv.py` (HubSpot CSV parsing, but it must preserve score -> AI/web review routing)
- `review/preview_merges.py`

The integration files are marked with headers explaining what to change and what to preserve.

## Scoring Contract

- `AUTO_MERGE_THRESHOLD = 0.95`
- `REVIEW_THRESHOLD = 0.70`
- exact contact email/domain signals can auto-merge
- fuzzy matches are capped below auto-merge and route to review
- `YES` / `NO` / `UNSURE` review outcomes come from the review path
- HubSpot duplicate exports are candidate pairs, not proof; CSV backfills must not stamp every row as `AUTO_MERGE`

Verify it:

```bash
python3 scripts/verify_original_scoring_contract.py
```

Expected output:

```text
OK: original scoring contract preserved
```

## Safety Model

- Dry-run before live mode.
- Use explicit live caps.
- Never print secrets or raw private CRM rows.
- Keep scoring, master selection, and merge execution intact.
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

- [Andy Toizer on LinkedIn](https://www.linkedin.com/in/andy-toizer)
- [Agent Operator](https://agentoperator.substack.com/)
- [Freckle.io](https://freckle.io/)
