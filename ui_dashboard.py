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
        append_activity("Captured interview input", {"provider": decision.provider})
        st.experimental_rerun()


def _render_activity(state: Dict[str, Any]) -> None:
    st.subheader("Activity Feed")
    activities = list(reversed(state.get("activity", [])))[:10]
    for activity in activities:
        st.write(f"- {activity['message']}")


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
            append_activity("Permission approved and action executed")
            st.experimental_rerun()
        if col2.button("Deny", key=f"deny-{request['id']}"):
            update_permission_request(request["id"], "denied")
            append_activity("Permission denied")
            st.experimental_rerun()


def main() -> None:
    st.set_page_config(page_title="Exegol - The Dark Throne", layout="wide")
    st.title("Exegol — The Dark Throne")

    state = load_state()

    if st.button("Run Demo Flow"):
        manager = AgentManager()
        manager.run_demo_flow()
        append_activity("Demo flow triggered")
        st.experimental_rerun()

    _render_interview(state)
    _render_activity(state)
    _render_ops_dashboard()
    _render_permissions(state)


if __name__ == "__main__":
    main()
