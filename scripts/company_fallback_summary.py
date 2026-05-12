#!/usr/bin/env python3
"""Summarize web-fallback verdicts for a capped company duplicate export."""

import argparse
import csv
import os
import sys
from pathlib import Path


def _default_repo_root() -> Path:
    return Path(os.getenv("CRM_DEDUPE_AGENT_REPO", Path.cwd()))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--repo-root", type=Path, default=_default_repo_root())
    args = parser.parse_args()

    repo_root = args.repo_root.expanduser().resolve()
    if not (repo_root / "pipeline" / "web_enricher.py").exists():
        parser.error(
            f"{repo_root} does not look like the CRM Dedupe Agent repo. "
            "Set CRM_DEDUPE_AGENT_REPO or pass --repo-root."
        )
    sys.path.insert(0, str(repo_root))

    from pipeline.web_enricher import check_same_company

    path = Path(args.csv_path)
    counts: dict[str, int] = {}

    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    for idx, row in enumerate(rows[: args.limit], 1):
        domain_a = (row.get("DOMAIN_1") or "").strip()
        domain_b = (row.get("DOMAIN_2") or "").strip()
        if not domain_a or not domain_b:
            key = "MISSING_DOMAIN"
        else:
            result = check_same_company(domain_a, domain_b)
            key = f"{result['verdict']}_{result['confidence']}"
        counts[key] = counts.get(key, 0) + 1
        print(f"{idx}: {key}")

    print("SUMMARY")
    for key in sorted(counts):
        print(f"{key}: {counts[key]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
