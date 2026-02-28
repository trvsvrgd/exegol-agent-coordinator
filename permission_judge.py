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
