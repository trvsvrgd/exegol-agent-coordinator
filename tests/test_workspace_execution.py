from pathlib import Path

from models import ActionRequest
from state_store import load_state
from workspace_execution import WorkspaceExecutor


def test_run_tests_updates_repo_plan(tmp_path, monkeypatch) -> None:
    state_dir = tmp_path / "state"
    log_dir = tmp_path / "logs"
    workspace_dir = tmp_path / "workspace"
    repo_dir = workspace_dir / "sample-repo"
    (repo_dir / ".git").mkdir(parents=True)

    monkeypatch.setenv("EXEGOL_STATE_DIR", str(state_dir))
    monkeypatch.setenv("EXEGOL_LOG_DIR", str(log_dir))
    monkeypatch.setenv("EXEGOL_WORKSPACE_DIR", str(workspace_dir))
    monkeypatch.setenv("EXEGOL_SANDBOX_MODE", "noop")

    executor = WorkspaceExecutor()
    action = ActionRequest(
        action_type="run_tests",
        description="Run tests",
        payload={"repo_path": str(repo_dir), "command": "pytest"},
    )
    executor.execute_action(action)

    plan_path = repo_dir / "plan.md"
    assert plan_path.exists()
    assert "Requirements Update" in plan_path.read_text(encoding="utf-8")


def test_cursor_prompt_adds_state_entry(tmp_path, monkeypatch) -> None:
    state_dir = tmp_path / "state"
    log_dir = tmp_path / "logs"
    workspace_dir = tmp_path / "workspace"

    monkeypatch.setenv("EXEGOL_STATE_DIR", str(state_dir))
    monkeypatch.setenv("EXEGOL_LOG_DIR", str(log_dir))
    monkeypatch.setenv("EXEGOL_WORKSPACE_DIR", str(workspace_dir))

    executor = WorkspaceExecutor()
    action = ActionRequest(
        action_type="cursor_prompt",
        description="Queue prompt",
        payload={"repo_path": str(workspace_dir / "demo"), "prompt": "Do the thing"},
    )
    executor.execute_action(action)

    state = load_state()
    assert state["cursor_prompts"]
