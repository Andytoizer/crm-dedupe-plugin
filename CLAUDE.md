# CLAUDE.md

This repo packages a Codex plugin for orchestrating CRM dedupe workflows.

## Rules

- Do not add secrets, CRM exports, customer records, database files, or private GTM notes.
- Preserve the original CRM Dedupe Agent scoring contract. The plugin is an orchestration layer, not a replacement scoring engine.
- Keep commands configurable with `CRM_DEDUPE_AGENT_REPO` or `--repo-root`; do not hard-code local machine paths.
- Default to dry-run instructions and require explicit caps before live merge commands.
- Use `$merge-safety-review` before any live CRM write.

## Public Packaging Checklist

- No `.env` files.
- No CSV exports.
- No local absolute paths.
- No private customer examples.
- `python3 scripts/verify_original_scoring_contract.py --repo-root <crm-dedupe-agent>` passes.
