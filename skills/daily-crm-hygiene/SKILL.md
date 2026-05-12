---
name: daily-crm-hygiene
description: Configure daily live CRM dedupe for high-confidence matches, with fuzzy or uncertain matches routed through AI review and only UNSURE cases sent to humans.
---

# Daily CRM Hygiene

Use this after the one-off backlog cleanup is understood. Clears today's duplicate backlog once, then keeps it from returning via an incremental agent.

The plugin engine lives at `${CLAUDE_PLUGIN_ROOT}`.

## First Response

Acknowledge the request in one sentence. Then act. Never go silent.

## Cadence

Default: daily.

The daily agent should:

- Fetch records modified since the last checkpoint.
- Auto-merge only high-confidence matches according to the bundled thresholds.
- Queue fuzzy or uncertain matches for AI review.
- Run AI review for ambiguous cases.
- Send a Slack digest of review items.

## Repo Touchpoints (inside `${CLAUDE_PLUGIN_ROOT}`)

- `agents/incremental_dedup_agent.py`
- `review/ai_review.py`
- `review/slack_digest.py`
- `scheduler/register_schedule.py`
- `pipeline/scorer.py`

## Scoring Contract

Daily hygiene must use the bundled scoring contract:

- contacts: email exact `1.0`, Gmail dots `0.97`, LinkedIn `0.98`, phone `0.92`, fuzzy capped at `0.89`
- companies: domain exact `1.0`, LinkedIn company page `0.98`, fuzzy name capped at `0.89`
- `>= 0.95` auto-merge candidate
- `0.70-0.95` review queue
- `< 0.70` discard

## Safety

- Daily live mode is acceptable only for high-confidence deterministic matches.
- Fuzzy cases enter the review queue.
- Company ambiguity should use web fallback, then Claude reasoning, then human review only for `UNSURE`.
- Summaries should report merged, flagged, skipped, and errored counts.

## Framing for the User

```text
First I clear the pile. Then I turn on the daily agent so the pile does not come back. High-confidence duplicates are fixed automatically, and messy cases go to review.
```
