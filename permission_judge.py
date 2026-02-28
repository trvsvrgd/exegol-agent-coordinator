from __future__ import annotations

from typing import Tuple

from models import ActionRequest, AgentProfile, PermissionDecision
from observability import log_event


def _permission_allows_commit(agent: AgentProfile) -> Tuple[bool, bool]:
    permissions = set(agent.permissions)
    if "git:commit" in permissions:
        return True, False
    if "git:commit:requires-approval" in permissions:
        return True, True
    return False, True


def evaluate_action(action: ActionRequest, agent: AgentProfile) -> PermissionDecision:
    requires_approval = True
    reason = "No matching permission found."

    if action.action_type == "git_commit":
        allowed, approval_required = _permission_allows_commit(agent)
        if allowed:
            requires_approval = approval_required
            reason = "Commit allowed with approval." if approval_required else "Commit allowed."
        else:
            requires_approval = True
            reason = "Commit not allowed; approval required."
    elif action.action_type == "run_tests":
        permissions = set(agent.permissions)
        if "tests:run" in permissions:
            requires_approval = False
            reason = "Test execution allowed."
        elif "tests:run:requires-approval" in permissions:
            requires_approval = True
            reason = "Test execution requires approval."
        else:
            requires_approval = True
            reason = "Test execution not allowed; approval required."
    elif action.action_type == "cursor_prompt":
        permissions = set(agent.permissions)
        if "cursor:prompt" in permissions:
            requires_approval = False
            reason = "Cursor prompt allowed."
        elif "cursor:prompt:requires-approval" in permissions:
            requires_approval = True
            reason = "Cursor prompt requires approval."
        else:
            requires_approval = True
            reason = "Cursor prompt not allowed; approval required."

    log_event(
        "permission_check",
        {
            "action_type": action.action_type,
            "agent": agent.name,
            "requires_approval": requires_approval,
            "reason": reason,
        },
    )
    return PermissionDecision(requires_approval=requires_approval, reason=reason)
