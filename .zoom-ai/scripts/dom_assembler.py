#!/usr/bin/env python3
"""
dom_assembler.py — Deterministic DOM surgery tool for Zoom AI-UX Workflow.

Receives JSON operation instructions and executes structural modifications on
an HTML file using BeautifulSoup. Supports: remove, insert, update, replace.

Used by the Alchemist Skill (Phase 4) review feedback loop to apply precise
DOM patches without regenerating the entire HTML.

Usage:
    python3 .zoom-ai/scripts/dom_assembler.py <html_file> <operations_json>

    operations_json can be:
    - A file path to a JSON file
    - A JSON string (auto-detected if starts with '[' or '{')

Operation format:
    [
      {"action": "remove",  "target": "#btn-123"},
      {"action": "insert",  "target": "#container", "position": "append", "content": "<div>...</div>"},
      {"action": "update",  "target": ".card-title", "attributes": {"class": "..."}, "text": "New"},
      {"action": "replace", "target": "#old", "content": "<section>...</section>"}
    ]

Exit codes:
    0 = all operations succeeded
    1 = one or more operations failed
    2 = usage error
"""

import json
import os
import shutil
import sys

from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# HTML parser
# ---------------------------------------------------------------------------

def load_html(file_path: str) -> tuple:
    """Load HTML file and return (content_string, soup)."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    soup = BeautifulSoup(content, "lxml")
    return content, soup


def save_html(file_path: str, soup: BeautifulSoup):
    """Save modified soup back to file."""
    # Use soup.decode() for consistent output (preserves original structure better)
    output = soup.decode(formatter="html5")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output)


# ---------------------------------------------------------------------------
# Operation executors
# ---------------------------------------------------------------------------

def op_remove(soup: BeautifulSoup, op: dict) -> dict:
    """Remove the first element matching the CSS selector."""
    target = op.get("target", "")
    elements = soup.select(target)
    if not elements:
        return {"success": False, "error": f"No element found for selector: {target}"}

    elements[0].decompose()
    return {"success": True}


def op_insert(soup: BeautifulSoup, op: dict) -> dict:
    """Insert HTML content relative to target element."""
    target = op.get("target", "")
    position = op.get("position", "append")
    content = op.get("content", "")

    elements = soup.select(target)
    if not elements:
        return {"success": False, "error": f"No element found for selector: {target}"}

    parent = elements[0]
    new_content = BeautifulSoup(content, "lxml")

    # Extract the meaningful content (skip html/body wrappers added by lxml)
    body = new_content.find("body")
    if body:
        fragments = list(body.children)
    else:
        fragments = list(new_content.children)

    if position == "append":
        for frag in fragments:
            parent.append(frag.__copy__() if hasattr(frag, '__copy__') else frag)
    elif position == "prepend":
        for i, frag in enumerate(fragments):
            parent.insert(i, frag.__copy__() if hasattr(frag, '__copy__') else frag)
    elif position == "before":
        for frag in fragments:
            parent.insert_before(frag.__copy__() if hasattr(frag, '__copy__') else frag)
    elif position == "after":
        for frag in reversed(fragments):
            parent.insert_after(frag.__copy__() if hasattr(frag, '__copy__') else frag)
    else:
        return {"success": False, "error": f"Unknown position: {position}"}

    return {"success": True}


def op_update(soup: BeautifulSoup, op: dict) -> dict:
    """Update attributes and/or text of the first matching element."""
    target = op.get("target", "")
    elements = soup.select(target)
    if not elements:
        return {"success": False, "error": f"No element found for selector: {target}"}

    el = elements[0]

    # Update attributes
    attrs = op.get("attributes", {})
    for key, value in attrs.items():
        if value is None:
            # Remove attribute
            if key in el.attrs:
                del el.attrs[key]
        else:
            el[key] = value

    # Update text content
    if "text" in op:
        el.string = op["text"]

    return {"success": True}


def op_replace(soup: BeautifulSoup, op: dict) -> dict:
    """Replace the first matching element with new HTML content."""
    target = op.get("target", "")
    content = op.get("content", "")

    elements = soup.select(target)
    if not elements:
        return {"success": False, "error": f"No element found for selector: {target}"}

    new_content = BeautifulSoup(content, "lxml")
    body = new_content.find("body")
    if body:
        fragments = list(body.children)
    else:
        fragments = list(new_content.children)

    old_el = elements[0]
    if fragments:
        # Insert new content before old element, then remove old
        for frag in fragments:
            old_el.insert_before(frag.__copy__() if hasattr(frag, '__copy__') else frag)
    old_el.decompose()

    return {"success": True}


# Operation dispatcher
OPERATIONS = {
    "remove": op_remove,
    "insert": op_insert,
    "update": op_update,
    "replace": op_replace,
}


# ---------------------------------------------------------------------------
# Main assembly
# ---------------------------------------------------------------------------

def parse_operations(ops_arg: str) -> list:
    """Parse operations from file path or inline JSON string."""
    stripped = ops_arg.strip()
    if stripped.startswith("[") or stripped.startswith("{"):
        # Inline JSON
        parsed = json.loads(stripped)
    else:
        # File path
        with open(stripped, "r", encoding="utf-8") as f:
            parsed = json.load(f)

    # Normalize: single operation → list
    if isinstance(parsed, dict):
        parsed = [parsed]

    return parsed


def assemble(file_path: str, operations: list) -> dict:
    """Execute all operations on the HTML file."""
    _, soup = load_html(file_path)

    details = []
    executed = 0
    failed = 0

    for i, op in enumerate(operations):
        action = op.get("action", "")
        target = op.get("target", "")

        if action not in OPERATIONS:
            details.append({
                "index": i,
                "action": action,
                "target": target,
                "success": False,
                "error": f"Unknown action: {action}",
            })
            failed += 1
            continue

        result = OPERATIONS[action](soup, op)
        details.append({
            "index": i,
            "action": action,
            "target": target,
            "success": result["success"],
            **({"error": result["error"]} if not result["success"] else {}),
        })

        if result["success"]:
            executed += 1
        else:
            failed += 1

    # Write back to file
    save_html(file_path, soup)

    return {
        "success": failed == 0,
        "operations_executed": executed,
        "operations_failed": failed,
        "details": details,
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: python3 dom_assembler.py <html_file> <operations_json>",
        }), file=sys.stderr)
        sys.exit(2)

    file_path = sys.argv[1]
    ops_arg = sys.argv[2]

    if not os.path.isfile(file_path):
        print(json.dumps({"error": f"File not found: {file_path}"}), file=sys.stderr)
        sys.exit(2)

    # Parse operations
    try:
        operations = parse_operations(ops_arg)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(json.dumps({
            "error": f"Failed to parse operations: {str(e)}",
        }), file=sys.stderr)
        sys.exit(2)

    # Backup original file
    backup_path = file_path + ".bak"
    shutil.copy2(file_path, backup_path)

    try:
        result = assemble(file_path, operations)
        result["backup"] = backup_path
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["success"] else 1)
    except Exception as e:
        # Restore from backup on failure
        if os.path.isfile(backup_path):
            shutil.copy2(backup_path, file_path)
        print(json.dumps({
            "error": str(e),
            "type": type(e).__name__,
            "restored_from_backup": True,
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
