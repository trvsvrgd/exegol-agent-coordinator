from __future__ import annotations

import json
import time
from dataclasses import asdict
from typing import Any, Dict, Optional

from config import ensure_directories, get_log_dir


def log_event(event_type: str, data: Dict[str, Any]) -> None:
    ensure_directories()
    payload = {
        "event_type": event_type,
        "timestamp": time.time(),
        **data,
    }
    log_path = get_log_dir() / "ops.jsonl"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload) + "\n")


class timer:
    def __init__(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        self.event_type = event_type
        self.data = data or {}
        self.start = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        elapsed_ms = (time.perf_counter() - self.start) * 1000
        log_event(
            self.event_type,
            {
                **self.data,
                "elapsed_ms": round(elapsed_ms, 2),
                "status": "error" if exc else "ok",
            },
        )
        return False
