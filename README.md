# Exegol Agent Coordinator (V1)

Local-first, agentic software development framework with a Streamlit UI, markdown-driven state, and permission-gated automation. The goal is to interview users about a business pain point and orchestrate agents to build, test, and deploy solutions — while keeping all actions transparent and auditable.

## What’s Included
- **The Dark Throne**: `ui_dashboard.py` Streamlit UI for interview, activity feed, ops metrics, and approvals
- **The Cloning Vats**: `agent_manager.py` loads `agents.md` + `plan.md` and runs the demo flow
- **The Wayfinder**: `llm_router.py` routes prompts to Gemini, self-hosted, or Cursor instructions
- **The Final Order**: `workspace_execution.py` manages the local `/exegol_workspace` and git actions
- **The Inquisitor**: `permission_judge.py` evaluates actions against natural-language permissions

## Quickstart
```bash
pip install -r requirements.txt
streamlit run ui_dashboard.py
```

## Demo Flow (V1)
1. Click **Run Demo Flow** in the UI.
2. An agent reads `plan.md` and attempts a git commit.
3. The Inquisitor requires approval and surfaces a request in the UI.
4. Approve or deny; approvals execute the commit and log telemetry.

## State & Config
- `plan.md` and `agents.md` are the human-readable source of truth.
- Runtime state is stored in `state/runtime_state.json`.
- Ops events are appended to `logs/ops.jsonl`.

Optional environment overrides:
- `EXEGOL_STATE_DIR`
- `EXEGOL_LOG_DIR`
- `EXEGOL_WORKSPACE_DIR`
- `EXEGOL_PLAN_PATH`
- `EXEGOL_AGENTS_PATH`

## Tests
```bash
pytest
```

## Security Notes
- No secrets are hardcoded; use environment variables for local configuration.
- Permission checks gate high-impact actions like git commits.
