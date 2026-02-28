# Project Technical Specification

## High-Level Intent
- Build Version 1 of "Exegol": a local, agentic software development framework
  that interviews users, orchestrates agents, and surfaces progress in a UI.

## Core Requirements
- **Low-Code/UI-First**: Users never type shell commands; Streamlit UI shows
  agent progress, traces, and permission approvals.
- **Transparent State**: Local markdown files (`plan.md`, `agents.md`) are the
  source of truth for agent roles and project architecture.
- **Cost-Conscious Routing**: LLM routing explicitly chooses Gemini for
  reasoning, self-hosted for volume, and Cursor for heavy code generation.
- **Centralized Git Hub**: All agent work happens inside a single
  `/exegol_workspace` directory.
- **Observability**: Log execution times, routing choices, and key events for
  display in an Operations dashboard.

## Tech Stack & Constraints
- **Language/Framework:** Python 3.11+, Streamlit UI
- **Key Libraries:** streamlit, gitpython, docker, google-generativeai, pyyaml
- **Storage/Data:** Local files (`plan.md`, `agents.md`, JSON state, log JSONL)
- **Style Preferences:** Readable markdown-driven state, minimal magic

## Security & Compliance Requirements
- **Access Control**: Local-only UI; no external service exposure by default
- **Data Encryption**: Local file storage only; no cloud data in V1
- **Logging & Monitoring**: JSONL logs for latency + actions; surfaced in UI

## SOC 2 Exception Log (Pattern Tracking)
- **Exception ID | Date | Reason | Mitigation**
- *Pattern*: If a standard control cannot be met, document it here with an
  expiration date and mitigation strategy.

## Out of Scope
- Production deployment, HA, or multi-tenant auth
- Cloud execution, managed services, or auto-scaling
- Full agent autonomy without human approvals
