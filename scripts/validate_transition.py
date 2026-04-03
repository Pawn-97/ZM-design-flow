#!/usr/bin/env python3
"""
validate_transition.py — Deterministic state transition validator for HarnessDesign AI-UX Workflow.

Checks pre-conditions before allowing phase/state transitions.
Called by Claude Code Hooks (PreToolUse) or directly by Skill SOP instructions.

Usage:
    python3 scripts/validate_transition.py <task_dir> <target_state>
    python3 scripts/validate_transition.py --check-write <file_path> <task_dir>
    python3 scripts/validate_transition.py --summary <task_dir>

Exit codes:
    0 = validation passed
    1 = validation failed (details in JSON output)
    2 = usage error
"""

import json
import os
import re
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# State transition rules — the single source of truth for workflow ordering
# MVP chain: onboarding → init → alignment → research_jtbd → interaction_design
#   → prepare_design_contract → contract_review → hifi_generation
#   → review → knowledge_extraction → complete
# ---------------------------------------------------------------------------

TRANSITIONS = {
    "migration": {
        "requires_files": [],
        "requires_approval": False,
        "next": None,  # Dynamic target — determined by coverage analysis
        "description": "Context migration from external AI tools",
    },
    "migration_complete": {
        "requires_files": [],
        "requires_approval": False,
        "next": None,  # Standby state — designer decides next action
        "description": "Migration complete, awaiting designer's next instruction",
    },
    "onboarding": {
        "requires_files": [
            ".harnessdesign/knowledge/product-context/product-context-index.md"
        ],
        "requires_approval": True,
        "next": "init",
        "description": "Product context knowledge base initialization",
    },
    "init": {
        "requires_files": [],
        "requires_approval": False,
        "next": "alignment",
        "description": "Task workspace initialization",
    },
    "alignment": {
        "requires_files": [
            "confirmed_intent.md",
            "phase1-handoff.md",
            "phase1-material-manifest.json",
        ],
        "requires_approval": True,
        "next": "research_jtbd",
        "description": "Context alignment — designer confirms shared understanding",
    },
    "research_jtbd": {
        "requires_files": ["00-research.md", "01-jtbd.md"],
        "requires_approval": True,
        "next": "interaction_design",
        "description": "Research + JTBD — designer confirms convergence",
    },
    "interaction_design": {
        "requires_files": ["02-structure.md"],
        "requires_approval": True,
        "next": "prepare_design_contract",
        "description": "Per-scenario interaction design with wireframes",
    },
    "prepare_design_contract": {
        "requires_files": ["03-design-contract.md"],
        "requires_approval": False,
        "next": "contract_review",
        "description": "Extract design contract from scenario archives",
    },
    "contract_review": {
        "requires_files": ["03-design-contract.md"],
        "requires_approval": True,
        "next": "hifi_generation",
        "description": "Designer reviews/edits design contract",
    },
    "hifi_generation": {
        "requires_files": ["index.html"],
        "requires_approval": False,
        "next": "review",
        "description": "High-fidelity HTML prototype generation",
    },
    "review": {
        "requires_files": ["index.html"],
        "requires_approval": True,
        "next": "knowledge_extraction",
        "description": "Designer reviews high-fidelity prototype — Approve / Reject / Feedback",
    },
    "knowledge_extraction": {
        "requires_files": [],
        "requires_approval": True,
        "next": "complete",
        "description": "Extract reusable knowledge from task artifacts",
    },
    "complete": {
        "requires_files": [],
        "requires_approval": False,
        "next": None,
        "description": "Task completed and archived",
    },
}


def load_progress(task_dir: str) -> dict:
    """Load task-progress.json from the task directory."""
    path = os.path.join(task_dir, "task-progress.json")
    if not os.path.isfile(path):
        return {"error": f"task-progress.json not found at {path}"}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_states(progress: dict) -> dict:
    """Get states dict with backward compatibility for 'gates' key."""
    return progress.get("states", progress.get("gates", {}))


def find_project_root(task_dir: str) -> str:
    """Walk up from task_dir to find the project root (contains .harnessdesign/ or CLAUDE.md)."""
    d = os.path.abspath(task_dir)
    while d and d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, ".harnessdesign")) or os.path.isfile(os.path.join(d, "CLAUDE.md")):
            return d
        d = os.path.dirname(d)
    # Fallback: two levels up from task dir (tasks/<name>/ → project root)
    return os.path.dirname(os.path.dirname(os.path.abspath(task_dir)))


def file_exists_and_nonempty(task_dir: str, relative_path: str) -> bool:
    """Check if a file exists relative to the task dir or project root and is non-empty."""
    project_root = find_project_root(task_dir)
    candidates = [
        os.path.join(task_dir, relative_path),
        os.path.join(project_root, relative_path),
    ]
    for p in candidates:
        if os.path.isfile(p) and os.path.getsize(p) > 0:
            return True
    return False


def read_relative_file(task_dir: str, relative_path: str) -> str | None:
    """Read a file relative to the task directory or project root."""
    project_root = find_project_root(task_dir)
    candidates = [
        os.path.join(task_dir, relative_path),
        os.path.join(project_root, relative_path),
    ]
    for path in candidates:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    return None


def parse_markdown_sections(text: str) -> dict:
    """Parse H2 sections from markdown into a simple title -> content mapping."""
    sections = {}
    current_title = None
    current_lines = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_title is not None:
                sections[current_title] = "\n".join(current_lines).strip()
            current_title = line[3:].strip()
            current_lines = []
            continue
        if current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        sections[current_title] = "\n".join(current_lines).strip()
    return sections


def extract_bullet_items(text: str) -> list[str]:
    """Extract flat markdown bullet items from a section."""
    items = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def normalize_text(value: str) -> str:
    """Normalize text for loose matching across artifacts."""
    lowered = value.lower()
    lowered = re.sub(r"`+", "", lowered)
    lowered = re.sub(r"\[.*?\]\(.*?\)", "", lowered)
    lowered = re.sub(r"[^\w\s\u4e00-\u9fff]+", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered)
    return lowered.strip()


def roughly_matches(candidate: str, haystack: str) -> bool:
    """Check whether a normalized candidate appears in a normalized text blob."""
    candidate_norm = normalize_text(candidate)
    haystack_norm = normalize_text(haystack)
    if not candidate_norm:
        return True
    if not haystack_norm:
        return False
    return candidate_norm in haystack_norm or haystack_norm in candidate_norm


def estimate_tokens(text: str) -> int:
    """Very rough token estimate for budget checks."""
    return max(1, len(text) // 4)


def validate_phase1_handoff(task_dir: str) -> dict:
    """Validate the Phase 1 boundary handoff bundle."""
    result = {"valid": True, "errors": [], "warnings": []}

    confirmed_text = read_relative_file(task_dir, "confirmed_intent.md")
    handoff_text = read_relative_file(task_dir, "phase1-handoff.md")
    manifest_text = read_relative_file(task_dir, "phase1-material-manifest.json")

    if not confirmed_text:
        result["valid"] = False
        result["errors"].append("confirmed_intent.md is missing or empty.")
        return result
    if not handoff_text:
        result["valid"] = False
        result["errors"].append("phase1-handoff.md is missing or empty.")
        return result
    if not manifest_text:
        result["valid"] = False
        result["errors"].append("phase1-material-manifest.json is missing or empty.")
        return result

    handoff_sections = parse_markdown_sections(handoff_text)
    required_sections = [
        "Core Questions",
        "Target Roles",
        "Confirmed Constraints",
        "Success Criteria",
        "Designer Background Assertions",
        "Deferred Questions For Research",
        "Research Targets",
        "Non-Goals",
        "Risk Flags",
        "Source References",
    ]
    for section in required_sections:
        if not handoff_sections.get(section):
            result["valid"] = False
            result["errors"].append(
                f"phase1-handoff.md is missing required section '{section}'."
            )

    try:
        manifest = json.loads(manifest_text)
    except json.JSONDecodeError as exc:
        result["valid"] = False
        result["errors"].append(
            f"phase1-material-manifest.json is not valid JSON: {exc}"
        )
        return result

    materials = manifest.get("materials")
    if not isinstance(materials, list):
        result["valid"] = False
        result["errors"].append(
            "phase1-material-manifest.json must contain a top-level 'materials' array."
        )
        materials = []

    for idx, item in enumerate(materials, start=1):
        if not isinstance(item, dict):
            result["valid"] = False
            result["errors"].append(
                f"phase1-material-manifest.json materials[{idx}] must be an object."
            )
            continue
        for field in [
            "id",
            "path",
            "kind",
            "source",
            "sha256",
            "summary",
            "relevance",
            "phase1_sections",
        ]:
            if field not in item:
                result["valid"] = False
                result["errors"].append(
                    f"phase1-material-manifest.json materials[{idx}] is missing '{field}'."
                )

    confirmed_sections = parse_markdown_sections(confirmed_text)
    confirmed_constraints = [
        item
        for item in extract_bullet_items(confirmed_sections.get("Constraints", ""))
        if item
    ]
    deferred_questions = extract_bullet_items(
        confirmed_sections.get("Deferred Questions", "")
    )

    handoff_constraints = "\n".join(
        [
            handoff_sections.get("Confirmed Constraints", ""),
            handoff_sections.get("Risk Flags", ""),
        ]
    )
    for constraint in confirmed_constraints:
        constraint_body = constraint.replace("✅", "").strip()
        if not roughly_matches(constraint_body, handoff_constraints):
            result["valid"] = False
            result["errors"].append(
                f"Constraint from confirmed_intent.md missing in handoff bundle: '{constraint_body}'."
            )

    handoff_deferred = handoff_sections.get("Deferred Questions For Research", "")
    for question in deferred_questions:
        if not roughly_matches(question, handoff_deferred):
            result["valid"] = False
            result["errors"].append(
                f"Deferred question missing in handoff bundle: '{question}'."
            )

    source_refs_section = handoff_sections.get("Source References", "")
    source_refs = extract_bullet_items(source_refs_section)
    if not source_refs:
        result["valid"] = False
        result["errors"].append("phase1-handoff.md must include at least one source reference.")
    else:
        valid_ref_tokens = {
            "confirmed_intent.md",
            "phase1-alignment.md",
            "phase1-handoff.md",
        }
        for item in materials:
            if isinstance(item, dict):
                path = item.get("path")
                if path:
                    valid_ref_tokens.add(os.path.basename(path))
                    valid_ref_tokens.add(path)
        for ref in source_refs:
            normalized_ref = normalize_text(ref)
            if not any(normalize_text(token) in normalized_ref for token in valid_ref_tokens):
                result["valid"] = False
                result["errors"].append(
                    f"Source reference does not point to a known artifact or material: '{ref}'."
                )

    handoff_tokens = estimate_tokens(handoff_text)
    if handoff_tokens < 200:
        result["valid"] = False
        result["errors"].append(
            f"phase1-handoff.md is too small ({handoff_tokens} estimated tokens)."
        )
    elif handoff_tokens > 2500:
        result["valid"] = False
        result["errors"].append(
            f"phase1-handoff.md exceeds the startup budget ({handoff_tokens} estimated tokens)."
        )
    elif handoff_tokens < 700 or handoff_tokens > 1200:
        result["warnings"].append(
            f"phase1-handoff.md is outside the recommended target range ({handoff_tokens} estimated tokens)."
        )

    return result


def validate_transition(task_dir: str, target_state: str) -> dict:
    """
    Validate whether transitioning to target_state is allowed.

    Returns a dict with:
      - valid: bool
      - errors: list[str]  (empty if valid)
      - warnings: list[str]
      - current_state: str
      - target_state: str
    """
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "current_state": None,
        "target_state": target_state,
        "timestamp": datetime.now().isoformat(),
    }

    # Load progress
    progress = load_progress(task_dir)
    if "error" in progress:
        result["valid"] = False
        result["errors"].append(progress["error"])
        return result

    current = progress.get("current_state")
    result["current_state"] = current

    # Check target state is known
    if target_state not in TRANSITIONS and target_state != "complete":
        result["valid"] = False
        result["errors"].append(
            f"Unknown target state: '{target_state}'. "
            f"Valid states: {list(TRANSITIONS.keys())}"
        )
        return result

    # --- Migration exception: migration states have dynamic targets ---
    if current in ("migration", "migration_complete"):
        migration_meta = progress.get("migration_metadata", {})
        states = get_states(progress)

        # migration → any phase is allowed if migration_metadata exists
        if current == "migration" and migration_meta:
            # Validate that all skipped phases have passes: true + approved_by: "migration"
            for skipped in migration_meta.get("phases_skipped", []):
                gate = states.get(skipped, {})
                if not gate.get("passes") or gate.get("approved_by") != "migration":
                    result["valid"] = False
                    result["errors"].append(
                        f"Skipped phase '{skipped}' must have passes=true and "
                        f"approved_by='migration' before transition"
                    )
            return result

        # migration_complete → any phase is allowed (designer chooses)
        if current == "migration_complete":
            if target_state in TRANSITIONS:
                return result
            result["valid"] = False
            result["errors"].append(
                f"Unknown target state: '{target_state}'"
            )
            return result

    # Check expected_next_state matches
    expected = progress.get("expected_next_state")
    if expected and expected != target_state:
        result["valid"] = False
        result["errors"].append(
            f"State mismatch: expected_next_state is '{expected}' "
            f"but attempting to transition to '{target_state}'"
        )

    # Check current state exists in transitions
    if current not in TRANSITIONS:
        result["valid"] = False
        result["errors"].append(f"Current state '{current}' not in transition rules")
        return result

    current_rule = TRANSITIONS[current]

    # Check current state's next allows this transition
    if current_rule["next"] != target_state:
        result["valid"] = False
        result["errors"].append(
            f"Invalid transition: '{current}' -> '{target_state}'. "
            f"Allowed next state: '{current_rule['next']}'"
        )

    # Check current state's pre-conditions are met
    states = get_states(progress)
    current_gate = states.get(current, {})

    # Check passes
    if not current_gate.get("passes", False):
        result["valid"] = False
        result["errors"].append(
            f"Current state '{current}' has not passed yet "
            f"(passes=false in task-progress.json)"
        )

    # Check approval if required
    if current_rule["requires_approval"]:
        if not current_gate.get("approved_by"):
            result["valid"] = False
            result["errors"].append(
                f"State '{current}' requires designer approval "
                f"([STOP AND WAIT FOR APPROVAL]) but approved_by is null. "
                f"Designer must confirm before proceeding."
            )

    # Check required artifacts exist
    for artifact in current_rule["requires_files"]:
        if not file_exists_and_nonempty(task_dir, artifact):
            result["valid"] = False
            result["errors"].append(
                f"Required artifact missing or empty: '{artifact}' "
                f"(expected for state '{current}')"
            )

    # Add warnings for edge cases
    if not result["errors"]:
        # Check artifact list in JSON matches actual files
        declared_artifacts = current_gate.get("artifacts", [])
        for artifact in current_rule["requires_files"]:
            basename = os.path.basename(artifact)
            if basename not in [os.path.basename(a) for a in declared_artifacts]:
                result["warnings"].append(
                    f"Artifact '{artifact}' exists on disk but not declared "
                    f"in states.{current}.artifacts — consider updating JSON"
                )

    # Transition-specific boundary validation
    if current == "alignment" and target_state == "research_jtbd":
        handoff = validate_phase1_handoff(task_dir)
        if not handoff["valid"]:
            result["valid"] = False
            result["errors"].extend(handoff["errors"])
        result["warnings"].extend(handoff["warnings"])

    return result


def generate_summary(task_dir: str) -> dict:
    """
    Generate a phase summary card data structure.
    Used by SOP to render the standardized phase completion card.
    """
    progress = load_progress(task_dir)
    if "error" in progress:
        return {"error": progress["error"]}

    current = progress.get("current_state", "unknown")
    states = get_states(progress)

    summary = {
        "current_state": current,
        "expected_next": progress.get("expected_next_state"),
        "description": TRANSITIONS.get(current, {}).get("description", ""),
        "checklist": [],
    }
    phase1_handoff = progress.get("phase1_handoff", {}) or {}

    # Migration states: show migration metadata in summary
    if current in ("migration", "migration_complete"):
        migration_meta = progress.get("migration_metadata", {})
        if migration_meta:
            summary["migration_metadata"] = migration_meta
            for phase, score in migration_meta.get("coverage_scores", {}).items():
                level = "full" if score >= 0.8 else "partial" if score >= 0.4 else "seed" if score >= 0.1 else "none"
                summary["checklist"].append(
                    {"item": f"{phase}: {level} ({score:.2f})", "status": "info", "type": "coverage"}
                )
        return summary

    # Build checklist for the current state
    if current in TRANSITIONS:
        rule = TRANSITIONS[current]

        # Artifact checks
        for artifact in rule["requires_files"]:
            exists = file_exists_and_nonempty(task_dir, artifact)
            summary["checklist"].append(
                {
                    "item": os.path.basename(artifact),
                    "status": "pass" if exists else "fail",
                    "type": "artifact",
                }
            )

        # Approval check
        if rule["requires_approval"]:
            gate = states.get(current, {})
            approved = bool(gate.get("approved_by"))
            summary["checklist"].append(
                {
                    "item": "Designer approval",
                    "status": "pass" if approved else "pending",
                    "type": "approval",
                }
            )

        if current in ("alignment", "research_jtbd"):
            handoff_path = phase1_handoff.get("handoff_path")
            manifest_path = phase1_handoff.get("material_manifest_path")
            if handoff_path:
                summary["checklist"].append(
                    {
                        "item": os.path.basename(handoff_path),
                        "status": "pass" if file_exists_and_nonempty(task_dir, handoff_path) else "fail",
                        "type": "boundary_handoff",
                    }
                )
            if manifest_path:
                summary["checklist"].append(
                    {
                        "item": os.path.basename(manifest_path),
                        "status": "pass" if file_exists_and_nonempty(task_dir, manifest_path) else "fail",
                        "type": "boundary_handoff",
                    }
                )
            if current == "research_jtbd":
                summary["checklist"].append(
                    {
                        "item": "Phase 1 handoff validated",
                        "status": "pass" if phase1_handoff.get("validated") else "fail",
                        "type": "boundary_handoff",
                    }
                )
                summary["checklist"].append(
                    {
                        "item": "Fresh resume required",
                        "status": "info" if phase1_handoff.get("fresh_resume_required") else "pass",
                        "type": "boundary_handoff",
                    }
                )
                if phase1_handoff.get("fresh_resume_required"):
                    summary["resume_guidance"] = (
                        "Begin Phase 2 from a fresh session and rebuild only from "
                        "confirmed_intent.md, phase1-handoff.md, phase1-material-manifest.json, "
                        "the knowledge base, and archive_index."
                    )

    # Archive checks (look for expected archive files)
    archive_dir = os.path.join(
        os.path.dirname(task_dir), ".harnessdesign", "memory", "sessions"
    )
    if os.path.isdir(archive_dir):
        archive_count = len(
            [f for f in os.listdir(archive_dir) if f.endswith(".md")]
        )
        summary["checklist"].append(
            {
                "item": f"{archive_count} archive file(s) found",
                "status": "info",
                "type": "archive",
            }
        )

    return summary


def check_write_allowed(file_path: str, task_dir: str) -> dict:
    """
    Check if writing to a specific file is allowed given the current state.
    Used by PreToolUse Hook to intercept writes.
    """
    result = {"allowed": True, "reason": None}

    # Only gate writes to task-progress.json and key artifacts
    basename = os.path.basename(file_path)

    if basename == "task-progress.json":
        # Allow writes to task-progress.json but warn if it looks like a skip
        # The actual content validation happens post-write
        result["allowed"] = True
        result["reason"] = "task-progress.json write — post-write validation will run"
        return result

    # Gate artifact writes based on current state
    progress = load_progress(task_dir)
    if "error" in progress:
        return result  # Can't validate, allow with warning

    current = progress.get("current_state", "")

    # Migration state: allow writing any artifact (converting imported content)
    if current in ("migration", "migration_complete"):
        result["allowed"] = True
        result["reason"] = f"Migration state '{current}' allows writing any artifact"
        return result
    state_artifacts = {
        "alignment": [
            "confirmed_intent.md",
            "phase1-handoff.md",
            "phase1-material-manifest.json",
        ],
        "research_jtbd": ["00-research.md", "01-jtbd.md"],
        "interaction_design": ["02-structure.md"],
        "prepare_design_contract": ["03-design-contract.md"],
        "contract_review": ["03-design-contract.md"],
        "hifi_generation": ["index.html"],
        "review": ["index.html"],
    }

    # Check if the file being written is an artifact for a future state
    for state, artifacts in state_artifacts.items():
        if basename in artifacts:
            # Find if this state comes after current
            state_order = list(TRANSITIONS.keys())
            if state in state_order and current in state_order:
                current_idx = state_order.index(current)
                target_idx = state_order.index(state)
                if target_idx > current_idx + 1:
                    result["allowed"] = False
                    result["reason"] = (
                        f"Attempting to write '{basename}' which belongs to "
                        f"state '{state}', but current state is '{current}'. "
                        f"This looks like a phase skip."
                    )
                    return result

    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        print(
            "Usage:\n"
            "  python3 validate_transition.py <task_dir> <target_state>\n"
            "  python3 validate_transition.py --check-write <file_path> <task_dir>\n"
            "  python3 validate_transition.py --summary <task_dir>",
            file=sys.stderr,
        )
        sys.exit(2)

    if sys.argv[1] == "--check-write":
        if len(sys.argv) < 4:
            print("Usage: --check-write <file_path> <task_dir>", file=sys.stderr)
            sys.exit(2)
        result = check_write_allowed(sys.argv[2], sys.argv[3])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["allowed"] else 1)

    elif sys.argv[1] == "--summary":
        result = generate_summary(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0)

    else:
        task_dir = sys.argv[1]
        target_state = sys.argv[2]
        result = validate_transition(task_dir, target_state)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()
