# Original Scoring Contract

The plugin agents must preserve the CRM Dedupe scoring and routing contract bundled in this repo.

## Thresholds

- `AUTO_MERGE_THRESHOLD = 0.95`
- `REVIEW_THRESHOLD = 0.70`
- Score `< 0.70` is discarded.
- Score `>= 0.70` and `< 0.95` enters the review queue.
- Score `>= 0.95` may auto-merge, subject to dry-run, caps, and approval rules.

## Contact Scoring

Use `pipeline.scorer.score_contacts()` from the CRM Dedupe Agent repo. Do not re-score contacts inside the plugin.

Priority:

1. Normalized exact email: `1.0`
2. Gmail dot-insensitive email near-match: `0.97`
3. Normalized LinkedIn profile slug match: `0.98`
4. Digits-only phone match: `0.92`
5. Fuzzy first name + last name + company: capped at `0.89`, so it cannot auto-merge by itself.

Fuzzy contact matching requires both first and last names, requires first-name similarity of at least `0.50`, strips generic company names, and routes qualifying fuzzy matches to review rather than direct merge.

## Company Scoring

Use `pipeline.scorer.score_companies()` from the CRM Dedupe Agent repo. Do not re-score companies inside the plugin.

Priority:

1. Normalized exact domain or website host: `1.0`
2. Normalized LinkedIn company page match: `0.98`
3. Fuzzy company name after legal suffix stripping: capped at `0.89`, so it cannot auto-merge by itself.

Different domains do not automatically mean different companies. They move the pair into the review path unless the original scorer produced an auto-merge signal.

## Review Routing

Use the bundled queue and review flow:

```text
score pair -> AUTO_MERGE / REVIEW / DISCARD
REVIEW -> fast CRM rules -> web research for companies -> Claude reasoning
YES -> merge
NO -> reject and suppress known non-duplicate pair
UNSURE -> leave for manual review / Slack digest
```

Company web evidence buckets are not final outcomes. `SAME_HIGH` and `DIFFERENT_HIGH` can decide in the web step. Medium, low, and unknown web buckets are evidence for Claude reasoning before any human-review label.

## Master Selection

Use `pipeline.scorer.select_master()` from the CRM Dedupe Agent repo. Master selection is engagement-weighted:

- notes, sends, populated fields, email, LinkedIn, and phone add completeness points
- older records get a small history bonus
- deals, replies, opens/clicks, recent sales activity, and recent contact activity add engagement points
- records with engagement activity receive a multiplier

The plugin should never pick a master with a simpler "newer wins" or "first CSV row wins" rule.
