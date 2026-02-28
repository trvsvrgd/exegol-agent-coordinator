from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

from agent_manager import AgentManager
from config import get_log_dir
from llm_router import route_prompt
from models import ActionRequest
from state_store import (
    add_interview_message,
    append_activity,
    load_state,
    update_permission_request,
)
from workspace_execution import WorkspaceExecutor


def _load_ops_events() -> List[Dict[str, Any]]:
    log_path = get_log_dir() / "ops.jsonl"
    if not log_path.exists():
        return []
    events = []
    for line in log_path.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _tooltip(label: str, text: str) -> str:
    safe_text = text.replace('"', "&quot;")
    return f"<span title=\"{safe_text}\">{label}</span>"


def _render_component_legend() -> None:
    st.subheader("System Map")
    legend = [
        ("Dark Throne", "UI layer in ui_dashboard.py (user inputs, approvals)."),
        ("Cloning Vats", "Agent orchestration in agent_manager.py."),
        ("Wayfinder", "LLM routing decisions in llm_router.py."),
        ("Final Order", "Workspace execution in workspace_execution.py."),
        ("Inquisitor", "Permission checks in permission_judge.py."),
    ]
    parts = [f"<strong>{_tooltip(name, desc)}</strong>" for name, desc in legend]
    st.markdown(" • ".join(parts), unsafe_allow_html=True)
    st.caption(
        "Hover the component names to see where each action is executed."
    )


def _render_interview(state: Dict[str, Any]) -> None:
    st.subheader("User Interview")
    for entry in state.get("interview", []):
        with st.chat_message(entry["role"]):
            st.write(entry["content"])

    prompt = st.chat_input("Describe the business pain point")
    if prompt:
        add_interview_message("user", prompt)
        decision = route_prompt(prompt, intent="interview")
        response = f"Interview queued via {decision.provider}. Captured: {prompt}"
        add_interview_message("assistant", response)
        append_activity(
            "Captured interview input",
            {
                "component": "Wayfinder",
                "location": "llm_router.py",
                "llm_used": decision.provider,
                "provider": decision.provider,
            },
        )
        st.rerun()


def _render_activity(state: Dict[str, Any]) -> None:
    st.subheader("Activity Feed")
    activities = list(reversed(state.get("activity", [])))[:10]
    for activity in activities:
        metadata = activity.get("metadata", {})
        component = metadata.get("component", "Unknown")
        location = metadata.get("location", "Unknown")
        llm_used = metadata.get("llm_used", "none")
        detail = (
            f"{_tooltip('Component', 'Subsystem that executed the action')}: {component} | "
            f"{_tooltip('Location', 'Module where the action ran')}: {location} | "
            f"{_tooltip('LLM', 'Provider used for this action')}: {llm_used}"
        )
        st.markdown(f"**{activity['message']}**", unsafe_allow_html=True)
        st.markdown(detail, unsafe_allow_html=True)


def _render_ops_dashboard() -> None:
    st.subheader("Operations Dashboard")
    events = _load_ops_events()
    routing = [e for e in events if e.get("event_type") == "llm_routing"]
    latencies = [e.get("latency_ms", 0) for e in routing if e.get("latency_ms") is not None]
    avg_latency = round(sum(latencies) / len(latencies), 2) if latencies else 0.0

    col1, col2, col3 = st.columns(3)
    col1.metric("LLM Routes", len(routing))
    col2.metric("Avg Routing Latency (ms)", avg_latency)
    col3.metric("Total Events", len(events))

    last_route = next((e for e in reversed(routing)), None)
    if last_route:
        details = (
            f"Provider: {last_route.get('provider')} | "
            f"Reason: {last_route.get('reason')} | "
            f"Latency: {last_route.get('latency_ms')}ms"
        )
        st.markdown(
            f"{_tooltip('Last LLM decision', 'Most recent routing choice')} : {details}",
            unsafe_allow_html=True,
        )

    st.caption("Recent events")
    for event in events[-5:]:
        st.write(f"{event.get('event_type')} :: {event.get('timestamp')}")


def _render_permissions(state: Dict[str, Any]) -> None:
    st.subheader("Permission Requests")
    executor = WorkspaceExecutor()
    pending = [req for req in state.get("permission_requests", []) if req["status"] == "pending"]
    if not pending:
        st.write("No pending approvals.")
        return

    for request in pending:
        st.markdown(f"**{request['title']}**")
        st.write(f"Agent: {request['agent']['name']} ({request['agent']['role']})")
        if request.get("reason"):
            st.markdown(f"_Paused for approval_: {request['reason']}")
        origin = request.get("origin", {})
        if origin:
            origin_line = (
                f"{_tooltip('Origin', 'Permission was evaluated here')}: "
                f"{origin.get('component', 'Unknown')} / {origin.get('location', 'Unknown')}"
            )
            st.markdown(origin_line, unsafe_allow_html=True)
        st.code(request["action"]["description"])
        col1, col2 = st.columns(2)
        if col1.button("Approve", key=f"approve-{request['id']}"):
            action = ActionRequest(
                action_type=request["action"]["action_type"],
                description=request["action"]["description"],
                payload=request["action"]["payload"],
            )
            executor.execute_action(action)
            update_permission_request(request["id"], "approved")
            append_activity(
                "Permission approved and action executed",
                {
                    "component": "Inquisitor",
                    "location": "permission_judge.py",
                    "llm_used": "none",
                },
            )
            st.rerun()
        if col2.button("Deny", key=f"deny-{request['id']}"):
            update_permission_request(request["id"], "denied")
            append_activity(
                "Permission denied",
                {
                    "component": "Inquisitor",
                    "location": "permission_judge.py",
                    "llm_used": "none",
                },
            )
            st.rerun()


def _render_cursor_prompts(state: Dict[str, Any]) -> None:
    st.subheader("Cursor Prompts")
    prompts = state.get("cursor_prompts", [])
    if not prompts:
        st.write("No Cursor prompts queued.")
        return
    st.caption(
        "No actions happen in Cursor unless a prompt is queued here."
    )
    for prompt in reversed(prompts)[-10:]:
        st.markdown(f"**{Path(prompt['repo_path']).name}**")
        st.code(prompt["prompt"])


def main() -> None:
    st.set_page_config(page_title="Exegol - The Dark Throne", layout="wide")
    st.title("Exegol — The Dark Throne")

    state = load_state()

    manager = AgentManager()
    col1, col2, col3 = st.columns(3)
    if col1.button("Run Demo Flow"):
        manager.run_demo_flow()
        append_activity(
            "Demo flow triggered",
            {"component": "Dark Throne", "location": "ui_dashboard.py", "llm_used": "none"},
        )
        st.rerun()
    if col2.button("Run Repo Test Audit"):
        manager.run_repo_test_audit()
        append_activity(
            "Repo test audit triggered",
            {"component": "Dark Throne", "location": "ui_dashboard.py", "llm_used": "none"},
        )
        st.rerun()
    if col3.button("Queue Cursor Prompts"):
        manager.run_cursor_prompt_flow()
        append_activity(
            "Cursor prompt flow triggered",
            {"component": "Dark Throne", "location": "ui_dashboard.py", "llm_used": "none"},
        )
        st.rerun()

    _render_component_legend()
    _render_interview(state)
    _render_activity(state)
    _render_ops_dashboard()
    _render_permissions(state)
    _render_cursor_prompts(state)


if __name__ == "__main__":
    main()
