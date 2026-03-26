#!/usr/bin/env python3
"""
cognitive_load_audit.py — Cognitive load auditor for HarnessDesign AI-UX Workflow.

Reads ux-heuristics.yaml thresholds and audits an HTML prototype for cognitive
load violations across 5 categories: cognitive_load, dom_structure, interaction,
visual_hierarchy, edge_states.

Usage:
    python3 .harnessdesign/scripts/cognitive_load_audit.py <html_file> [--heuristics <yaml_path>]

Default heuristics path: .harnessdesign/knowledge/rules/ux-heuristics.yaml
(auto-resolved relative to script location)

Exit codes:
    0 = audit passed (no errors or criticals)
    1 = audit found violations
    2 = usage error
"""

import json
import os
import re
import sys

import yaml

# Add script directory to path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dom_extractor import extract, parse_html

# ---------------------------------------------------------------------------
# Default heuristics path resolution
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_HEURISTICS = os.path.normpath(
    os.path.join(SCRIPT_DIR, "..", "knowledge", "rules", "ux-heuristics.yaml")
)


def load_heuristics(path: str) -> dict:
    """Load ux-heuristics.yaml configuration."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------------------------------------------------------------------------
# Severity calculation
# ---------------------------------------------------------------------------

def compute_severity(actual: float, limit: float, severity_config: dict) -> str:
    """Compute severity level based on threshold ratios."""
    if limit <= 0:
        return "pass"

    ratio = actual / limit

    if ratio <= 1.0:
        return "pass"
    elif ratio <= severity_config.get("warning_threshold_ratio", 1.2):
        return "warning"
    elif ratio <= severity_config.get("error_threshold_ratio", 1.5):
        return "error"
    else:
        return "critical"


def make_violation(category: str, metric: str, scenario: str,
                   limit, actual, severity: str, ratio: float) -> dict:
    """Create a structured violation entry."""
    return {
        "category": category,
        "metric": metric,
        "scenario": scenario,
        "limit": limit,
        "actual": actual,
        "severity": severity,
        "ratio": round(ratio, 2),
    }


# ---------------------------------------------------------------------------
# Audit functions per category
# ---------------------------------------------------------------------------

def audit_cognitive_load(extraction: dict, config: dict, severity_cfg: dict) -> list:
    """Audit cognitive load metrics per scenario."""
    violations = []
    cl = config.get("cognitive_load", {})

    max_interactive = cl.get("max_interactive_elements_per_view", 12)
    max_primary = cl.get("max_primary_actions_per_view", 3)
    max_form_fields = cl.get("max_form_fields_per_page", 8)

    for sc in extraction["scenarios"]:
        sid = sc["id"]

        # Interactive elements per view
        count = extraction["interactive_count_per_scenario"].get(sid, 0)
        if count > max_interactive:
            ratio = count / max_interactive
            sev = compute_severity(count, max_interactive, severity_cfg)
            violations.append(make_violation(
                "cognitive_load", "max_interactive_elements_per_view",
                sid, max_interactive, count, sev, ratio
            ))

        # Primary actions per view
        primary_count = extraction["primary_actions_per_scenario"].get(sid, 0)
        if primary_count > max_primary:
            ratio = primary_count / max_primary
            sev = compute_severity(primary_count, max_primary, severity_cfg)
            violations.append(make_violation(
                "cognitive_load", "max_primary_actions_per_view",
                sid, max_primary, primary_count, sev, ratio
            ))

        # Form fields per page
        field_count = extraction["form_fields_per_scenario"].get(sid, 0)
        if field_count > max_form_fields:
            ratio = field_count / max_form_fields
            sev = compute_severity(field_count, max_form_fields, severity_cfg)
            violations.append(make_violation(
                "cognitive_load", "max_form_fields_per_page",
                sid, max_form_fields, field_count, sev, ratio
            ))

    return violations


def audit_dom_structure(extraction: dict, config: dict, severity_cfg: dict) -> list:
    """Audit DOM structure metrics."""
    violations = []
    ds = config.get("dom_structure", {})

    max_depth = ds.get("max_nesting_depth", 10)
    max_children = ds.get("max_children_per_container", 15)
    max_hidden_ratio = ds.get("max_hidden_element_ratio", 0.3)

    # Nesting depth per scenario
    for sid, depth in extraction["dom_depth"]["per_scenario"].items():
        if depth > max_depth:
            ratio = depth / max_depth
            sev = compute_severity(depth, max_depth, severity_cfg)
            violations.append(make_violation(
                "dom_structure", "max_nesting_depth",
                sid, max_depth, depth, sev, ratio
            ))

    # Max children per container per scenario
    for sid, mc in extraction["max_children_per_scenario"].items():
        if mc > max_children:
            ratio = mc / max_children
            sev = compute_severity(mc, max_children, severity_cfg)
            violations.append(make_violation(
                "dom_structure", "max_children_per_container",
                sid, max_children, mc, sev, ratio
            ))

    # Hidden element ratio (global)
    hidden_ratio = extraction["hidden_element_ratio"]
    if hidden_ratio > max_hidden_ratio:
        ratio = hidden_ratio / max_hidden_ratio
        sev = compute_severity(hidden_ratio, max_hidden_ratio, severity_cfg)
        violations.append(make_violation(
            "dom_structure", "max_hidden_element_ratio",
            "__global__", max_hidden_ratio, hidden_ratio, sev, ratio
        ))

    return violations


def audit_interaction(extraction: dict, config: dict, severity_cfg: dict) -> list:
    """Audit interaction pattern metrics."""
    violations = []
    ia = config.get("interaction", {})

    max_modal_nesting = ia.get("max_modal_nesting", 2)

    # Modal nesting per scenario
    for sid, modal_count in extraction["modals_per_scenario"].items():
        if modal_count > max_modal_nesting:
            ratio = modal_count / max_modal_nesting
            sev = compute_severity(modal_count, max_modal_nesting, severity_cfg)
            violations.append(make_violation(
                "interaction", "max_modal_nesting",
                sid, max_modal_nesting, modal_count, sev, ratio
            ))

    return violations


def audit_visual_hierarchy(extraction: dict, config: dict, severity_cfg: dict) -> list:
    """Audit visual hierarchy metrics."""
    violations = []
    vh = config.get("visual_hierarchy", {})

    max_font_variants = vh.get("max_font_size_variants", 5)
    max_color_variants = vh.get("max_color_variants", 6)

    # Font size variants (global)
    font_count = len(extraction["font_sizes"])
    if font_count > max_font_variants:
        ratio = font_count / max_font_variants
        sev = compute_severity(font_count, max_font_variants, severity_cfg)
        violations.append(make_violation(
            "visual_hierarchy", "max_font_size_variants",
            "__global__", max_font_variants, font_count, sev, ratio
        ))

    # Color variants (global, non-grayscale)
    # Filter out grayscale colors (#xxx where all channels are similar)
    non_gray = []
    for c in extraction["colors_used"]:
        hex_val = c.lstrip("#").lower()
        if len(hex_val) == 6:
            r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
            max_diff = max(abs(r - g), abs(g - b), abs(r - b))
            if max_diff > 20:  # Not grayscale
                non_gray.append(c)
        elif len(hex_val) == 3:
            r, g, b = int(hex_val[0]*2, 16), int(hex_val[1]*2, 16), int(hex_val[2]*2, 16)
            max_diff = max(abs(r - g), abs(g - b), abs(r - b))
            if max_diff > 20:
                non_gray.append(c)

    color_count = len(non_gray)
    if color_count > max_color_variants:
        ratio = color_count / max_color_variants
        sev = compute_severity(color_count, max_color_variants, severity_cfg)
        violations.append(make_violation(
            "visual_hierarchy", "max_color_variants",
            "__global__", max_color_variants, color_count, sev, ratio
        ))

    return violations


def audit_edge_states(extraction: dict, config: dict) -> list:
    """Audit edge state requirements (boolean checks)."""
    violations = []
    es = config.get("edge_states", {})

    if es.get("require_empty_state_for_lists", True):
        for state in extraction["empty_states"]:
            if state["has_list_or_table"] and not state["has_empty_state"]:
                violations.append({
                    "category": "edge_states",
                    "metric": "require_empty_state_for_lists",
                    "scenario": state["scenario"],
                    "severity": "error",
                    "message": f"Scenario '{state['scenario']}' has list/table but no empty state",
                })

    return violations


# ---------------------------------------------------------------------------
# Main audit
# ---------------------------------------------------------------------------

def audit(file_path: str, heuristics_path: str = None) -> dict:
    """Run full cognitive load audit."""
    if heuristics_path is None:
        heuristics_path = DEFAULT_HEURISTICS

    config = load_heuristics(heuristics_path)
    extraction = extract(file_path)
    severity_cfg = config.get("severity", {})

    all_violations = []
    all_violations.extend(audit_cognitive_load(extraction, config, severity_cfg))
    all_violations.extend(audit_dom_structure(extraction, config, severity_cfg))
    all_violations.extend(audit_interaction(extraction, config, severity_cfg))
    all_violations.extend(audit_visual_hierarchy(extraction, config, severity_cfg))
    all_violations.extend(audit_edge_states(extraction, config))

    # Compute summary
    summary = {"pass": 0, "warning": 0, "error": 0, "critical": 0}
    for v in all_violations:
        sev = v.get("severity", "error")
        summary[sev] = summary.get(sev, 0) + 1

    # Total metrics checked (rough count)
    total_checks = (
        len(extraction["scenarios"]) * 3  # cognitive_load: 3 metrics per scenario
        + len(extraction["dom_depth"]["per_scenario"]) * 2  # dom_structure: 2 per scenario
        + 1  # hidden_element_ratio global
        + len(extraction["modals_per_scenario"])  # interaction
        + 2  # visual_hierarchy: font + color global
        + len(extraction["empty_states"])  # edge_states
    )
    summary["pass"] = total_checks - len(all_violations)

    has_blocking = summary.get("critical", 0) > 0

    return {
        "passed": summary["error"] == 0 and summary["critical"] == 0,
        "blocking": has_blocking,
        "summary": summary,
        "violations": all_violations,
        "heuristics_file": heuristics_path,
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python3 cognitive_load_audit.py <html_file> [--heuristics <yaml_path>]",
        }), file=sys.stderr)
        sys.exit(2)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(json.dumps({"error": f"File not found: {file_path}"}), file=sys.stderr)
        sys.exit(2)

    heuristics_path = None
    if "--heuristics" in sys.argv:
        idx = sys.argv.index("--heuristics")
        if idx + 1 < len(sys.argv):
            heuristics_path = sys.argv[idx + 1]

    try:
        result = audit(file_path, heuristics_path)
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
