#!/usr/bin/env python3
"""
dom_extractor.py — DOM structure extractor for Zoom AI-UX Workflow.

Parses an HTML file and outputs a structured JSON representation of the DOM,
including scenario detection, interactive elements, navigation links, forms,
empty states, DOM depth, CSS variables, colors, spacing, and font sizes.

Used as a base module by validate_html.py, cognitive_load_audit.py, and
completeness_lint.py.

Usage:
    python3 .zoom-ai/scripts/dom_extractor.py <html_file>

Exit codes:
    0 = extraction succeeded
    1 = extraction failed
    2 = usage error
"""

import json
import os
import re
import sys

from bs4 import BeautifulSoup, Comment

# ---------------------------------------------------------------------------
# ZDS allowed colors (from .zoom-ai/knowledge/Design.md)
# ---------------------------------------------------------------------------

ZDS_ALLOWED_COLORS = {
    "#0b5cff", "#0047cc", "#ebf0ff", "#e02d3c", "#12805c", "#f5a623",
    "#f7f8fa", "#ffffff", "#232333", "#3e3e4f", "#6e6e7e", "#acacb9",
    "#e8e8ed", "#f0f0f5", "#000000",
}

ZDS_SPECIAL_VALUES = {"transparent", "inherit", "currentcolor", "none", "initial", "unset"}

# ZDS allowed spacing suffixes (Tailwind class number part)
ZDS_ALLOWED_SPACING = {"0", "0.5", "1", "1.5", "2", "3", "4", "6", "8", "12", "px", "auto"}

# Tailwind preset color names to flag as violations
TAILWIND_PRESET_PATTERN = re.compile(
    r"\b(?:red|blue|green|yellow|purple|pink|indigo|gray|slate|zinc|neutral|stone|"
    r"orange|teal|cyan|sky|violet|fuchsia|rose|emerald|lime|amber)-\d{2,3}\b"
)

# Interactive element selectors
INTERACTIVE_TAGS = {"button", "a", "input", "select", "textarea"}
INTERACTIVE_ATTRS = {"onclick", "onchange", "onsubmit"}
INTERACTIVE_ROLES = {"button", "link", "checkbox", "radio", "switch", "slider",
                     "tab", "menuitem", "option", "combobox", "textbox"}

# Hex color pattern
HEX_COLOR_PATTERN = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")

# CSS color property pattern (in style attributes or <style> blocks)
CSS_COLOR_PROPS = re.compile(
    r"(?:color|background-color|background|border-color|border|outline-color|"
    r"fill|stroke|box-shadow|text-shadow|border-top-color|border-right-color|"
    r"border-bottom-color|border-left-color)\s*:\s*([^;]+)",
    re.IGNORECASE,
)

# Tailwind arbitrary color pattern: bg-[#xxx], text-[#xxx], border-[#xxx]
TW_ARBITRARY_COLOR = re.compile(
    r"(?:bg|text|border|ring|outline|shadow|accent|fill|stroke)-\[([^\]]+)\]"
)

# Tailwind spacing pattern: p-N, m-N, gap-N, space-x-N, etc.
TW_SPACING_PATTERN = re.compile(
    r"(?:p|px|py|pt|pr|pb|pl|m|mx|my|mt|mr|mb|ml|gap|gap-x|gap-y|"
    r"space-x|space-y|inset|top|right|bottom|left|w|h|"
    r"min-w|min-h|max-w|max-h)-(\[?\d+(?:\.\d+)?(?:px|rem)?\]?|auto|px|full|screen)"
)

# Font size pattern in Tailwind: text-[Npx], text-xs, text-sm, etc.
TW_FONTSIZE_PATTERN = re.compile(r"text-\[(\d+)px\]")

# CSS font-size pattern
CSS_FONTSIZE_PATTERN = re.compile(r"font-size\s*:\s*(\d+)(?:px)?", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Core extraction functions
# ---------------------------------------------------------------------------

def parse_html(file_path: str) -> BeautifulSoup:
    """Parse HTML file with BeautifulSoup using lxml parser."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return BeautifulSoup(content, "lxml")


def detect_scenarios(soup: BeautifulSoup) -> list:
    """Detect scenario containers by [data-scenario] or id containing 'scenario'."""
    scenarios = []

    # Method 1: data-scenario attribute
    for el in soup.find_all(attrs={"data-scenario": True}):
        sid = el.get("data-scenario", "")
        name = el.get("data-scenario-name", "") or el.get("aria-label", "") or sid
        scenarios.append({
            "id": sid,
            "name": name,
            "element": el,
            "element_count": len(el.find_all(True)),
        })

    if scenarios:
        return scenarios

    # Method 2: id containing "scenario"
    for el in soup.find_all(id=re.compile(r"scenario", re.IGNORECASE)):
        sid = el.get("id", "")
        name = el.get("aria-label", "") or sid
        scenarios.append({
            "id": sid,
            "name": name,
            "element": el,
            "element_count": len(el.find_all(True)),
        })

    # Method 3: sections with id or class containing "scene"/"view"/"page"
    if not scenarios:
        for el in soup.find_all(["section", "div"],
                                id=re.compile(r"scene|view|page", re.IGNORECASE)):
            sid = el.get("id", "")
            scenarios.append({
                "id": sid,
                "name": el.get("aria-label", "") or sid,
                "element": el,
                "element_count": len(el.find_all(True)),
            })

    return scenarios


def find_interactive_elements(root, scenario_id: str = "") -> list:
    """Find all interactive elements within a root element."""
    elements = []

    for tag in root.find_all(True):
        is_interactive = False
        reason = ""

        if tag.name in INTERACTIVE_TAGS:
            # Skip links without href
            if tag.name == "a" and not tag.get("href"):
                if not tag.get("onclick") and tag.get("role") not in INTERACTIVE_ROLES:
                    continue
            is_interactive = True
            reason = f"tag:{tag.name}"

        if not is_interactive:
            for attr in INTERACTIVE_ATTRS:
                if tag.get(attr):
                    is_interactive = True
                    reason = f"attr:{attr}"
                    break

        if not is_interactive:
            role = tag.get("role", "").lower()
            if role in INTERACTIVE_ROLES:
                is_interactive = True
                reason = f"role:{role}"

        if not is_interactive:
            if tag.get("tabindex") and tag.get("tabindex") != "-1":
                is_interactive = True
                reason = "tabindex"

        if is_interactive:
            text = tag.get_text(strip=True)[:80]
            elements.append({
                "tag": tag.name,
                "text": text,
                "scenario": scenario_id,
                "reason": reason,
                "id": tag.get("id", ""),
                "classes": " ".join(tag.get("class", [])),
            })

    return elements


def find_navigation_links(soup: BeautifulSoup) -> list:
    """Find navigateToScenario() calls and similar navigation patterns."""
    links = []
    nav_pattern = re.compile(r"navigateToScenario\s*\(\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)

    # Search in onclick attributes
    for el in soup.find_all(attrs={"onclick": True}):
        onclick = el.get("onclick", "")
        for match in nav_pattern.finditer(onclick):
            target = match.group(1)
            # Find which scenario this element belongs to
            parent_scenario = ""
            parent = el
            while parent:
                if parent.get("data-scenario"):
                    parent_scenario = parent.get("data-scenario")
                    break
                if parent.get("id") and "scenario" in parent.get("id", "").lower():
                    parent_scenario = parent.get("id")
                    break
                parent = parent.parent
            links.append({"from": parent_scenario, "to": target})

    # Search in <script> blocks
    for script in soup.find_all("script"):
        if script.string:
            for match in nav_pattern.finditer(script.string):
                links.append({"from": "", "to": match.group(1)})

    # Search href="#scenario-xxx" patterns
    for a in soup.find_all("a", href=re.compile(r"#scenario|#scene|#view")):
        href = a.get("href", "")
        target = href.lstrip("#")
        parent_scenario = ""
        parent = a
        while parent:
            if parent.get("data-scenario"):
                parent_scenario = parent.get("data-scenario")
                break
            if parent.get("id") and "scenario" in parent.get("id", "").lower():
                parent_scenario = parent.get("id")
                break
            parent = parent.parent
        links.append({"from": parent_scenario, "to": target})

    return links


def find_forms(root, scenario_id: str = "") -> list:
    """Find form elements and their fields."""
    forms = []
    for form in root.find_all("form"):
        fields = []
        for inp in form.find_all(["input", "select", "textarea"]):
            inp_type = inp.get("type", "text")
            if inp_type in ("hidden", "submit"):
                continue
            fields.append({
                "tag": inp.name,
                "type": inp_type,
                "name": inp.get("name", ""),
                "id": inp.get("id", ""),
            })
        forms.append({
            "scenario": scenario_id,
            "field_count": len(fields),
            "fields": fields,
        })

    # Also detect standalone inputs not in forms
    standalone = root.find_all(["input", "select", "textarea"], recursive=True)
    form_inputs = set()
    for form in root.find_all("form"):
        for inp in form.find_all(["input", "select", "textarea"]):
            form_inputs.add(id(inp))
    standalone_fields = [
        inp for inp in standalone
        if id(inp) not in form_inputs and inp.get("type") not in ("hidden", "submit")
    ]
    if standalone_fields:
        fields = [{
            "tag": inp.name,
            "type": inp.get("type", "text"),
            "name": inp.get("name", ""),
            "id": inp.get("id", ""),
        } for inp in standalone_fields]
        forms.append({
            "scenario": scenario_id,
            "field_count": len(fields),
            "fields": fields,
            "standalone": True,
        })

    return forms


def detect_empty_states(root, scenario_id: str = "") -> dict:
    """Check if a scenario has empty state handling."""
    # Look for elements with class/id/data-* containing "empty"
    empty_markers = root.find_all(
        True,
        class_=re.compile(r"empty[-_]?state|no[-_]?data|no[-_]?results|placeholder", re.IGNORECASE)
    )
    if not empty_markers:
        empty_markers = root.find_all(
            True,
            id=re.compile(r"empty[-_]?state|no[-_]?data|no[-_]?results", re.IGNORECASE)
        )
    if not empty_markers:
        empty_markers = root.find_all(attrs={"data-empty-state": True})

    # Check for ZDS empty-state component reference
    if not empty_markers:
        for el in root.find_all(True):
            classes = " ".join(el.get("class", []))
            if "zds-empty" in classes.lower() or "empty-state" in classes.lower():
                empty_markers = [el]
                break

    has_list_or_table = bool(root.find_all(["table", "ul", "ol"]) or
                            root.find_all(True, class_=re.compile(r"list|grid|table", re.IGNORECASE)))

    return {
        "scenario": scenario_id,
        "has_list_or_table": has_list_or_table,
        "has_empty_state": bool(empty_markers),
        "present": not has_list_or_table or bool(empty_markers),
    }


def compute_dom_depth(element, current_depth: int = 0) -> int:
    """Compute maximum DOM nesting depth from an element."""
    max_depth = current_depth
    for child in element.children:
        if hasattr(child, "children") and child.name:
            child_depth = compute_dom_depth(child, current_depth + 1)
            max_depth = max(max_depth, child_depth)
    return max_depth


def extract_css_variables(soup: BeautifulSoup) -> list:
    """Extract CSS custom property declarations from <style> blocks."""
    variables = []
    var_pattern = re.compile(r"(--[\w-]+)\s*:")
    for style in soup.find_all("style"):
        if style.string:
            for match in var_pattern.finditer(style.string):
                var_name = match.group(1)
                if var_name not in variables:
                    variables.append(var_name)
    return variables


def extract_colors(soup: BeautifulSoup) -> list:
    """Extract all hex colors used in the document."""
    colors = set()

    # From <style> blocks
    for style in soup.find_all("style"):
        if style.string:
            for match in HEX_COLOR_PATTERN.finditer(style.string):
                colors.add(match.group(0).lower())

    # From inline styles
    for el in soup.find_all(True, style=True):
        style_val = el.get("style", "")
        for match in HEX_COLOR_PATTERN.finditer(style_val):
            colors.add(match.group(0).lower())

    # From Tailwind arbitrary values: bg-[#xxx], text-[#xxx]
    for el in soup.find_all(True, class_=True):
        classes = " ".join(el.get("class", []))
        for match in TW_ARBITRARY_COLOR.finditer(classes):
            val = match.group(1)
            hex_match = HEX_COLOR_PATTERN.search(val)
            if hex_match:
                colors.add(hex_match.group(0).lower())

    return sorted(colors)


def extract_spacing_classes(soup: BeautifulSoup) -> list:
    """Extract Tailwind spacing classes used in the document."""
    spacings = set()
    for el in soup.find_all(True, class_=True):
        classes = " ".join(el.get("class", []))
        for match in TW_SPACING_PATTERN.finditer(classes):
            spacings.add(match.group(0))
    return sorted(spacings)


def extract_font_sizes(soup: BeautifulSoup) -> list:
    """Extract font sizes used (from Tailwind classes and inline styles)."""
    sizes = set()

    # Tailwind text-[Npx]
    for el in soup.find_all(True, class_=True):
        classes = " ".join(el.get("class", []))
        for match in TW_FONTSIZE_PATTERN.finditer(classes):
            sizes.add(int(match.group(1)))

    # Inline style font-size
    for el in soup.find_all(True, style=True):
        style_val = el.get("style", "")
        for match in CSS_FONTSIZE_PATTERN.finditer(style_val):
            sizes.add(int(match.group(1)))

    # <style> block font-size
    for style in soup.find_all("style"):
        if style.string:
            for match in CSS_FONTSIZE_PATTERN.finditer(style.string):
                sizes.add(int(match.group(1)))

    return sorted(sizes)


def count_hidden_elements(soup: BeautifulSoup) -> int:
    """Count elements with display:none or visibility:hidden."""
    count = 0
    hidden_pattern = re.compile(r"display\s*:\s*none|visibility\s*:\s*hidden", re.IGNORECASE)

    for el in soup.find_all(True, style=True):
        if hidden_pattern.search(el.get("style", "")):
            count += 1

    # Also check Tailwind hidden class
    for el in soup.find_all(True, class_=re.compile(r"\bhidden\b")):
        count += 1

    return count


def find_tailwind_preset_violations(soup: BeautifulSoup) -> list:
    """Find usage of Tailwind preset color names (e.g., blue-500)."""
    violations = []
    for el in soup.find_all(True, class_=True):
        classes = " ".join(el.get("class", []))
        for match in TAILWIND_PRESET_PATTERN.finditer(classes):
            violations.append({
                "class": match.group(0),
                "element": el.name,
                "id": el.get("id", ""),
            })
    return violations


def find_primary_actions(root) -> list:
    """Find primary action buttons (CTA) within a root element."""
    primary = []
    for btn in root.find_all(["button", "a"]):
        classes = " ".join(btn.get("class", []))
        # Detect primary by ZDS blue color or explicit primary class
        if ("#0b5cff" in classes.lower() or
            "primary" in classes.lower() or
            "bg-[#0B5CFF]" in classes or
            "bg-[#0b5cff]" in classes or
            btn.get("data-variant") == "primary"):
            primary.append({
                "tag": btn.name,
                "text": btn.get_text(strip=True)[:50],
                "id": btn.get("id", ""),
            })
    return primary


def find_modals(root) -> list:
    """Find modal/dialog elements within a root element."""
    modals = []
    for el in root.find_all(True, role="dialog"):
        modals.append(el)
    for el in root.find_all(True, class_=re.compile(r"modal|dialog", re.IGNORECASE)):
        if el not in modals:
            modals.append(el)
    return modals


def max_children_count(root) -> int:
    """Find the maximum number of direct children any container has."""
    max_count = 0
    for el in root.find_all(True):
        children = [c for c in el.children if hasattr(c, "name") and c.name]
        max_count = max(max_count, len(children))
    return max_count


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract(file_path: str) -> dict:
    """Extract full DOM structure analysis from an HTML file."""
    soup = parse_html(file_path)
    body = soup.find("body") or soup

    scenarios = detect_scenarios(soup)

    # If no scenarios detected, treat entire body as one implicit scenario
    if not scenarios:
        scenarios = [{
            "id": "__root__",
            "name": "root",
            "element": body,
            "element_count": len(body.find_all(True)),
        }]

    # Per-scenario analysis
    all_interactive = []
    all_forms = []
    all_empty_states = []
    per_scenario_depth = {}
    per_scenario_primary = {}
    per_scenario_modals = {}
    per_scenario_max_children = {}

    for sc in scenarios:
        el = sc["element"]
        sid = sc["id"]

        interactive = find_interactive_elements(el, sid)
        all_interactive.extend(interactive)

        forms = find_forms(el, sid)
        all_forms.extend(forms)

        empty = detect_empty_states(el, sid)
        all_empty_states.append(empty)

        depth = compute_dom_depth(el)
        per_scenario_depth[sid] = depth

        primary = find_primary_actions(el)
        per_scenario_primary[sid] = primary

        modals = find_modals(el)
        per_scenario_modals[sid] = len(modals)

        per_scenario_max_children[sid] = max_children_count(el)

    nav_links = find_navigation_links(soup)
    css_vars = extract_css_variables(soup)
    colors = extract_colors(soup)
    spacing = extract_spacing_classes(soup)
    font_sizes = extract_font_sizes(soup)
    hidden_count = count_hidden_elements(soup)
    total_elements = len(body.find_all(True))
    tw_violations = find_tailwind_preset_violations(soup)

    max_depth = max(per_scenario_depth.values()) if per_scenario_depth else 0

    return {
        "file": file_path,
        "scenarios": [
            {"id": s["id"], "name": s["name"], "element_count": s["element_count"]}
            for s in scenarios
        ],
        "interactive_elements": all_interactive,
        "interactive_count_per_scenario": {
            sc["id"]: len([e for e in all_interactive if e["scenario"] == sc["id"]])
            for sc in scenarios
        },
        "primary_actions_per_scenario": {
            sid: len(acts) for sid, acts in per_scenario_primary.items()
        },
        "navigation_links": nav_links,
        "forms": all_forms,
        "form_fields_per_scenario": {
            sc["id"]: sum(f["field_count"] for f in all_forms if f["scenario"] == sc["id"])
            for sc in scenarios
        },
        "empty_states": all_empty_states,
        "dom_depth": {
            "max": max_depth,
            "per_scenario": per_scenario_depth,
        },
        "modals_per_scenario": per_scenario_modals,
        "max_children_per_scenario": per_scenario_max_children,
        "css_variables": css_vars,
        "colors_used": colors,
        "tailwind_preset_violations": tw_violations,
        "spacing_classes": spacing,
        "font_sizes": font_sizes,
        "hidden_elements": hidden_count,
        "total_elements": total_elements,
        "hidden_element_ratio": round(hidden_count / total_elements, 3) if total_elements > 0 else 0,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: python3 dom_extractor.py <html_file>",
        }), file=sys.stderr)
        sys.exit(2)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(json.dumps({
            "error": f"File not found: {file_path}",
        }), file=sys.stderr)
        sys.exit(2)

    try:
        result = extract(file_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({
            "error": str(e),
            "type": type(e).__name__,
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
