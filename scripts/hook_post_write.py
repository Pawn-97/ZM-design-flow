#!/usr/bin/env python3
"""
hook_post_write.py — PostToolUse hook for Claude Code.

After a Write completes, checks if the written file is an archive file
and validates its integrity using verify_archive.py.

Outputs warnings (not blocks) if archive quality is insufficient.
"""

import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)


# Map filename patterns to archive types
ARCHIVE_PATTERNS = [
    (r"phase1-alignment\.md$", "phase1"),
    (r"phase2-topic-.+\.md$", "phase2-topic"),
    (r"phase2-research-full\.md$", "phase2-research"),
    (r"phase3-scenario-\d+-round-\d+\.md$", "phase3-round"),
    (r"phase3-scenario-\d+\.md$", "phase3-scenario"),
    (r"phase4-review-round-\d+\.md$", "phase4-review"),
    (r"phase2-insight-cards\.md$", "insight-cards"),
]


def detect_archive_type(file_path: str) -> str | None:
    """Detect archive type from filename pattern."""
    basename = os.path.basename(file_path)
    for pattern, archive_type in ARCHIVE_PATTERNS:
        if re.search(pattern, basename):
            return archive_type
    return None


def main():
    # Parse tool input
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
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Check if this is an archive file
    archive_type = detect_archive_type(file_path)
    if not archive_type:
        sys.exit(0)  # Not an archive file, skip

    # Run verification
    sys.path.insert(0, SCRIPT_DIR)
    from verify_archive import verify_archive

    result = verify_archive(file_path, archive_type)

    if not result["valid"]:
        # Output warning (not a block — archive is already written)
        errors = "\n".join(f"  - {e}" for e in result["errors"])
        print(
            f"⚠️ Archive Quality Warning for '{os.path.basename(file_path)}':\n"
            f"{errors}\n\n"
            f"Please review and fix the archive before proceeding.",
            file=sys.stderr,
        )
        # Exit 0 anyway — post-write hooks shouldn't block
        # The warning will be injected into the conversation

    sys.exit(0)


if __name__ == "__main__":
    main()
