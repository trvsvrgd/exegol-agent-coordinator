# Exegol V1 Plan

## Status Summary
- **Objective**: Build a minimal demo app to validate agent orchestration + permissions.
- **Current Focus**: Validation evidence + packaging polish.
- **Workspace**: Local, Streamlit UI, markdown-driven state.

## Architecture Snapshot
- Streamlit UI for interview, progress, approvals
- Local markdown-driven agents and plan
- Local workspace for git operations and sandbox tests

## In Progress (Do Next)
- [ ] Record test evidence in Verification Log
- [ ] Run smoke checks on UI flows

## Backlog (Planned Work)
- [ ] Improve sandbox runner reliability (docker health checks + timeout handling)
- [ ] Add audit export for ops metrics
- [ ] Expand per-repo plan updates to include failing test names
- [ ] The UI needs to be be dark and stormy like exegol with other star wars aesthetics

## Completed
- [x] Initialize pytest
- [x] Create `.gitignore` for secrets/local data
- [x] Scaffold core modules + UI shell
- [x] Add mock runtime files (`plan.md`, `agents.md`)
- [x] Add observability logging + demo flow
- [x] Add tests for routing + permissions
- [x] Add tests for demo flow + state updates
- [x] Add test-execution agent with sandbox runner
- [x] Update per-repo `plan.md` after test runs
- [x] Add Cursor prompt agent + UI display
- [x] Add tests for repo audit workflow
- [x] Add PyInstaller build script + spec
- [x] Document .exe build in README
- [x] Add one-click launcher scripts
- [x] Add MSI installer scaffolding (WiX)
- [x] Add icon preparation workflow

## Requirements Inbox (Add New Ideas Here)
- [ ] Example requirement here

## Verification Evidence (For Auditors)
- [AI to paste terminal logs or test results here after each successful run]

## Active Exceptions
- [Record any temporary dev-only configs here to be cleaned up before PR]
