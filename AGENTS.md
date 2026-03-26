# Zoom AI-UX Workflow — Codex Adaptation

## Overview

This project is a portable Skill + Knowledge directory (`.zoom-ai/`) that runs inside AI coding tools. The AI tool's agent loop is the orchestration engine — Skill SOP files (Markdown + YAML) guide the 4-phase UX design workflow.

## Quick Start

1. Read `.zoom-ai/knowledge/skills/zoom-router.md` for the main orchestration logic
2. Check `task-progress.json` in the task directory for current state
3. Follow the Skill SOP instructions step by step

## Directory Structure

See `CLAUDE.md` for the full directory map (it applies to all host tools).

## Key Rules

- Always read `task-progress.json` before taking action
- Follow `[STOP AND WAIT FOR APPROVAL]` control points — wait for designer confirmation
- Archive conversations at Phase/scenario boundaries to `.zoom-ai/memory/sessions/`
- Use Chinese for designer-facing dialogue, keep technical terms in English
- Follow ZDS design rules in `.zoom-ai/knowledge/Design.md` for HTML generation
