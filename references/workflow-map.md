# CRM Dedupe Workflow Map

## Engine Layer

This standalone repo contains the engine pieces:

- `review/merge_from_csv.py`: one-off HubSpot duplicate export backfill.
- `pipeline/scorer.py`: deterministic contact and company scoring, including thresholds, fuzzy caps, and master record selection.
- `pipeline/blocker.py`: candidate pair generation.
- `pipeline/web_enricher.py`: company domain fallback research.
- `review/ai_review.py`: fast rules, web research, and Claude review.
- `review/slack_digest.py`: human review digest.
- `agents/incremental_dedup_agent.py`: scheduled incremental cleanup.
- `scheduler/register_schedule.py`: scheduled task definitions.

## Plugin Orchestrator Workflow

The plugin splits the work by orchestration decision:

1. Export and validate the duplicate backlog.
2. Route contact records to the contact dedupe agent for end-to-end contact ownership.
3. Route company records to the company dedupe agent for end-to-end company ownership.
4. Review merge safety before any live write.
5. Schedule daily high-confidence cleanup.

## Why Pluginize

- Smaller context windows per task.
- Fewer accidental cross-task assumptions.
- Better prompts for non-engineer operators.
- Easier handoffs between "inspect", "approve", and "automate" phases.
- Safer live operations because each skill has a narrow blast radius.
- Preservation of the bundled scoring contract: high-confidence matches can be merged, clear non-duplicates can be suppressed, and only genuinely uncertain cases need human eyes.

## Demo Principle

The audience should see Codex as the operating layer:

```text
I exported HubSpot duplicates. Dry-run the first 25 contacts. Do not make live changes. Tell me what looks risky.
```

The human gives the intent. The orchestrator routes the work to the right specialist skill.

## Important Guardrail

The plugin must not turn the AI review loop into a manual-only company investigation step.

Bundled engine behavior:

```text
Score >= 0.95 -> auto-merge candidate
0.70 <= score < 0.95 -> review queue
Score < 0.70 -> discard
AI review YES -> merge
AI review NO -> suppress pair
AI review UNSURE -> Slack/manual review
```

The company dedupe agent can add web evidence and make the routing visible, but it should not final-route every `DIFFERENT_MEDIUM`, `UNKNOWN_LOW`, or `SAME_LOW` web bucket to human review before Claude has a chance to reason over the evidence.

See `references/original-scoring-contract.md` for the exact scoring priorities the plugin agents must preserve.
