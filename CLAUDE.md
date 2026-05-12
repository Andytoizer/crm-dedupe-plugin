# CRM Dedupe Plugin — Claude Code Guide

This repository packages a Codex plugin, but it is also designed to work cleanly in Claude Code.

Claude Code should treat this repo as an orchestration layer around a separate checkout of the original CRM Dedupe Agent:

```bash
git clone https://github.com/Andytoizer/crm-dedupe-agent ../crm-dedupe-agent
export CRM_DEDUPE_AGENT_REPO=/path/to/crm-dedupe-agent
```

## How To Work Here

- Read this file first, then the relevant file under `skills/*/SKILL.md`.
- Use the `.claude/commands/` slash commands when available.
- Run CRM Dedupe Agent commands from `$CRM_DEDUPE_AGENT_REPO`.
- Keep this plugin repo free of secrets, CRM exports, databases, customer records, and private GTM notes.
- Preserve the original CRM Dedupe Agent scoring contract. The plugin is an orchestration layer, not a replacement scoring engine.
- Keep commands configurable with `CRM_DEDUPE_AGENT_REPO` or `--repo-root`; do not hard-code local machine paths.
- Default to dry-run instructions and require explicit caps before live merge commands.
- Use `$merge-safety-review` before any live CRM write.

## Claude Code Slash Commands

Project commands live in `.claude/commands/`:

- `/crm-dedupe-orchestrator`
- `/contact-dedupe-agent`
- `/company-dedupe-agent`
- `/hubspot-dedupe-backfill`
- `/merge-safety-review`
- `/daily-crm-hygiene`
- `/verify-scoring-contract`

These commands mirror the Codex skills in `skills/`.

## Validation

Run this before publishing changes:

```bash
python3 scripts/verify_original_scoring_contract.py --repo-root "$CRM_DEDUPE_AGENT_REPO"
python3 -m py_compile scripts/company_fallback_summary.py scripts/verify_original_scoring_contract.py
```

Expected scoring verifier output:

```text
OK: original scoring contract preserved
```

## Public Packaging Checklist

- No `.env` files.
- No CSV/TSV exports.
- No database files.
- No local absolute paths.
- No private customer examples.
- `README.md` remains useful for both Codex and Claude Code users.
