from __future__ import annotations

import json
import time
import uuid
from typing import Any, Dict, List, Optional

from config import ensure_directories, get_state_dir
from observability import log_event


def _default_state() -> Dict[str, Any]:
    return {
        "activity": [],
        "permission_requests": [],
        "interview": [],
        "last_updated": time.time(),
    }


def _state_path():
    return get_state_dir() / "runtime_state.json"


def load_state() -> Dict[str, Any]:
    ensure_directories()
    path = _state_path()
    if not path.exists():
        return _default_state()
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state: Dict[str, Any]) -> None:
    ensure_directories()
    state["last_updated"] = time.time()
    path = _state_path()
    with path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, indent=2)


def append_activity(message: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    state = load_state()
    state["activity"].append(
        {
            "id": str(uuid.uuid4()),
            "message": message,
            "metadata": metadata or {},
            "timestamp": time.time(),
        }
    )
    save_state(state)
    log_event("activity", {"message": message, "metadata": metadata or {}})


def add_permission_request(
    title: str, action: Dict[str, Any], agent: Dict[str, Any]
) -> str:
    state = load_state()
    request_id = str(uuid.uuid4())
    state["permission_requests"].append(
        {
            "id": request_id,
            "title": title,
            "action": action,
            "agent": agent,
            "status": "pending",
            "timestamp": time.time(),
        }
    )
    save_state(state)
    log_event("permission_request", {"request_id": request_id, "title": title})
    return request_id


def update_permission_request(request_id: str, status: str) -> None:
    state = load_state()
    for request in state["permission_requests"]:
        if request["id"] == request_id:
            request["status"] = status
            request["resolved_at"] = time.time()
            break
    save_state(state)
    log_event("permission_decision", {"request_id": request_id, "status": status})


def add_interview_message(role: str, content: str) -> None:
    state = load_state()
    state["interview"].append(
        {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": time.time(),
        }
    )
    save_state(state)
