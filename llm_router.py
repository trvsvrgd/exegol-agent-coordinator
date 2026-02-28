from __future__ import annotations

import time
from typing import Literal

from models import LLMDecision
from observability import log_event


Provider = Literal["gemini", "self_hosted", "cursor_instructions"]


def route_prompt(prompt: str, intent: str) -> LLMDecision:
    start = time.perf_counter()
    normalized = intent.strip().lower()

    if normalized in {"plan", "interview", "reasoning"}:
        provider: Provider = "gemini"
        reason = "Complex reasoning/interview flow."
    elif normalized in {"bulk", "automation", "low_cost"}:
        provider = "self_hosted"
        reason = "High-volume automation."
    else:
        provider = "cursor_instructions"
        reason = "Heavy code generation delegated to Cursor."

    latency_ms = (time.perf_counter() - start) * 1000
    decision = LLMDecision(
        provider=provider,
        reason=reason,
        latency_ms=round(latency_ms, 2),
    )
    log_event(
        "llm_routing",
        {
            "provider": decision.provider,
            "reason": decision.reason,
            "latency_ms": decision.latency_ms,
        },
    )
    return decision


def format_cursor_instructions(task: str) -> str:
    return (
        "Cursor Action Required:\n"
        f"- Task: {task}\n"
        "- Open the relevant file(s) in Cursor\n"
        "- Apply the suggested edits\n"
        "- Run tests after the change"
    )
