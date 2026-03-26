#!/usr/bin/env python3
"""
verify_archive.py — Archive integrity verifier for Zoom AI-UX Workflow.

Validates that archive files produced during Context Reset / phase transitions
contain the required structure, YAML frontmatter, and content.

Usage:
    python3 scripts/verify_archive.py <archive_file> <archive_type>

Archive types:
    phase1          - Phase 1 alignment archive
    phase2-topic    - Phase 2 topic-level discussion archive
    phase2-research - Phase 2 full research report archive
    phase3-scenario - Phase 3 per-scenario archive (must contain RoundDecision)
    phase3-round    - Phase 3 per-round recall buffer
    phase4-review   - Phase 4 review round archive
    insight-cards   - InsightCard collection file

Exit codes:
    0 = validation passed
    1 = validation failed
    2 = usage error
"""

import json
import os
import re
import sys


# ---------------------------------------------------------------------------
# YAML frontmatter parser (no PyYAML dependency — uses regex)
# ---------------------------------------------------------------------------

FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL
)


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter as a simple key-value dict (flat parsing)."""
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}

    raw = match.group(1)
    result = {}
    current_key = None
    current_list = None

    for line in raw.split("\n"):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Simple key: value
        kv_match = re.match(r"^(\w[\w_-]*)\s*:\s*(.+)$", stripped)
        if kv_match:
            key = kv_match.group(1)
            value = kv_match.group(2).strip().strip('"').strip("'")
            if current_key and current_list is not None:
                result[current_key] = current_list
            current_key = key
            current_list = None
            result[key] = value
            continue

        # Key with no inline value (starts a list)
        key_only = re.match(r"^(\w[\w_-]*)\s*:\s*$", stripped)
        if key_only:
            if current_key and current_list is not None:
                result[current_key] = current_list
            current_key = key_only.group(1)
            current_list = []
            continue

        # List item
        list_item = re.match(r"^-\s+(.+)$", stripped)
        if list_item and current_list is not None:
            current_list.append(list_item.group(1).strip().strip('"').strip("'"))

    if current_key and current_list is not None:
        result[current_key] = current_list

    return result


# ---------------------------------------------------------------------------
# Validation rules per archive type
# ---------------------------------------------------------------------------

def validate_phase1(content: str, frontmatter: dict) -> list:
    """Validate Phase 1 alignment archive."""
    errors = []
    if not frontmatter:
        errors.append("Missing YAML frontmatter")
    else:
        if "keywords" not in frontmatter:
            errors.append("Frontmatter missing 'keywords' field")
        if "sections" not in frontmatter:
            errors.append("Frontmatter missing 'sections' field")

    if len(content.strip()) < 100:
        errors.append("Archive content suspiciously short (<100 chars)")

    return errors


def validate_phase2_topic(content: str, frontmatter: dict) -> list:
    """Validate Phase 2 topic-level discussion archive."""
    errors = []
    if not frontmatter:
        errors.append("Missing YAML frontmatter")
    else:
        if "keywords" not in frontmatter:
            errors.append("Frontmatter missing 'keywords' field")
        if "topic_domain" not in frontmatter:
            errors.append(
                "Frontmatter missing 'topic_domain' field "
                "(required for topic-level archives)"
            )

    if len(content.strip()) < 200:
        errors.append("Archive content suspiciously short (<200 chars)")

    return errors


def validate_phase2_research(content: str, frontmatter: dict) -> list:
    """Validate Phase 2 full research report archive."""
    errors = []
    if not frontmatter:
        errors.append("Missing YAML frontmatter")

    # Should have substantial content
    if len(content.strip()) < 500:
        errors.append("Research archive too short (<500 chars) — expected full report")

    # Should have markdown headings
    headings = re.findall(r"^#{1,3}\s+.+$", content, re.MULTILINE)
    if len(headings) < 2:
        errors.append("Research archive has fewer than 2 headings — structure seems incomplete")

    return errors


def validate_phase3_scenario(content: str, frontmatter: dict) -> list:
    """Validate Phase 3 per-scenario archive (must contain RoundDecision)."""
    errors = []
    if not frontmatter:
        errors.append("Missing YAML frontmatter")
    else:
        if "keywords" not in frontmatter:
            errors.append("Frontmatter missing 'keywords' field")

    # Must contain at least one RoundDecision structure
    round_markers = re.findall(
        r"(?:round\s*:\s*\d|RoundDecision|options_presented|verdict\s*:)",
        content,
        re.IGNORECASE,
    )
    if not round_markers:
        errors.append(
            "No RoundDecision structure found in scenario archive. "
            "Expected at least one round with verdict/options_presented."
        )

    if len(content.strip()) < 300:
        errors.append("Scenario archive too short (<300 chars)")

    return errors


def validate_phase3_round(content: str, frontmatter: dict) -> list:
    """Validate Phase 3 per-round recall buffer."""
    errors = []
    if len(content.strip()) < 100:
        errors.append("Round recall buffer too short (<100 chars)")
    return errors


def validate_phase4_review(content: str, frontmatter: dict) -> list:
    """Validate Phase 4 review round archive."""
    errors = []
    if len(content.strip()) < 50:
        errors.append("Review round archive too short (<50 chars)")
    return errors


def validate_insight_cards(content: str, frontmatter: dict) -> list:
    """Validate InsightCard collection file."""
    errors = []

    # Should contain at least one InsightCard
    card_markers = re.findall(
        r"(?:topic_domain\s*:|key_insights\s*:|blind_spots\s*:)",
        content,
        re.IGNORECASE,
    )
    if not card_markers:
        errors.append(
            "No InsightCard structure found. "
            "Expected topic_domain, key_insights, blind_spots fields."
        )

    # Check blind_spots presence (anti-premature-convergence mechanism)
    blind_spots = re.findall(r"blind_spots\s*:", content, re.IGNORECASE)
    if not blind_spots:
        errors.append(
            "No 'blind_spots' field found in InsightCards. "
            "Each card must have >=2 blind spots for anti-premature-convergence."
        )

    # Check key_insights has content
    insights_blocks = re.findall(
        r"key_insights\s*:\s*\n((?:\s+-\s+.+\n?)+)", content
    )
    for i, block in enumerate(insights_blocks):
        items = re.findall(r"^\s+-\s+(.+)$", block, re.MULTILINE)
        if len(items) == 0:
            errors.append(f"InsightCard #{i+1}: key_insights is empty")

    return errors


VALIDATORS = {
    "phase1": validate_phase1,
    "phase2-topic": validate_phase2_topic,
    "phase2-research": validate_phase2_research,
    "phase3-scenario": validate_phase3_scenario,
    "phase3-round": validate_phase3_round,
    "phase4-review": validate_phase4_review,
    "insight-cards": validate_insight_cards,
}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def verify_archive(file_path: str, archive_type: str) -> dict:
    """Run validation on an archive file."""
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "file": file_path,
        "type": archive_type,
    }

    # File existence
    if not os.path.isfile(file_path):
        result["valid"] = False
        result["errors"].append(f"Archive file not found: {file_path}")
        return result

    # File non-empty
    if os.path.getsize(file_path) == 0:
        result["valid"] = False
        result["errors"].append(f"Archive file is empty: {file_path}")
        return result

    # Read content
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse frontmatter
    frontmatter = parse_frontmatter(content)

    # Run type-specific validator
    if archive_type not in VALIDATORS:
        result["valid"] = False
        result["errors"].append(
            f"Unknown archive type: '{archive_type}'. "
            f"Valid types: {list(VALIDATORS.keys())}"
        )
        return result

    errors = VALIDATORS[archive_type](content, frontmatter)
    if errors:
        result["valid"] = False
        result["errors"] = errors

    return result


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: python3 verify_archive.py <archive_file> <archive_type>\n"
            f"Valid types: {list(VALIDATORS.keys())}",
            file=sys.stderr,
        )
        sys.exit(2)

    file_path = sys.argv[1]
    archive_type = sys.argv[2]

    result = verify_archive(file_path, archive_type)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
