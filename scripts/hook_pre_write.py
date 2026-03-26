#!/usr/bin/env python3
"""
hook_pre_write.py — PreToolUse hook for Claude Code.

Intercepts Write/Edit tool calls and validates state transitions
when AI attempts to write to task-progress.json or key artifacts.

This script is called by Claude Code's hooks system. It reads the
tool input from stdin (JSON) and outputs a decision.

If the write should be blocked, it exits with code 2 and prints
a human-readable message that Claude Code will inject into the conversation.
"""

import json
import os
import sys

# Project root detection
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


def find_task_dir(file_path: str) -> str | None:
    """Find the nearest task directory containing task-progress.json."""
    # Walk up from the file path looking for task-progress.json
    d = os.path.dirname(file_path) if os.path.isfile(file_path) else file_path
    while d and d != os.path.dirname(d):
        if os.path.isfile(os.path.join(d, "task-progress.json")):
            return d
        d = os.path.dirname(d)
    # Also check common task locations
    tasks_dir = os.path.join(PROJECT_ROOT, "tasks")
    if os.path.isdir(tasks_dir):
        for task_name in os.listdir(tasks_dir):
            candidate = os.path.join(tasks_dir, task_name)
            if os.path.isfile(os.path.join(candidate, "task-progress.json")):
                return candidate
    return None


def main():
    """
    Read tool input, check if the write is to a sensitive file,
    and validate if the current workflow state allows it.
    """
    # Try to parse tool input from first argument or stdin
    tool_input = None
    if len(sys.argv) > 1:
        try:
            tool_input = json.loads(sys.argv[1])
        except (json.JSONDecodeError, IndexError):
            pass

    if tool_input is None:
        try:
            tool_input = json.load(sys.stdin)
        except (json.JSONDecodeError, EOFError):
            pass

    if tool_input is None:
        # Can't parse input — allow the write (fail open)
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    basename = os.path.basename(file_path)

    # Only gate writes to workflow-critical files
    critical_files = [
        "task-progress.json",
        "confirmed_intent.md",
        "00-research.md",
        "01-jtbd.md",
        "02-structure.md",
        "03-design-contract.md",
        "index.html",
    ]

    if basename not in critical_files:
        sys.exit(0)  # Not a critical file, allow

    # Find the task directory
    task_dir = find_task_dir(file_path)
    if not task_dir:
        sys.exit(0)  # No active task found, allow

    # Import and run the validation
    sys.path.insert(0, SCRIPT_DIR)
    from validate_transition import check_write_allowed

    result = check_write_allowed(file_path, task_dir)

    if not result["allowed"]:
        # Block the write — output goes to the conversation as a hook message
        print(
            f"⚠️ Workflow Guard: Write to '{basename}' blocked.\n"
            f"Reason: {result['reason']}\n\n"
            f"Check task-progress.json to verify the current workflow state "
            f"before writing this file.",
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
