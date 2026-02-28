from agent_manager import AgentManager
from state_store import load_state


def test_demo_flow_creates_permission_request(tmp_path, monkeypatch) -> None:
    state_dir = tmp_path / "state"
    log_dir = tmp_path / "logs"
    workspace_dir = tmp_path / "workspace"
    plan_path = tmp_path / "plan.md"
    agents_path = tmp_path / "agents.md"

    plan_path.write_text("# Plan\n", encoding="utf-8")
    agents_path.write_text(
        "# Agents\n\n```yaml\nagents:\n  - name: \"Maul\"\n"
        "    role: \"Builder\"\n"
        "    permissions:\n      - \"git:commit:requires-approval\"\n```\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("EXEGOL_STATE_DIR", str(state_dir))
    monkeypatch.setenv("EXEGOL_LOG_DIR", str(log_dir))
    monkeypatch.setenv("EXEGOL_WORKSPACE_DIR", str(workspace_dir))
    monkeypatch.setenv("EXEGOL_PLAN_PATH", str(plan_path))
    monkeypatch.setenv("EXEGOL_AGENTS_PATH", str(agents_path))

    manager = AgentManager()
    request_id = manager.run_demo_flow()
    state = load_state()

    assert request_id
    assert any(req["id"] == request_id for req in state["permission_requests"])
