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

## Repo Test Audit + Cursor Prompts
1. Click **Run Repo Test Audit** to request test execution for each repo in the workspace.
2. Approve a request to run tests (sandbox mode controls execution).
3. Each repo’s `plan.md` receives a requirements update with results.
4. Click **Queue Cursor Prompts** to generate Cursor tasks per repo plan.

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
- `EXEGOL_SANDBOX_MODE` (`noop` or `docker`)

## Tests
```bash
pytest
```

## Windows .exe Build
```powershell
.\scripts\build_exe.ps1
```

The executable is output to `dist\exegol\exegol.exe`.

## One-Click Launcher
- `launch_exegol.bat` (double-click)
- `launch_exegol.ps1` (PowerShell)

If the `.exe` exists it will run it; otherwise it falls back to Streamlit.

## App Icon (Optional)
Set `EXEGOL_ICON_PATH` to your PNG file before building:
```powershell
$env:EXEGOL_ICON_PATH="C:\path\to\icon.png"
.\scripts\build_exe.ps1
```

The build scripts will generate `assets\icon.ico` and apply it to the `.exe` and MSI.

## Windows MSI Installer (WiX)
1. Install the WiX Toolset v3 and ensure `candle.exe` and `light.exe` are in PATH.
2. Build the `.exe` first:
   ```powershell
   .\scripts\build_exe.ps1
   ```
3. Build the MSI:
   ```powershell
   .\scripts\build_msi.ps1 -Version 0.1.0
   ```

The installer is output to `installer\dist\exegol-<version>.msi`.

## Security Notes
- No secrets are hardcoded; use environment variables for local configuration.
- Permission checks gate high-impact actions like git commits.
