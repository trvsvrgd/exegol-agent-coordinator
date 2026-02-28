from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AgentProfile:
    name: str
    role: str
    permissions: List[str] = field(default_factory=list)


@dataclass
class ActionRequest:
    action_type: str
    description: str
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PermissionDecision:
    requires_approval: bool
    reason: str
    request_id: Optional[str] = None


@dataclass
class LLMDecision:
    provider: str
    reason: str
    latency_ms: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
