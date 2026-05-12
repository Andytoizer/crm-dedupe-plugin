#!/usr/bin/env python3
"""Verify that plugin guidance still matches the original CRM Dedupe Agent scoring."""

import argparse
import os
import sys
from pathlib import Path


def _default_repo_root() -> Path:
    return Path(os.getenv("CRM_DEDUPE_AGENT_REPO", Path.cwd()))


def _base_contact(record_id: str, **overrides) -> dict:
    record = {
        "id": record_id,
        "email": "",
        "firstname": "Alex",
        "lastname": "Rivera",
        "company": "Acme Construction",
        "phone": "",
        "mobilephone": "",
        "phone_1": "",
        "hs_linkedin_url": "",
        "lemlistlinkedinurl": "",
        "num_associated_deals": 0,
        "num_notes": 0,
        "hs_email_open": 0,
        "hs_email_click": 0,
        "hs_email_sends_since_last_engagement": 0,
        "hs_email_replied": 0,
        "createdate": "2024-01-01T00:00:00Z",
    }
    record.update(overrides)
    return record


def _base_company(record_id: str, **overrides) -> dict:
    record = {
        "id": record_id,
        "name": "Acme Construction LLC",
        "domain": "",
        "website": "",
        "linkedin_company_page": "",
        "lemlistprofileurl": "",
        "phone": "",
        "num_associated_contacts": 0,
        "num_associated_deals": 0,
        "createdate": "2024-01-01T00:00:00Z",
    }
    record.update(overrides)
    return record


def _assert_result(label: str, result, score: float, action: str, signal: str) -> None:
    if result.score != score or result.action != action or signal not in result.match_signals:
        raise AssertionError(
            f"{label}: expected score={score}, action={action}, signal={signal}; "
            f"got score={result.score}, action={result.action}, signals={result.match_signals}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=_default_repo_root())
    args = parser.parse_args()

    repo_root = args.repo_root.expanduser().resolve()
    if not (repo_root / "pipeline" / "scorer.py").exists():
        parser.error(
            f"{repo_root} does not look like the CRM Dedupe Agent repo. "
            "Set CRM_DEDUPE_AGENT_REPO or pass --repo-root."
        )
    sys.path.insert(0, str(repo_root))

    from config.settings import AUTO_MERGE_THRESHOLD, REVIEW_THRESHOLD
    from pipeline.scorer import score_companies, score_contacts, select_master

    if AUTO_MERGE_THRESHOLD != 0.95:
        raise AssertionError(f"AUTO_MERGE_THRESHOLD changed: {AUTO_MERGE_THRESHOLD}")
    if REVIEW_THRESHOLD != 0.70:
        raise AssertionError(f"REVIEW_THRESHOLD changed: {REVIEW_THRESHOLD}")

    _assert_result(
        "contact email exact",
        score_contacts(
            _base_contact("c1", email="alex@example.com"),
            _base_contact("c2", email="ALEX@example.com"),
        ),
        1.0,
        "AUTO_MERGE",
        "email_exact",
    )
    _assert_result(
        "contact Gmail dots",
        score_contacts(
            _base_contact("c1", email="alex.rivera@gmail.com"),
            _base_contact("c2", email="alexrivera@gmail.com"),
        ),
        0.97,
        "AUTO_MERGE",
        "email_gmail_dots",
    )
    _assert_result(
        "contact LinkedIn",
        score_contacts(
            _base_contact("c1", hs_linkedin_url="https://www.linkedin.com/in/alex-rivera/"),
            _base_contact("c2", lemlistlinkedinurl="linkedin.com/in/alex-rivera"),
        ),
        0.98,
        "AUTO_MERGE",
        "linkedin_exact",
    )
    _assert_result(
        "contact phone",
        score_contacts(
            _base_contact("c1", phone="+1 (415) 555-1212"),
            _base_contact("c2", mobilephone="4155551212"),
        ),
        0.92,
        "REVIEW",
        "phone_exact",
    )
    fuzzy_contact = score_contacts(
        _base_contact("c1", firstname="Alex", lastname="Rivera", company="Acme Construction LLC"),
        _base_contact("c2", firstname="Alex", lastname="Rivera", company="Acme Construction Inc"),
    )
    if fuzzy_contact.score > 0.89 or fuzzy_contact.action != "REVIEW":
        raise AssertionError(f"contact fuzzy cap changed: {fuzzy_contact}")

    _assert_result(
        "company domain",
        score_companies(
            _base_company("co1", domain="https://www.acme.com/path"),
            _base_company("co2", website="acme.com"),
        ),
        1.0,
        "AUTO_MERGE",
        "domain_exact",
    )
    _assert_result(
        "company LinkedIn",
        score_companies(
            _base_company("co1", linkedin_company_page="https://linkedin.com/company/acme"),
            _base_company("co2", lemlistprofileurl="linkedin.com/company/acme/"),
        ),
        0.98,
        "AUTO_MERGE",
        "linkedin_company_exact",
    )
    fuzzy_company = score_companies(
        _base_company("co1", name="Acme Construction LLC"),
        _base_company("co2", name="Acme Construction Inc"),
    )
    if fuzzy_company.score > 0.89 or fuzzy_company.action != "REVIEW":
        raise AssertionError(f"company fuzzy cap changed: {fuzzy_company}")

    master, secondary = select_master(
        _base_contact("quiet", email="quiet@example.com"),
        _base_contact("active", email="active@example.com", num_associated_deals=2),
    )
    if master["id"] != "active" or secondary["id"] != "quiet":
        raise AssertionError("engagement-weighted master selection changed")

    print("OK: original scoring contract preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
