---
name: harnessdesign-research
description: "Codex entrypoint for the HarnessDesign research and JTBD phase."
---

Read and follow the Skill SOP at `.harnessdesign/knowledge/skills/research-strategist-skill.md`.

For Codex, route workflow-critical writes through `harnessdesign_runtime`, and map any `AskUserQuestion` step to `hd_ask_decision`.
If `phase1_handoff.fresh_resume_required` is true, treat this as a fresh boundary-start and rebuild Phase 2 from `confirmed_intent.md`, `phase1-handoff.md`, `phase1-material-manifest.json`, the knowledge base, and `archive_index`.

Arguments: $ARGUMENTS
