"""
One-time script to register scheduled dedup tasks via the Claude scheduled-tasks MCP.

Run this once to set up the always-on dedup schedule:
    python scheduler/register_schedule.py

Tasks registered:
  1. Incremental dedup — daily cleanup, live only when DEDUP_LIVE=true
  2. Slack review digest — daily at 9am Pacific
  3. Weekly bulk re-scan — Sundays at 2am Pacific
"""
import os
import shlex
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR_SHELL = shlex.quote(PROJECT_DIR)

SCHEDULED_TASKS = [
    {
        "name": "hubspot-dedup-incremental",
        "description": "Run daily HubSpot dedup; live merges only when DEDUP_LIVE=true",
        "schedule": "0 16 * * *",  # Daily at 8am Pacific standard time / 9am Pacific daylight time
        "prompt": (
            f"Run the HubSpot incremental deduplication agent. "
            f"Execute: cd {PROJECT_DIR_SHELL} && "
            f"if [ \"$DEDUP_LIVE\" = \"true\" ]; then python agents/incremental_dedup_agent.py --live; "
            f"else python agents/incremental_dedup_agent.py; fi. "
            f"Live mode is allowed only when DEDUP_LIVE=true; otherwise run as a dry-run. "
            f"In live mode, auto-merge only high-confidence matches according to the repo thresholds, "
            f"queue fuzzy or uncertain matches for human review, and report a summary of "
            f"contacts and companies merged or flagged."
        ),
    },
    {
        "name": "hubspot-dedup-slack-digest",
        "description": "Send daily Slack digest of pending review queue items",
        "schedule": "0 17 * * *",  # 9am Pacific standard time / 10am Pacific daylight time
        "prompt": (
            f"Send the HubSpot dedup review digest to Slack. "
            f"Execute: cd {PROJECT_DIR_SHELL} && python review/slack_digest.py. "
            f"Report how many items were included in the digest."
        ),
    },
    {
        "name": "hubspot-dedup-weekly-bulk",
        "description": "Weekly full re-scan of all HubSpot records to catch long-tail duplicates",
        "schedule": "0 10 * * 0",  # Sundays 2am Pacific standard time / 3am Pacific daylight time
        "prompt": (
            f"Run the HubSpot bulk deduplication agent for a full re-scan. "
            f"Execute: cd {PROJECT_DIR_SHELL} && python agents/bulk_dedup_agent.py. "
            f"Add --live flag only if DEDUP_LIVE=true is set in the environment. "
            f"Report totals for contacts and companies: merged, flagged, discarded."
        ),
    },
]


def register():
    print("HubSpot Dedup — Schedule Registration")
    print("=" * 50)
    print()
    print("This script registers 3 scheduled tasks via the scheduled-tasks MCP.")
    print("Run it from Claude Code with MCP access, or use the MCP tool directly.")
    print()
    print("Tasks to register:")
    for task in SCHEDULED_TASKS:
        print(f"\n  Name:     {task['name']}")
        print(f"  Schedule: {task['schedule']}")
        print(f"  Prompt:   {task['prompt'][:100]}...")

    print()
    print("To register these tasks, use the scheduled-tasks MCP tool:")
    print("  mcp__scheduled-tasks__create_scheduled_task")
    print()
    print("Or ask Claude: 'Register the HubSpot dedup schedule using scheduler/register_schedule.py'")

    # Output the task configs as JSON for easy copy-paste into MCP tool calls
    import json
    print()
    print("Task configs (JSON):")
    print(json.dumps(SCHEDULED_TASKS, indent=2))


if __name__ == "__main__":
    register()
