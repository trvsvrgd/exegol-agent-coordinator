from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def _env_path(name: str, default: Path) -> Path:
    return Path(os.getenv(name, str(default))).resolve()


def get_state_dir() -> Path:
    return _env_path("EXEGOL_STATE_DIR", BASE_DIR / "state")


def get_log_dir() -> Path:
    return _env_path("EXEGOL_LOG_DIR", BASE_DIR / "logs")


def get_workspace_dir() -> Path:
    return _env_path("EXEGOL_WORKSPACE_DIR", BASE_DIR / "exegol_workspace")


def get_plan_path() -> Path:
    return _env_path("EXEGOL_PLAN_PATH", BASE_DIR / "plan.md")


def get_agents_path() -> Path:
    return _env_path("EXEGOL_AGENTS_PATH", BASE_DIR / "agents.md")


def get_sandbox_mode() -> str:
    return os.getenv("EXEGOL_SANDBOX_MODE", "noop").strip().lower()


def ensure_directories() -> None:
    for path in (get_state_dir(), get_log_dir(), get_workspace_dir()):
        path.mkdir(parents=True, exist_ok=True)
