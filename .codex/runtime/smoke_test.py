#!/usr/bin/env python3
"""Smoke tests for the HarnessDesign Codex runtime helpers."""

from __future__ import annotations

import json
import pathlib
import tempfile
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from common import (
    detect_archive_type,
    get_resume_payload,
    merge_patch,
    prompt_alias_context,
    should_block_bash_command,
)


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    merged = merge_patch({"a": {"b": 1}, "c": 2}, {"a": {"d": 3}, "c": None})
    assert_true(merged == {"a": {"b": 1, "d": 3}}, "merge_patch failed")

    assert_true(
        detect_archive_type("phase3-scenario-1-round-2.md") == "phase3-round",
        "archive detection failed",
    )
    assert_true(
        prompt_alias_context("/harnessdesign-start --prd foo.md") is not None,
        "command alias context missing",
    )
    blocked, _ = should_block_bash_command("cat <<'EOF' > tasks/demo/index.html\nEOF")
    assert_true(blocked, "critical Bash write should be blocked")

    with tempfile.TemporaryDirectory() as tmp_dir:
        progress = {
            "task_name": "smoke",
            "current_state": "research_jtbd",
            "expected_next_state": "interaction_design",
            "states": {
                "research_jtbd": {
                    "passes": False,
                    "approved_by": None,
                    "approved_at": None,
                    "artifacts": [],
                }
            },
            "phase1_handoff": {
                "handoff_path": "phase1-handoff.md",
                "material_manifest_path": "phase1-material-manifest.json",
                "validated": True,
                "validated_at": "2026-04-03T00:00:00",
                "fresh_resume_required": True,
            },
            "phase2_state": {
                "insight_cards_path": None,
                "current_topic_domain": None,
                "topic_count": 0,
            },
            "archive_index": [],
            "accumulated_constraints": [],
        }
        task_dir = pathlib.Path(tmp_dir)
        (task_dir / "task-progress.json").write_text(
            json.dumps(progress, ensure_ascii=False), encoding="utf-8"
        )
        payload = get_resume_payload(task_dir)
        assert_true(payload.get("fresh_resume_required") is True, "resume payload missing boundary flag")
        assert_true("resume_guidance" in payload, "resume guidance missing")
    print("HarnessDesign Codex runtime smoke tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
