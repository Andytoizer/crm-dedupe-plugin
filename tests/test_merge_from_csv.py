"""Tests for the HubSpot CSV full-pipeline backfill runner."""
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from review import merge_from_csv


def _write_csv(path, rows):
    headers = sorted({key for row in rows for key in row})
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def _patch_no_db(monkeypatch):
    monkeypatch.setattr(merge_from_csv, "init_db", lambda: None)
    monkeypatch.setattr(merge_from_csv, "_pair_is_known_non_duplicate", lambda *_: False)


def test_contacts_csv_scores_then_runs_ai_review_for_review_rows(tmp_path, monkeypatch, capsys):
    _patch_no_db(monkeypatch)
    monkeypatch.setattr(merge_from_csv, "ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(merge_from_csv.anthropic, "Anthropic", lambda api_key: object())

    decisions = []
    monkeypatch.setattr(
        merge_from_csv,
        "_decide",
        lambda *args: decisions.append(args) or ("YES", "Same person after review", "claude"),
    )

    merges = []
    monkeypatch.setattr(
        merge_from_csv,
        "execute_merge",
        lambda **kwargs: merges.append(kwargs) or None,
    )

    csv_path = tmp_path / "contacts.csv"
    _write_csv(csv_path, [
        {
            "HS_OBJECT_ID_1": "1",
            "HS_OBJECT_ID_2": "2",
            "EMAIL_1": "jane@example.com",
            "EMAIL_2": "jane@example.com",
            "FIRSTNAME_1": "Jane",
            "FIRSTNAME_2": "Jane",
            "LASTNAME_1": "Doe",
            "LASTNAME_2": "Doe",
        },
        {
            "HS_OBJECT_ID_1": "3",
            "HS_OBJECT_ID_2": "4",
            "FIRSTNAME_1": "John",
            "FIRSTNAME_2": "Jon",
            "LASTNAME_1": "Smith",
            "LASTNAME_2": "Smith",
            "COMPANY_1": "Acme Corp",
            "COMPANY_2": "Acme Inc",
        },
    ])

    merge_from_csv.run(str(csv_path), "contact", dry_run=True)

    output = capsys.readouterr().out
    assert len(merges) == 2
    assert len(decisions) == 1
    assert merges[0]["match"].match_reason == "identical email address"
    assert merges[1]["match"].match_reason.startswith("AI review [claude]")
    assert "AUTO_MERGE from scorer: 1" in output
    assert "AI YES (merge):        1" in output


def test_companies_csv_ai_no_suppresses_without_merging_in_dry_run(tmp_path, monkeypatch, capsys):
    _patch_no_db(monkeypatch)
    monkeypatch.setattr(merge_from_csv, "ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr(merge_from_csv.anthropic, "Anthropic", lambda api_key: object())
    monkeypatch.setattr(
        merge_from_csv,
        "_decide",
        lambda *args: ("NO", "Different companies after web research", "web_high"),
    )

    merges = []
    monkeypatch.setattr(
        merge_from_csv,
        "execute_merge",
        lambda **kwargs: merges.append(kwargs) or None,
    )

    csv_path = tmp_path / "companies.csv"
    _write_csv(csv_path, [{
        "HS_OBJECT_ID_1": "10",
        "HS_OBJECT_ID_2": "11",
        "NAME_1": "Acme Corporation",
        "NAME_2": "Acme Corp Inc",
        "DOMAIN_1": "acme.com",
        "DOMAIN_2": "acme.io",
    }])

    merge_from_csv.run(str(csv_path), "company", dry_run=True)

    output = capsys.readouterr().out
    assert merges == []
    assert "AI NO [web_high]" in output
    assert "AI NO (suppress):      1" in output


def test_live_csv_backfill_requires_max_merges(monkeypatch, tmp_path):
    _patch_no_db(monkeypatch)
    csv_path = tmp_path / "contacts.csv"
    _write_csv(csv_path, [{
        "HS_OBJECT_ID_1": "1",
        "HS_OBJECT_ID_2": "2",
        "EMAIL_1": "jane@example.com",
        "EMAIL_2": "jane@example.com",
    }])

    with pytest.raises(SystemExit, match="--max-merges"):
        merge_from_csv.run(str(csv_path), "contact", dry_run=False)
