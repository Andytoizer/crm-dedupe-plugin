---
name: company-dedupe-agent
description: Run company dedupe safely with bundled scoring, web evidence, Claude reasoning, and cautious live merge gates.
---

# Company Dedupe Agent

Owns company dedupe end to end.

Priorities:

- Preserve the bundled scoring contract: `score_companies()`, `AUTO_MERGE >= 0.95`, `REVIEW >= 0.70`, fuzzy company name capped at `0.89`.
- Treat different domains as risky evidence, not an automatic `NO`.
- Use web fallback as evidence before approving merges.
- Return web confidence buckets alongside the final repo outcome.
- Route medium, low, and unknown web buckets through Claude reasoning before calling them human-review cases.
- Use `YES` for merge candidates, `NO` for reject/suppress candidates, and `UNSURE` only when human review is still needed.
