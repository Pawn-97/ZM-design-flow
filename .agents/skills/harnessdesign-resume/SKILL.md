---
name: harnessdesign-resume
description: "Codex entrypoint for resuming an existing HarnessDesign task."
---

Read and follow the Skill SOP at `.harnessdesign/knowledge/skills/harnessdesign-router.md`.

This is the Codex entrypoint for `/harnessdesign-resume`.

When running inside Codex:
- Use `hd_list_tasks`, `hd_get_task_state`, and `hd_resume_task` to recover task context.
- Use the `harnessdesign_runtime` MCP tools for all workflow-critical writes and decisions.
- If the resumed task is at `research_jtbd` and `phase1_handoff.fresh_resume_required` is true, rebuild Phase 2 from the boundary handoff package only.

Task to resume: $ARGUMENTS
