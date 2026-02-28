from __future__ import annotations

import re
from typing import List

import yaml

from config import get_agents_path, get_plan_path
from models import ActionRequest, AgentProfile
from observability import log_event, timer
from permission_judge import evaluate_action
from state_store import add_permission_request, append_activity


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

    def run_demo_flow(self) -> str:
        with timer("demo_flow"):
            agent = self.agents[-1]
            append_activity(f"{agent.name} reads plan.md")
            append_activity("Preparing git commit action")

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
                )
                append_activity("Permission requested for git commit")
                log_event(
                    "demo_flow_paused",
                    {"request_id": request_id, "reason": decision.reason},
                )
                return request_id

            log_event("demo_flow_auto_approved", {"reason": decision.reason})
            return "auto-approved"
