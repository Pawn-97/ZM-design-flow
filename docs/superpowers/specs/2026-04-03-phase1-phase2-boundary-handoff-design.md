# Phase 1 to Phase 2 Boundary Handoff Design

## Context

HarnessDesign currently archives the full Phase 1 dialogue and persists a compact `confirmed_intent.md`, but it does not force a fresh Codex session at the `alignment -> research_jtbd` boundary. When the designer uploads many background materials or spends many rounds in Phase 1, the live conversation history can continue to occupy context even after state transition. This weakens the guarantee that Phase 2 starts from a deterministic, disk-backed input set.

Phase 2 already uses `topic-level Context Reset` internally. The boundary between Phase 1 and Phase 2 should adopt the same harness principle: compile the conversation into verifiable artifacts, then resume from artifacts instead of relying on residual chat memory.

## Goals

- Force a reliable context reset when moving from Phase 1 to Phase 2.
- Preserve all Phase 1 outputs needed by Phase 2 with explicit traceability.
- Make the boundary deterministic, inspectable, and validator-enforced.
- Keep the default Phase 2 startup budget bounded and predictable.

## Non-Goals

- Do not redesign the overall state machine.
- Do not require Phase 2 to reload every original background file by default.
- Do not depend on hidden model memory or same-thread continuity.

## Design Summary

Treat `alignment -> research_jtbd` as a compile boundary.

Phase 1 must produce a small handoff bundle in addition to `confirmed_intent.md`, validate that bundle, archive the full Phase 1 dialogue, and then stop with an explicit fresh-resume instruction. Phase 2 must start from disk and only load the approved handoff artifacts plus the normal anchor layer inputs.

## New Artifacts

### 1. `phase1-handoff.md`

Human-readable but machine-structured handoff document. This is the primary Phase 2 startup artifact.

Required sections:

- `Core Questions`
- `Target Roles`
- `Confirmed Constraints`
- `Success Criteria`
- `Designer Background Assertions`
- `Deferred Questions For Research`
- `Research Targets`
- `Non-Goals`
- `Risk Flags`
- `Source References`

Rules:

- Target size: `700-1200` tokens.
- Every item must be grounded in either `confirmed_intent.md`, `phase1-alignment.md`, or a designer-uploaded material.
- Each section should be concise and directly useful for research planning.

### 2. `phase1-material-manifest.json`

Structured index for Phase 1 inputs that are too large to keep in working memory but may need precise recall later.

Required per-item fields:

- `id`
- `path`
- `kind`
- `source`
- `sha256`
- `summary`
- `relevance`
- `phase1_sections`

Rules:

- One entry per uploaded file or externally referenced material handled in Phase 1.
- `summary` is limited to 1-2 sentences.
- `relevance` states why the material matters for Phase 2.

### 3. `phase1-alignment.md`

Remains the full archive and evidence source. No change in role, but it becomes an explicit source for `phase1-handoff.md`.

## Boundary Protocol

### Phase 1 Exit

At the end of Phase 1:

1. Generate `confirmed_intent.md`.
2. Generate `phase1-handoff.md`.
3. Generate `phase1-material-manifest.json`.
4. Archive the full Phase 1 dialogue to `phase1-alignment.md`.
5. Update `archive_index` with the Phase 1 archive and handoff semantic tags.
6. Run handoff validation.
7. Only if validation passes:
   - mark `states.alignment.passes = true`
   - move `current_state` to `research_jtbd`
8. Stop the current phase with an explicit message that Phase 2 must continue via fresh resume.

### Phase 2 Entry

Phase 2 startup must assume no live chat memory.

Allowed default startup inputs:

- `confirmed_intent.md`
- `phase1-handoff.md`
- `phase1-material-manifest.json`
- `product-context-index.md`
- `archive_index`
- required L1 knowledge base files

Disallowed default behavior:

- reading the full Phase 1 archive unless recall is needed
- re-reading all uploaded materials by default
- using same-thread conversation history as an implicit source of truth

## Validation Contract

Add a deterministic handoff validator to the `alignment -> research_jtbd` transition gate.

Validation checks:

1. `confirmed_intent.md` exists and is non-empty.
2. `phase1-handoff.md` exists and all required sections are present.
3. `phase1-material-manifest.json` exists if Phase 1 included uploaded materials.
4. Every constraint confirmed in `confirmed_intent.md` appears in either:
   - `Confirmed Constraints`, or
   - `Risk Flags` with justification.
5. Every deferred question from Phase 1 appears in `Deferred Questions For Research`.
6. `Source References` is non-empty and each entry points to a valid source artifact.
7. Token budget is within boundary limits.

Failure policy:

- If any check fails, `alignment -> research_jtbd` is blocked.
- The AI must repair the handoff artifacts before transition.

## Runtime Behavior

Codex runtime should support an explicit fresh-resume boundary rather than silently continuing in the same long-running session.

Expected behavior:

- Phase 1 transition prompt tells the designer that the boundary package has been compiled.
- The prompt instructs the next step as `use /harnessdesign-resume to begin Phase 2 from fresh context`.
- Session recovery and resume payload should surface that this task is ready for `research_jtbd` and that a fresh resume is recommended.

This is a protocol-level reset, not a memory wipe primitive. The reliability comes from starting the next phase from disk-backed artifacts only.

## Skill Changes

### `alignment-skill.md`

- Extend Phase 1 outputs to include `phase1-handoff.md` and `phase1-material-manifest.json`.
- Change the transition prompt to recommend fresh resume.
- Clarify that uploaded material summaries must be captured in the manifest as they are introduced.

### `research-strategist-skill.md`

- Update prerequisites to require `phase1-handoff.md`.
- Load `phase1-handoff.md` into the anchor layer alongside `confirmed_intent.md`.
- Treat `phase1-material-manifest.json` as the default recall map for designer materials.
- State explicitly that Phase 2 startup assumes fresh context and disk-backed reconstruction.

### `harnessdesign-router.md`

- Document the boundary compile step in the Phase 1 to Phase 2 transition.
- Extend session recovery guidance to prefer fresh resume at this boundary.

## Schema and Validator Changes

### `task-progress.json`

Add a `phase1_handoff` object for explicit boundary tracking.

Suggested fields:

- `handoff_path`
- `material_manifest_path`
- `validated`
- `validated_at`
- `fresh_resume_required`

### `validate_transition.py`

Add a transition-specific validator for `alignment -> research_jtbd` that checks the handoff bundle.

### `integration_test.py`

Add static checks that:

- new artifact names are referenced consistently
- schema contains `phase1_handoff`
- router and skills mention the boundary handoff files

## Token Budget

Phase 2 startup budget should be roughly:

- `confirmed_intent.md`: `~500`
- `phase1-handoff.md`: `~700-1200`
- `product-context-index.md`: `~500-800`
- summary index: `~500-1000`
- material manifest: `~300-800`
- selected L1 files: variable, but bounded by existing Phase 2 loading rules

This keeps the startup deterministic and substantially below the risk zone caused by carrying Phase 1 chat history forward.

## Why This Matches Harness Engineering

- Conversation is scaffolding; handoff artifacts are the building.
- Phase boundaries become compile points, not loose conversational continuations.
- State transition depends on deterministic checks, not model confidence.
- Traceability makes context loss visible and recoverable.
- Recall becomes an explicit tool path instead of a hidden reliance on old memory.

## Implementation Order

1. Add the design contract for new artifacts and phase1 handoff state.
2. Update `alignment-skill.md`.
3. Update `research-strategist-skill.md`.
4. Update `harnessdesign-router.md`.
5. Update `task_progress_schema.json`.
6. Update `validate_transition.py`.
7. Update Codex runtime resume messaging if needed.
8. Update `integration_test.py`.

## Open Questions

- Whether `phase1-handoff` should live only as Markdown or also have a JSON mirror. For now, Markdown plus validator parsing is sufficient.
- Whether fresh resume should be recommended or mandatory in UI copy. For reliability, the protocol should treat it as mandatory even if the runtime cannot hard-enforce a new thread.
