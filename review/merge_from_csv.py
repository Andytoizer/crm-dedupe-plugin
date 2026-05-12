# ============================================================
# INTEGRATION FILE — Adapt this for your CRM  
# Original: Built for HubSpot CSV export format (columns: FIRSTNAME_1, EMAIL_2, etc.)
# What to change: CONTACT_FIELD_MAP and COMPANY_FIELD_MAP to match your CRM's export column names
# What to preserve: The master selection logic and merge execution flow
# ============================================================

"""
Run HubSpot-identified duplicate pairs through the full dedupe pipeline.

HubSpot's own dedup tool exports pairs as CSV with columns:
  HS_OBJECT_ID_1, HS_OBJECT_ID_2, FIRSTNAME_1, FIRSTNAME_2, ...

This script:
  1. Reads the CSV
  2. Builds record dicts from the _1/_2 columns
  3. Scores each pair with the bundled scorer
  4. Sends REVIEW pairs through fast rules, web research, and Claude reasoning
  5. Executes or simulates approved merges via HubSpot API

Usage:
    # Dry run (default)
    python review/merge_from_csv.py --contacts contacts.csv
    python review/merge_from_csv.py --companies companies.csv

    # Live
    python review/merge_from_csv.py --contacts contacts.csv --live
    python review/merge_from_csv.py --companies companies.csv --live
"""
import argparse
import csv
import json
import os
import sys
import time
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import anthropic

from config.settings import ANTHROPIC_API_KEY
from db.database import get_session, init_db
from db.models import KnownNonDuplicate, ReviewQueue
from pipeline.merger import execute_merge
from pipeline.scorer import score_companies, score_contacts, select_master
from review.ai_review import _decide, _suppress


# Map CSV column names (uppercase, no suffix) → our internal record field names
CONTACT_FIELD_MAP = {
    "HS_OBJECT_ID": "id",
    "FIRSTNAME": "firstname",
    "LASTNAME": "lastname",
    "EMAIL": "email",
    "PHONE": "phone",
    "MOBILEPHONE": "mobilephone",
    "COMPANY": "company",
    "HS_LINKEDIN_URL": "hs_linkedin_url",
    "LEMLISTLINKEDINURL": "lemlistlinkedinurl",
    "NUM_ASSOCIATED_DEALS": "num_associated_deals",
    "NUM_NOTES": "num_notes",
    "HS_EMAIL_OPEN": "hs_email_open",
    "HS_EMAIL_SENDS_SINCE_LAST_ENGAGEMENT": "hs_email_sends_since_last_engagement",
    "HS_LAST_SALES_ACTIVITY_TIMESTAMP": "hs_last_sales_activity_timestamp",
    "NOTES_LAST_CONTACTED": "notes_last_contacted",
    "HS_SALES_EMAIL_LAST_REPLIED": "hs_email_replied",
    "CREATEDATE": "createdate",
    "LASTMODIFIEDDATE": "lastmodifieddate",
    "LIFECYCLESTAGE": "lifecyclestage",
    "HUBSPOT_OWNER_ID": "hubspot_owner_id",
    "HS_MERGED_OBJECT_IDS": "hs_merged_object_ids",
}

COMPANY_FIELD_MAP = {
    "HS_OBJECT_ID": "id",
    "NAME": "name",
    "DOMAIN": "domain",
    "WEBSITE": "website",
    "LINKEDIN_COMPANY_PAGE": "linkedin_company_page",
    "LEMLISTPROFILEURL": "lemlistprofileurl",
    "PHONE": "phone",
    "NUM_ASSOCIATED_CONTACTS": "num_associated_contacts",
    "NUM_ASSOCIATED_DEALS": "num_associated_deals",
    "HS_LAST_SALES_ACTIVITY_TIMESTAMP": "hs_last_sales_activity_timestamp",
    "CREATEDATE": "createdate",
    "HS_LASTMODIFIEDDATE": "lastmodifieddate",
    "LIFECYCLESTAGE": "lifecyclestage",
    "HUBSPOT_OWNER_ID": "hubspot_owner_id",
    "HS_MERGED_OBJECT_IDS": "hs_merged_object_ids",
}


def _build_record(row: dict, suffix: str, field_map: dict) -> dict:
    """Extract _1 or _2 fields from a CSV row into a normalised record dict."""
    record = {}
    for csv_col, internal_field in field_map.items():
        val = row.get(f"{csv_col}_{suffix}", "").strip()
        record[internal_field] = val
    # Coerce all numeric fields — must be 0 not None so scorer comparisons work
    numeric_fields = (
        "num_associated_deals", "num_notes", "num_associated_contacts",
        "hs_email_open", "hs_email_click", "hs_email_sends_since_last_engagement",
        "hs_email_replied",
    )
    for f in numeric_fields:
        try:
            record[f] = int(record.get(f) or 0)
        except (ValueError, TypeError):
            record[f] = 0
    return record


def _contact_summary(record: dict) -> dict:
    return {
        "name": f"{record.get('firstname', '')} {record.get('lastname', '')}".strip(),
        "email": record.get("email", ""),
        "phone": record.get("phone", "") or record.get("mobilephone", ""),
        "company": record.get("company", ""),
        "linkedin": record.get("hs_linkedin_url", "") or record.get("lemlistlinkedinurl", ""),
        "createdate": record.get("createdate", ""),
        "deals": record.get("num_associated_deals", 0),
        "notes": record.get("num_notes", 0),
    }


def _company_summary(record: dict) -> dict:
    return {
        "name": record.get("name", ""),
        "domain": record.get("domain", ""),
        "website": record.get("website", ""),
        "linkedin": record.get("linkedin_company_page", "") or record.get("lemlistprofileurl", ""),
        "contacts": record.get("num_associated_contacts", 0),
        "deals": record.get("num_associated_deals", 0),
        "createdate": record.get("createdate", ""),
    }


def _add_to_review_queue(object_type: str, rec_a: dict, rec_b: dict, result) -> bool:
    """Add an UNSURE pair to the local review queue if it is not already present."""
    summary_fn = _contact_summary if object_type == "contact" else _company_summary
    id_a = rec_a["id"]
    id_b = rec_b["id"]
    with get_session() as session:
        existing = session.query(ReviewQueue).filter(
            ReviewQueue.object_type == object_type,
            ReviewQueue.status.in_(["PENDING", "APPROVED", "REJECTED"]),
            ReviewQueue.id_a.in_([id_a, id_b]),
            ReviewQueue.id_b.in_([id_a, id_b]),
        ).first()
        if existing:
            return False

        session.add(ReviewQueue(
            object_type=object_type,
            id_a=id_a,
            id_b=id_b,
            score=result.score,
            match_signals=json.dumps(result.match_signals),
            match_reason=result.match_reason,
            record_a_summary=json.dumps(summary_fn(rec_a)),
            record_b_summary=json.dumps(summary_fn(rec_b)),
            status="PENDING",
        ))
    return True


def _pair_is_known_non_duplicate(object_type: str, id_a: str, id_b: str) -> bool:
    with get_session() as session:
        return session.query(KnownNonDuplicate).filter(
            KnownNonDuplicate.object_type == object_type,
            KnownNonDuplicate.id_a.in_([id_a, id_b]),
            KnownNonDuplicate.id_b.in_([id_a, id_b]),
        ).first() is not None


def _merge_status(dry_run: bool, merged_id) -> str:
    return "DRY" if dry_run else f"MERGED→{merged_id}"


def run(
    csv_path: str,
    object_type: str,
    dry_run: bool = True,
    limit: int = None,
    max_merges: int = None,
    ai_review: bool = True,
):
    init_db()
    hs_type = "contacts" if object_type == "contact" else "companies"

    if not dry_run and max_merges is None:
        raise SystemExit("Live CSV backfills require an explicit --max-merges cap.")

    print(f"\n{'='*60}")
    print(f"CSV Full Pipeline — {object_type}s")
    print(f"File: {csv_path}")
    print(f"Mode: {'DRY RUN' if dry_run else '*** LIVE ***'}")
    print("Pipeline: score → auto-merge candidates OR AI review → YES / NO / UNSURE")
    if not dry_run:
        print(f"Live merge cap: {max_merges}")
    print(f"{'='*60}\n")

    field_map = CONTACT_FIELD_MAP if object_type == "contact" else COMPANY_FIELD_MAP
    score_fn = score_contacts if object_type == "contact" else score_companies

    auto_merge = 0
    ai_yes = 0
    ai_no = 0
    ai_unsure = 0
    discard = 0
    skipped = 0
    errors = 0
    executed = 0
    methods = {"fast_rule": 0, "web_high": 0, "web+claude": 0, "claude": 0}
    run_id = f"csv-full-pipeline-{uuid.uuid4()}"
    client = None

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if limit:
        rows = rows[:limit]

    total = len(rows)

    for i, row in enumerate(rows, 1):
        if not dry_run and executed >= max_merges:
            print(f"[{i}/{total}] STOP — reached --max-merges={max_merges}")
            break

        rec_a = _build_record(row, "1", field_map)
        rec_b = _build_record(row, "2", field_map)

        id_a = rec_a.get("id")
        id_b = rec_b.get("id")

        if not id_a or not id_b:
            print(f"[{i}/{total}] SKIP — missing IDs")
            skipped += 1
            continue

        if id_a == id_b:
            print(f"[{i}/{total}] SKIP — same record ID ({id_a})")
            skipped += 1
            continue

        try:
            if _pair_is_known_non_duplicate(object_type, id_a, id_b):
                print(f"[{i}/{total}] SKIP — known non-duplicate pair")
                skipped += 1
                continue
        except Exception as e:
            print(f"[{i}/{total}] WARN — could not check suppression table: {e}")

        try:
            result = score_fn(rec_a, rec_b)

            if result.action == "DISCARD":
                print(f"[{i}/{total}] DISCARD score={result.score:.2f} | {result.match_reason}")
                discard += 1
                continue

            if result.action == "REVIEW":
                if not ai_review:
                    queued = _add_to_review_queue(object_type, rec_a, rec_b, result)
                    queue_note = "queued" if queued else "already queued"
                    print(f"[{i}/{total}] REVIEW score={result.score:.2f} | {queue_note}")
                    ai_unsure += 1
                    continue

                if client is None:
                    if not ANTHROPIC_API_KEY:
                        raise RuntimeError("ANTHROPIC_API_KEY is required for CSV REVIEW rows.")
                    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

                decision, reason, method = _decide(
                    object_type, rec_a, rec_b, result.match_reason, client,
                )
                methods[method] = methods.get(method, 0) + 1

                if decision == "NO":
                    ai_no += 1
                    if not dry_run:
                        _suppress(object_type, id_a, id_b)
                    print(f"[{i}/{total}] AI NO [{method}] score={result.score:.2f} | {'would suppress' if dry_run else 'suppressed'} | {reason}")
                    continue

                if decision == "UNSURE":
                    ai_unsure += 1
                    queued = _add_to_review_queue(object_type, rec_a, rec_b, result)
                    queue_note = "queued for human review" if queued else "already queued for human review"
                    print(f"[{i}/{total}] AI UNSURE [{method}] score={result.score:.2f} | {queue_note} | {reason}")
                    continue

                if decision != "YES":
                    ai_unsure += 1
                    queued = _add_to_review_queue(object_type, rec_a, rec_b, result)
                    queue_note = "queued for human review" if queued else "already queued for human review"
                    print(f"[{i}/{total}] AI {decision} [{method}] score={result.score:.2f} | {queue_note} | {reason}")
                    continue

                result.action = "AUTO_MERGE"
                result.match_reason = f"AI review [{method}]: {reason}"
                ai_yes += 1
            else:
                auto_merge += 1

            merged_id = execute_merge(
                match=result,
                record_a=rec_a,
                record_b=rec_b,
                object_type=hs_type,
                run_id=run_id,
                dry_run=dry_run,
            )

            if not dry_run:
                executed += 1

            master, secondary = select_master(rec_a, rec_b)
            source = "AI YES" if result.match_reason.startswith("AI review") else "AUTO"
            print(
                f"[{i}/{total}] {source} {_merge_status(dry_run, merged_id)} "
                f"score={result.score:.2f} | master {master['id']} ← absorbs {secondary['id']} | "
                f"{result.match_reason}"
            )

        except ValueError as e:
            print(f"[{i}/{total}] SKIP — {e}")
            skipped += 1
        except Exception as e:
            print(f"[{i}/{total}] ERROR — {e}")
            errors += 1

        if not dry_run:
            time.sleep(0.15)  # gentle rate limiting

    print(f"\n{'='*60}")
    print(f"{'DRY RUN ' if dry_run else ''}Results:")
    print(f"  AUTO_MERGE from scorer: {auto_merge}")
    print(f"  AI YES (merge):        {ai_yes}")
    print(f"  AI NO (suppress):      {ai_no}")
    print(f"  AI UNSURE (human):     {ai_unsure}")
    print(f"  DISCARD:               {discard}")
    print(f"  Skipped:               {skipped}")
    print(f"  Errors:                {errors}")
    print(f"\nDecision methods:")
    print(f"  Fast CRM rule: {methods['fast_rule']}")
    print(f"  Web (high):    {methods['web_high']}")
    print(f"  Web + Claude:  {methods['web+claude']}")
    print(f"  Claude only:   {methods['claude']}")
    if dry_run:
        print(f"\nRun with --live --max-merges <N> to execute approved merges.")
    print(f"{'='*60}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--contacts", metavar="CSV", help="Path to contacts duplicate CSV")
    group.add_argument("--companies", metavar="CSV", help="Path to companies duplicate CSV")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-merges", type=int, default=None,
                        help="Required in live mode; hard cap on merge writes")
    parser.add_argument("--queue-only", action="store_true",
                        help="Do not run AI review; add REVIEW rows to the local queue")
    args = parser.parse_args()

    if args.contacts:
        run(
            args.contacts, "contact",
            dry_run=not args.live,
            limit=args.limit,
            max_merges=args.max_merges,
            ai_review=not args.queue_only,
        )
    else:
        run(
            args.companies, "company",
            dry_run=not args.live,
            limit=args.limit,
            max_merges=args.max_merges,
            ai_review=not args.queue_only,
        )
