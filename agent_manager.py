from __future__ import annotations

import re
from typing import List, Optional

import yaml

from config import get_agents_path, get_plan_path
from llm_router import format_cursor_instructions
from models import ActionRequest, AgentProfile
from observability import log_event, timer
from permission_judge import evaluate_action
from state_store import add_permission_request, append_activity
from workspace_execution import WorkspaceExecutor


def _extract_yaml_block(markdown: str) -> str:
    match = re.search(r"```yaml(.*?)```", markdown, re.DOTALL)
    if not match:
        raise ValueError("No YAML block found in agents.md")
    return match.group(1).strip()


def load_agents() -> List[AgentProfile]:
    raw = get_agents_path().read_text(encoding="utf-8")
    yaml_block = _extract_yaml_block(raw)
    payload = yaml.safe_load(yaml_block)
    agents = []
    for item in payload.get("agents", []):
        agents.append(
            AgentProfile(
                name=item["name"],
                role=item["role"],
                permissions=item.get("permissions", []),
            )
        )
    return agents


def load_plan() -> str:
    return get_plan_path().read_text(encoding="utf-8")


class AgentManager:
    def __init__(self) -> None:
        self.agents = load_agents()
        self.plan = load_plan()
        self.executor = WorkspaceExecutor()

    def _select_agent(self, permission_prefix: str) -> Optional[AgentProfile]:
        for agent in self.agents:
            for permission in agent.permissions:
                if permission.startswith(permission_prefix):
                    return agent
        return None

    def run_demo_flow(self) -> str:
        with timer("demo_flow"):
            agent = self.agents[-1]
            append_activity(
                f"{agent.name} reads plan.md",
                {"component": "Cloning Vats", "location": "agent_manager.py"},
            )
            append_activity(
                "Preparing git commit action",
                {"component": "Cloning Vats", "location": "agent_manager.py"},
            )

            action = ActionRequest(
                action_type="git_commit",
                description="Attempt demo git commit in workspace",
                payload={"repo": "demo-repo", "message": "demo commit"},
            )
            decision = evaluate_action(action, agent)
            if decision.requires_approval:
                request_id = add_permission_request(
                    title="Git commit requested",
                    action={
                        "action_type": action.action_type,
                        "description": action.description,
                        "payload": action.payload,
                    },
                    agent={"name": agent.name, "role": agent.role},
                    reason=decision.reason,
                    origin={"component": "Inquisitor", "location": "permission_judge.py"},
                )
                append_activity(
                    "Permission requested for git commit",
                    {
                        "component": "Inquisitor",
                        "location": "permission_judge.py",
                        "reason": decision.reason,
                    },
                )
                log_event(
                    "demo_flow_paused",
                    {"request_id": request_id, "reason": decision.reason},
                )
                return request_id

            log_event("demo_flow_auto_approved", {"reason": decision.reason})
            return "auto-approved"

    def run_repo_test_audit(self, command: str = "pytest") -> List[str]:
        with timer("repo_test_audit"):
            agent = self._select_agent("tests:run")
            if agent is None:
                raise RuntimeError("No agent configured with tests:run permissions.")

            request_ids = []
            for repo_path in self.executor.list_repos():
                action = ActionRequest(
                    action_type="run_tests",
                    description=f"Run tests in {repo_path.name}",
                    payload={
                        "repo_path": str(repo_path),
                        "command": command,
                        "update_plan": True,
                    },
                )
                decision = evaluate_action(action, agent)
                if decision.requires_approval:
                    request_id = add_permission_request(
                        title=f"Run tests for {repo_path.name}",
                        action={
                            "action_type": action.action_type,
                            "description": action.description,
                            "payload": action.payload,
                        },
                        agent={"name": agent.name, "role": agent.role},
                        reason=decision.reason,
                        origin={"component": "Inquisitor", "location": "permission_judge.py"},
                    )
                    request_ids.append(request_id)
                    append_activity(
                        f"Permission requested for tests in {repo_path.name}",
                        {
                            "component": "Inquisitor",
                            "location": "permission_judge.py",
                            "reason": decision.reason,
                        },
                    )
                else:
                    self.executor.execute_action(action)
                    append_activity(
                        f"Tests executed for {repo_path.name}",
                        {"component": "Final Order", "location": "workspace_execution.py"},
                    )
            return request_ids

    def run_cursor_prompt_flow(self) -> List[str]:
        with timer("cursor_prompt_flow"):
            agent = self._select_agent("cursor:prompt")
            if agent is None:
                raise RuntimeError("No agent configured with cursor:prompt permissions.")

            request_ids = []
            for repo_path in self.executor.list_repos():
                plan_path = repo_path / "plan.md"
                if plan_path.exists():
                    plan_content = plan_path.read_text(encoding="utf-8")
                else:
                    plan_content = "# Plan\n"
                snippet = plan_content.replace("\n", " ")[:400]
                task = (
                    f"Review and update {repo_path.name}/plan.md based on test results."
                )
                prompt = format_cursor_instructions(f"{task}\nPlan snapshot: {snippet}")
                action = ActionRequest(
                    action_type="cursor_prompt",
                    description=f"Queue Cursor prompt for {repo_path.name}",
                    payload={"repo_path": str(repo_path), "prompt": prompt},
                )
                decision = evaluate_action(action, agent)
                if decision.requires_approval:
                    request_id = add_permission_request(
                        title=f"Queue Cursor prompt for {repo_path.name}",
                        action={
                            "action_type": action.action_type,
                            "description": action.description,
                            "payload": action.payload,
                        },
                        agent={"name": agent.name, "role": agent.role},
                        reason=decision.reason,
                        origin={"component": "Inquisitor", "location": "permission_judge.py"},
                    )
                    request_ids.append(request_id)
                    append_activity(
                        f"Permission requested for Cursor prompt in {repo_path.name}",
                        {
                            "component": "Inquisitor",
                            "location": "permission_judge.py",
                            "reason": decision.reason,
                        },
                    )
                else:
                    self.executor.execute_action(action)
                    append_activity(
                        f"Cursor prompt queued for {repo_path.name}",
                        {"component": "Final Order", "location": "workspace_execution.py"},
                    )
            return request_ids
