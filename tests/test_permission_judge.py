from models import ActionRequest, AgentProfile
from permission_judge import evaluate_action


def test_commit_requires_approval_when_flagged() -> None:
    agent = AgentProfile(
        name="Maul", role="Builder", permissions=["git:commit:requires-approval"]
    )
    action = ActionRequest(
        action_type="git_commit",
        description="Commit",
        payload={"repo": "demo"},
    )
    decision = evaluate_action(action, agent)
    assert decision.requires_approval is True


def test_commit_allowed_without_approval() -> None:
    agent = AgentProfile(name="Vader", role="Lead", permissions=["git:commit"])
    action = ActionRequest(
        action_type="git_commit",
        description="Commit",
        payload={"repo": "demo"},
    )
    decision = evaluate_action(action, agent)
    assert decision.requires_approval is False
