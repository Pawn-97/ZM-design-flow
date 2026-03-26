#!/usr/bin/env python3
"""
validate_html.py — HTML structure & ZDS compliance validator for HarnessDesign AI-UX Workflow.

Checks 6 validation items corresponding to the Alchemist Skill's validation checklist:
1. HTML syntax correctness
2. ZDS color compliance (no Tailwind presets, no custom colors)
3. Spacing compliance (only 4px grid multiples)
4. Scenario completeness (all DesignContract scenarios present)
5. Navigation coverage (navigateToScenario covers adjacency map)
6. Empty states (lists/tables have empty state handling)

Usage:
    python3 .harnessdesign/scripts/validate_html.py <html_file> [--contract <design_contract_path>]

Exit codes:
    0 = all checks passed
    1 = one or more checks failed
    2 = usage error
"""

import json
import os
import re
import sys

# Add script directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dom_extractor import (
    parse_html,
    extract,
    ZDS_ALLOWED_COLORS,
    ZDS_SPECIAL_VALUES,
    ZDS_ALLOWED_SPACING,
    TW_SPACING_PATTERN,
    HEX_COLOR_PATTERN,
    TAILWIND_PRESET_PATTERN,
)

# ---------------------------------------------------------------------------
# DesignContract parser (minimal — extracts scenario IDs and adjacency map)
# ---------------------------------------------------------------------------

def parse_design_contract(contract_path: str) -> dict:
    """Parse 03-design-contract.md to extract scenario IDs and adjacency map."""
    if not os.path.isfile(contract_path):
        return {"scenarios": [], "adjacency": {}}

    with open(contract_path, "r", encoding="utf-8") as f:
        content = f.read()

    scenarios = []
    adjacency = {}

    # Extract scenario IDs from headers or structured lists
    # Pattern: scenario_id: xxx or scenario-N: xxx (must contain a digit to avoid false positives)
    for match in re.finditer(
        r"(?:scenario[_-]?id)\s*[:：]\s*['\"]?([a-zA-Z0-9_-]+)",
        content, re.IGNORECASE
    ):
        sid = match.group(1)
        if sid not in scenarios:
            scenarios.append(sid)

    # Also try section headers
    for match in re.finditer(r"#{2,4}\s+.*?(scenario[-_]?\d+\w*)", content, re.IGNORECASE):
        sid = match.group(1)
        if sid not in scenarios:
            scenarios.append(sid)

    # Extract adjacency map
    # Pattern: scenario-1 → scenario-2 or scenario-1 -> scenario-2
    for match in re.finditer(
        r"([a-zA-Z0-9_-]+)\s*(?:→|->|=>)\s*([a-zA-Z0-9_-]+)",
        content
    ):
        src, dst = match.group(1), match.group(2)
        if "scenario" in src.lower() or "scenario" in dst.lower():
            adjacency.setdefault(src, [])
            if dst not in adjacency[src]:
                adjacency[src].append(dst)

    return {"scenarios": scenarios, "adjacency": adjacency}


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

def check_html_syntax(file_path: str) -> dict:
    """Check 1: HTML syntax correctness."""
    try:
        soup = parse_html(file_path)

        issues = []
        if not soup.find("html"):
            issues.append("Missing <html> tag")
        if not soup.find("head"):
            issues.append("Missing <head> tag")
        if not soup.find("body"):
            issues.append("Missing <body> tag")

        # Check for unclosed critical tags by verifying structure
        body = soup.find("body")
        if body and len(body.find_all(True)) == 0:
            issues.append("Empty <body> — no content")

        return {
            "passed": len(issues) == 0,
            "details": "Valid HTML structure" if not issues else "; ".join(issues),
            "issues": issues,
        }
    except Exception as e:
        return {
            "passed": False,
            "details": f"Parse error: {str(e)}",
            "issues": [str(e)],
        }


def check_zds_color_compliance(extraction: dict) -> dict:
    """Check 2: ZDS color compliance."""
    violations = []

    # Check hex colors
    for color in extraction["colors_used"]:
        normalized = color.lower().strip()
        # Normalize 3-char hex to 6-char
        if len(normalized) == 4:  # #abc -> #aabbcc
            normalized = "#" + normalized[1]*2 + normalized[2]*2 + normalized[3]*2

        if normalized not in ZDS_ALLOWED_COLORS and normalized not in ZDS_SPECIAL_VALUES:
            violations.append({
                "type": "disallowed_color",
                "value": color,
                "message": f"Color {color} is not in ZDS allowed palette",
            })

    # Check Tailwind preset color names
    for v in extraction["tailwind_preset_violations"]:
        violations.append({
            "type": "tailwind_preset",
            "value": v["class"],
            "element": v["element"],
            "element_id": v["id"],
            "message": f"Tailwind preset color '{v['class']}' used — must use ZDS hex values",
        })

    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "violation_count": len(violations),
    }


def check_spacing_compliance(extraction: dict) -> dict:
    """Check 3: Spacing compliance (4px grid only)."""
    violations = []

    for cls in extraction["spacing_classes"]:
        match = TW_SPACING_PATTERN.match(cls)
        if match:
            value = match.group(1)
            # Remove brackets for arbitrary values
            value = value.strip("[]").replace("px", "").replace("rem", "")

            if value not in ZDS_ALLOWED_SPACING:
                violations.append({
                    "class": cls,
                    "value": value,
                    "message": f"Spacing class '{cls}' uses non-standard value '{value}'",
                })

    return {
        "passed": len(violations) == 0,
        "violations": violations,
        "violation_count": len(violations),
    }


def check_scenario_completeness(extraction: dict, contract: dict) -> dict:
    """Check 4: All DesignContract scenarios present in HTML."""
    if not contract["scenarios"]:
        return {
            "passed": True,
            "details": "No design contract provided — skipping scenario completeness check",
            "missing": [],
            "skipped": True,
        }

    html_scenario_ids = {s["id"].lower() for s in extraction["scenarios"]}
    missing = []

    for sid in contract["scenarios"]:
        if sid.lower() not in html_scenario_ids:
            missing.append(sid)

    return {
        "passed": len(missing) == 0,
        "missing": missing,
        "expected": contract["scenarios"],
        "found": [s["id"] for s in extraction["scenarios"]],
    }


def check_navigation_coverage(extraction: dict, contract: dict) -> dict:
    """Check 5: navigateToScenario() covers adjacency map."""
    if not contract["adjacency"]:
        return {
            "passed": True,
            "details": "No adjacency map in design contract — skipping navigation check",
            "missing": [],
            "skipped": True,
        }

    # Build set of required navigation links
    required_links = set()
    for src, targets in contract["adjacency"].items():
        for dst in targets:
            required_links.add((src.lower(), dst.lower()))

    # Build set of actual navigation links
    actual_targets = {link["to"].lower() for link in extraction["navigation_links"]}

    missing = []
    for src, dst in required_links:
        if dst not in actual_targets:
            missing.append({"from": src, "to": dst})

    return {
        "passed": len(missing) == 0,
        "missing": missing,
        "required_count": len(required_links),
        "covered_targets": sorted(actual_targets),
    }


def check_empty_states(extraction: dict) -> dict:
    """Check 6: Lists/tables have empty state handling."""
    missing = []

    for state in extraction["empty_states"]:
        if state["has_list_or_table"] and not state["has_empty_state"]:
            missing.append(state["scenario"])

    return {
        "passed": len(missing) == 0,
        "missing_for": missing,
        "checked_scenarios": len(extraction["empty_states"]),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def validate(file_path: str, contract_path: str = None) -> dict:
    """Run all 6 validation checks."""
    extraction = extract(file_path)

    contract = {"scenarios": [], "adjacency": {}}
    if contract_path:
        contract = parse_design_contract(contract_path)
    else:
        # Auto-detect: look for 03-design-contract.md in same task directory
        task_dir = os.path.dirname(file_path)
        auto_contract = os.path.join(task_dir, "03-design-contract.md")
        if os.path.isfile(auto_contract):
            contract = parse_design_contract(auto_contract)

    checks = {
        "html_syntax": check_html_syntax(file_path),
        "zds_color_compliance": check_zds_color_compliance(extraction),
        "spacing_compliance": check_spacing_compliance(extraction),
        "scenario_completeness": check_scenario_completeness(extraction, contract),
        "navigation_coverage": check_navigation_coverage(extraction, contract),
        "empty_states": check_empty_states(extraction),
    }

    error_count = sum(1 for c in checks.values() if not c["passed"])
    warning_count = sum(1 for c in checks.values() if c.get("skipped"))

    return {
        "passed": error_count == 0,
        "checks": checks,
        "error_count": error_count,
        "warning_count": warning_count,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python3 validate_html.py <html_file> [--contract <path>]",
        }), file=sys.stderr)
        sys.exit(2)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(json.dumps({"error": f"File not found: {file_path}"}), file=sys.stderr)
        sys.exit(2)

    contract_path = None
    if "--contract" in sys.argv:
        idx = sys.argv.index("--contract")
        if idx + 1 < len(sys.argv):
            contract_path = sys.argv[idx + 1]

    try:
        result = validate(file_path, contract_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["passed"] else 1)
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "type": type(e).__name__,
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
