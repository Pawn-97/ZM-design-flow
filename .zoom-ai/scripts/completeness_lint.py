#!/usr/bin/env python3
"""
completeness_lint.py — DesignContract completeness linter for Zoom AI-UX Workflow.

Verifies that an HTML prototype covers all requirements specified in the
DesignContract (03-design-contract.md):
1. Scenario coverage — all scenario containers present
2. Interaction commitments — commitments have corresponding DOM elements
3. Navigation topology — adjacency links have interactive triggers
4. Shared state model — JS variables declared
5. Edge states — empty states, error handling, write confirmations
6. Interactive states — hover/focus/disabled CSS rules

Usage:
    python3 .zoom-ai/scripts/completeness_lint.py <html_file> <design_contract_path>

Exit codes:
    0 = all checks passed
    1 = completeness gaps found
    2 = usage error
"""

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dom_extractor import extract, parse_html


# ---------------------------------------------------------------------------
# DesignContract parser
# ---------------------------------------------------------------------------

def parse_design_contract(path: str) -> dict:
    """Parse 03-design-contract.md into structured data."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    contract = {
        "scenarios": [],
        "interaction_commitments": {},  # {scenario_id: [commitment_text, ...]}
        "adjacency": {},               # {src: [dst, ...]}
        "shared_state": [],             # [{name, type, produced_by, consumed_by}]
        "global_constraints": [],       # [constraint_text, ...]
        "edge_cases": {},               # {scenario_id: [edge_case_text, ...]}
    }

    # --- Parse scenarios ---
    # Pattern: scenario_id or scenario-id in headers/lists
    current_scenario = None
    in_commitments = False
    in_edge_cases = False
    in_constraints = False
    in_shared_state = False
    in_adjacency = False

    lines = content.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect scenario headers
        sc_header = re.match(
            r"#{2,4}\s+.*?(scenario[-_]?\d+\w*)",
            stripped, re.IGNORECASE
        )
        if sc_header:
            sid = sc_header.group(1)
            if sid not in contract["scenarios"]:
                contract["scenarios"].append(sid)
            current_scenario = sid
            in_commitments = False
            in_edge_cases = False
            continue

        # Detect scenario_id in key-value format
        sc_kv = re.match(
            r"[-*]\s*(?:scenario[_-]?id|id)\s*[:：]\s*['\"]?([a-zA-Z0-9_-]+)",
            stripped, re.IGNORECASE
        )
        if sc_kv:
            sid = sc_kv.group(1)
            if sid not in contract["scenarios"]:
                contract["scenarios"].append(sid)
            current_scenario = sid
            continue

        # Detect section markers
        lower = stripped.lower()
        if "interaction_commitment" in lower or "交互承诺" in lower:
            in_commitments = True
            in_edge_cases = False
            in_constraints = False
            in_shared_state = False
            in_adjacency = False
            continue
        if "edge_case" in lower or "边缘" in lower:
            in_edge_cases = True
            in_commitments = False
            in_constraints = False
            continue
        if "global_constraint" in lower or "global constraint" in lower or "全局约束" in lower:
            in_constraints = True
            in_commitments = False
            in_edge_cases = False
            in_shared_state = False
            in_adjacency = False
            current_scenario = None
            continue
        if "shared_state" in lower or "shared state" in lower or "共享状态" in lower:
            in_shared_state = True
            in_constraints = False
            in_commitments = False
            in_edge_cases = False
            in_adjacency = False
            continue
        if "navigation_topology" in lower or "adjacency" in lower or "导航拓扑" in lower:
            in_adjacency = True
            in_shared_state = False
            in_constraints = False
            in_commitments = False
            in_edge_cases = False
            continue

        # Empty line resets context within sub-sections
        if not stripped:
            continue

        # If starts with new header, reset sub-section flags
        if stripped.startswith("#"):
            in_commitments = False
            in_edge_cases = False
            in_constraints = False
            in_shared_state = False
            in_adjacency = False
            continue

        # Collect items
        list_item = re.match(r"[-*]\s+(.+)", stripped)
        numbered_item = re.match(r"\d+\.\s+(.+)", stripped)
        item_text = None
        if list_item:
            item_text = list_item.group(1).strip()
        elif numbered_item:
            item_text = numbered_item.group(1).strip()

        if item_text:
            if in_commitments and current_scenario:
                contract["interaction_commitments"].setdefault(current_scenario, [])
                contract["interaction_commitments"][current_scenario].append(item_text)
            elif in_edge_cases and current_scenario:
                contract["edge_cases"].setdefault(current_scenario, [])
                contract["edge_cases"][current_scenario].append(item_text)
            elif in_constraints:
                contract["global_constraints"].append(item_text)
            elif in_shared_state:
                # Parse: name: xxx, type: yyy or just the item text
                state_match = re.match(
                    r"(?:name\s*[:：]\s*)?(\w+).*?(?:type\s*[:：]\s*(\w+))?",
                    item_text, re.IGNORECASE
                )
                if state_match:
                    contract["shared_state"].append({
                        "name": state_match.group(1),
                        "type": state_match.group(2) or "unknown",
                        "raw": item_text,
                    })

        # Parse adjacency: scenario-1 → scenario-2
        adj_match = re.match(
            r"[-*]?\s*([a-zA-Z0-9_-]+)\s*(?:→|->|=>)\s*([a-zA-Z0-9_-]+)",
            stripped
        )
        if adj_match and in_adjacency:
            src, dst = adj_match.group(1), adj_match.group(2)
            contract["adjacency"].setdefault(src, [])
            if dst not in contract["adjacency"][src]:
                contract["adjacency"][src].append(dst)

    return contract


# ---------------------------------------------------------------------------
# Lint checks
# ---------------------------------------------------------------------------

def lint_scenarios(extraction: dict, contract: dict) -> dict:
    """Check: all contract scenarios have HTML containers."""
    html_ids = {s["id"].lower() for s in extraction["scenarios"]}
    missing = [s for s in contract["scenarios"] if s.lower() not in html_ids]

    return {
        "total": len(contract["scenarios"]),
        "covered": len(contract["scenarios"]) - len(missing),
        "missing": missing,
    }


def lint_interaction_commitments(extraction: dict, contract: dict) -> dict:
    """Check: interaction commitments have corresponding elements.

    Uses keyword matching — extracts key nouns/verbs from commitment text
    and searches for them in interactive element text/classes/ids.
    """
    total = 0
    covered = 0
    uncovered = []

    # Build searchable index from interactive elements
    search_index = ""
    for el in extraction["interactive_elements"]:
        search_index += f" {el['text']} {el['id']} {el['classes']}"
    search_index = search_index.lower()

    # Also include all text content from HTML
    # We approximate by checking element text from extraction
    for sc_id, commitments in contract["interaction_commitments"].items():
        for commitment in commitments:
            total += 1
            # Extract meaningful keywords (Chinese and English)
            keywords = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z]{3,}", commitment)
            # Check if any keyword appears in the search index
            found = any(kw.lower() in search_index for kw in keywords if len(kw) >= 2)
            if found:
                covered += 1
            else:
                uncovered.append({
                    "scenario": sc_id,
                    "commitment": commitment,
                })

    return {
        "total": total,
        "covered": covered,
        "uncovered": uncovered,
    }


def lint_navigation(extraction: dict, contract: dict) -> dict:
    """Check: adjacency links have interactive triggers."""
    if not contract["adjacency"]:
        return {"total": 0, "covered": 0, "missing": []}

    required = set()
    for src, targets in contract["adjacency"].items():
        for dst in targets:
            required.add((src.lower(), dst.lower()))

    actual_targets = {link["to"].lower() for link in extraction["navigation_links"]}

    missing = []
    for src, dst in required:
        if dst not in actual_targets:
            missing.append({"from": src, "to": dst})

    return {
        "total": len(required),
        "covered": len(required) - len(missing),
        "missing": missing,
    }


def lint_shared_state(extraction: dict, contract: dict, file_path: str) -> dict:
    """Check: shared state variables declared in JS."""
    if not contract["shared_state"]:
        return {"total": 0, "covered": 0, "missing": []}

    # Read HTML file to search JS content
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Extract all <script> content
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")
    js_content = ""
    for script in soup.find_all("script"):
        if script.string:
            js_content += " " + script.string

    js_lower = js_content.lower()

    missing = []
    covered = 0
    for state in contract["shared_state"]:
        name = state["name"].lower()
        # Check for variable declaration or usage
        if name in js_lower:
            covered += 1
        else:
            # Also check camelCase and snake_case variants
            camel = re.sub(r"[-_](\w)", lambda m: m.group(1).upper(), name)
            if camel in js_lower:
                covered += 1
            else:
                missing.append(state["name"])

    return {
        "total": len(contract["shared_state"]),
        "covered": covered,
        "missing": missing,
    }


def lint_edge_states(extraction: dict, contract: dict) -> dict:
    """Check: edge cases have corresponding implementations."""
    total = 0
    covered = 0
    missing = []

    # Check empty states for lists
    for state in extraction["empty_states"]:
        if state["has_list_or_table"]:
            total += 1
            if state["has_empty_state"]:
                covered += 1
            else:
                missing.append({
                    "type": "empty_state",
                    "scenario": state["scenario"],
                    "message": "List/table without empty state",
                })

    # Check contract edge cases
    for sc_id, cases in contract["edge_cases"].items():
        for case in cases:
            total += 1
            # Simple heuristic: check if keywords from the edge case appear in the HTML
            keywords = re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z]{3,}", case)
            # Build text from scenario elements
            sc_elements = [
                el for el in extraction["interactive_elements"]
                if el["scenario"].lower() == sc_id.lower()
            ]
            sc_text = " ".join(
                f"{el['text']} {el['id']} {el['classes']}" for el in sc_elements
            ).lower()

            found = any(kw.lower() in sc_text for kw in keywords if len(kw) >= 2)
            if found:
                covered += 1
            else:
                missing.append({
                    "type": "edge_case",
                    "scenario": sc_id,
                    "case": case,
                })

    return {
        "total": total,
        "covered": covered,
        "missing": missing,
    }


def lint_interactive_states(file_path: str) -> dict:
    """Check: buttons/inputs have hover/focus/disabled CSS rules."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract <style> content
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, "lxml")
    css_content = ""
    for style in soup.find_all("style"):
        if style.string:
            css_content += " " + style.string

    # Also check Tailwind classes for hover:/focus:/disabled:
    classes_content = ""
    for el in soup.find_all(True, class_=True):
        classes_content += " " + " ".join(el.get("class", []))

    has_hover = bool(
        re.search(r":hover\s*\{", css_content) or
        "hover:" in classes_content
    )
    has_focus = bool(
        re.search(r":focus\s*\{", css_content) or
        "focus:" in classes_content
    )
    has_disabled = bool(
        re.search(r":disabled\s*\{|\.disabled\s*\{|\[disabled\]", css_content) or
        "disabled:" in classes_content
    )

    missing = []
    if not has_hover:
        missing.append("hover")
    if not has_focus:
        missing.append("focus")
    if not has_disabled:
        missing.append("disabled")

    return {
        "has_hover": has_hover,
        "has_focus": has_focus,
        "has_disabled": has_disabled,
        "missing_states": missing,
        "passed": len(missing) == 0,
    }


# ---------------------------------------------------------------------------
# Main lint
# ---------------------------------------------------------------------------

def lint(file_path: str, contract_path: str) -> dict:
    """Run full completeness lint."""
    extraction = extract(file_path)
    contract = parse_design_contract(contract_path)

    scenarios = lint_scenarios(extraction, contract)
    commitments = lint_interaction_commitments(extraction, contract)
    navigation = lint_navigation(extraction, contract)
    shared_state = lint_shared_state(extraction, contract, file_path)
    edge_states = lint_edge_states(extraction, contract)
    interactive_states = lint_interactive_states(file_path)

    # Count errors and warnings
    error_count = 0
    warning_count = 0

    if scenarios["missing"]:
        error_count += len(scenarios["missing"])
    if commitments["uncovered"]:
        # Uncovered commitments are warnings (heuristic matching may miss)
        warning_count += len(commitments["uncovered"])
    if navigation["missing"]:
        error_count += len(navigation["missing"])
    if shared_state["missing"]:
        warning_count += len(shared_state["missing"])
    if edge_states["missing"]:
        error_count += len(edge_states["missing"])
    if interactive_states["missing_states"]:
        warning_count += len(interactive_states["missing_states"])

    return {
        "passed": error_count == 0,
        "coverage": {
            "scenarios": scenarios,
            "interaction_commitments": commitments,
            "navigation_links": navigation,
            "shared_state": shared_state,
            "edge_states": edge_states,
            "interactive_states": interactive_states,
        },
        "error_count": error_count,
        "warning_count": warning_count,
        "contract_file": contract_path,
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: python3 completeness_lint.py <html_file> <design_contract_path>",
        }), file=sys.stderr)
        sys.exit(2)

    file_path = sys.argv[1]
    contract_path = sys.argv[2]

    if not os.path.isfile(file_path):
        print(json.dumps({"error": f"File not found: {file_path}"}), file=sys.stderr)
        sys.exit(2)
    if not os.path.isfile(contract_path):
        print(json.dumps({"error": f"Contract not found: {contract_path}"}), file=sys.stderr)
        sys.exit(2)

    try:
        result = lint(file_path, contract_path)
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
