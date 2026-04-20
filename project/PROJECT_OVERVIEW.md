# SedimentPalace MCP — Project Overview

## Purpose
SedimentPalace MCP is a local-first memory system for AI agents.  
It stores project context in Markdown files with YAML metadata and manages memory lifecycle via deterministic sedimentation rules.

## Core Problem
Agents lose context quality over time: either too much noisy history or weakly structured retrieval.

## Product Goal
Build a transparent, file-native memory engine that:
- Preserves causal/project structure.
- Automatically decays low-value context.
- Promotes stable knowledge into long-lived layers.
- Works through MCP tools for agent interoperability.

## Scope (v1)
- MCP server over stdio JSON-RPC.
- Layered memory model: `01_Shallow`, `02_Sediment`, `03_Bedrock`.
- YAML frontmatter normalization.
- Deterministic `metabolize` cycle.
- Local filesystem storage only.
- Windows-friendly bootstrap.

## Non-Goals (v1)
- Cloud sync.
- Vector database as primary source.
- Multi-tenant auth system.
- Web UI.

## Success Criteria
- Agent can start from `PALACE_MAP.md` and operate safely.
- Memory hygiene improves automatically (measurable decay/promotion outcomes).
- Operations are auditable and recoverable.
- System remains understandable and editable by humans.

## Start Here For Any Agent
1. Read `project/ARCHITECTURE_AND_STACK.md`.
2. Read `project/AGENT_WORK_RULES.md`.
3. Read open ADRs in `project/adr/`.
4. Use role prompt (`PROMPT_BACKEND.md`, `PROMPT_FRONTEND.md`, `PROMPT_DEVOPS.md`) for execution context.
