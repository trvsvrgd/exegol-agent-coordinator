from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

from git import Repo

from config import ensure_directories, get_workspace_dir
from models import ActionRequest
from observability import log_event, timer


class WorkspaceExecutor:
    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        ensure_directories()
        self.workspace_root = workspace_root or get_workspace_dir()

    def ensure_repo(self, repo_name: str) -> Repo:
        repo_path = self.workspace_root / repo_name
        repo_path.mkdir(parents=True, exist_ok=True)
        if (repo_path / ".git").exists():
            repo = Repo(repo_path)
        else:
            repo = Repo.init(repo_path)
            repo.config_writer().set_value("user", "name", "Exegol Bot").release()
            repo.config_writer().set_value("user", "email", "exegol@local").release()
        return repo

    def execute_action(self, action: ActionRequest) -> str:
        if action.action_type == "git_commit":
            return self._execute_git_commit(action)
        raise ValueError(f"Unsupported action: {action.action_type}")

    def _execute_git_commit(self, action: ActionRequest) -> str:
        repo_name = action.payload.get("repo", "demo-repo")
        message = action.payload.get("message", "demo commit")
        with timer("workspace_git_commit", {"repo": repo_name}):
            repo = self.ensure_repo(repo_name)
            demo_file = Path(repo.working_tree_dir) / "demo.txt"
            demo_file.write_text(
                f"Demo update at {time.time()}\n",
                encoding="utf-8",
            )
            repo.index.add([str(demo_file)])
            commit = repo.index.commit(message)
            log_event(
                "git_commit",
                {"repo": repo_name, "commit": commit.hexsha, "message": message},
            )
            return commit.hexsha

    def run_in_sandbox(self, command: str) -> str:
        log_event("sandbox_request", {"command": command})
        return "sandbox_execution_stub"
