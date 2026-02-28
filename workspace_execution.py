from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

from git import Repo

from config import ensure_directories, get_sandbox_mode, get_workspace_dir
from models import ActionRequest
from observability import log_event, timer
from state_store import add_cursor_prompt, append_activity


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
        if action.action_type == "run_tests":
            return self._execute_run_tests(action)
        if action.action_type == "cursor_prompt":
            return self._execute_cursor_prompt(action)
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

    def list_repos(self) -> Tuple[Path, ...]:
        repos = []
        for entry in self.workspace_root.iterdir():
            if entry.is_dir() and (entry / ".git").exists():
                repos.append(entry)
        return tuple(sorted(repos))

    def _run_tests_noop(self, repo_path: Path, command: str) -> Dict[str, object]:
        return {
            "status": "skipped",
            "exit_code": None,
            "output": "Sandbox mode is noop; no tests executed.",
            "command": command,
            "repo_path": str(repo_path),
            "runner": "noop",
        }

    def _run_tests_docker(self, repo_path: Path, command: str) -> Dict[str, object]:
        try:
            import docker
        except ImportError as exc:
            raise RuntimeError("docker SDK not installed") from exc

        client = docker.from_env()
        image = "python:3.11-slim"
        volumes = {str(repo_path): {"bind": "/repo", "mode": "rw"}}
        container = client.containers.run(
            image=image,
            command=["bash", "-lc", command],
            volumes=volumes,
            working_dir="/repo",
            detach=True,
        )
        result = container.wait()
        output = container.logs().decode("utf-8", errors="replace")
        container.remove(force=True)
        return {
            "status": "success" if result.get("StatusCode") == 0 else "failed",
            "exit_code": result.get("StatusCode"),
            "output": output,
            "command": command,
            "repo_path": str(repo_path),
            "runner": "docker",
        }

    def _update_plan_with_result(self, repo_path: Path, result: Dict[str, object]) -> None:
        plan_path = repo_path / "plan.md"
        if plan_path.exists():
            content = plan_path.read_text(encoding="utf-8")
        else:
            content = "# Plan\n\n"

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        status = result.get("status")
        command = result.get("command")
        update_lines = [
            "",
            f"## Requirements Update ({timestamp})",
            f"- Test command: `{command}`",
            f"- Result: {status}",
        ]
        if status != "success":
            update_lines.append("- Requirement: Investigate failing tests")
        content = content.rstrip() + "\n" + "\n".join(update_lines) + "\n"
        plan_path.write_text(content, encoding="utf-8")

    def _execute_run_tests(self, action: ActionRequest) -> str:
        repo_path = Path(action.payload.get("repo_path", ""))
        command = action.payload.get("command", "pytest")
        update_plan = action.payload.get("update_plan", True)
        if not repo_path.exists():
            raise FileNotFoundError(f"Repo path not found: {repo_path}")

        mode = get_sandbox_mode()
        with timer("workspace_run_tests", {"repo_path": str(repo_path), "mode": mode}):
            if mode == "docker":
                result = self._run_tests_docker(repo_path, command)
            else:
                result = self._run_tests_noop(repo_path, command)

        if update_plan:
            self._update_plan_with_result(repo_path, result)

        log_event(
            "test_run",
            {
                "repo_path": str(repo_path),
                "status": result.get("status"),
                "runner": result.get("runner"),
            },
        )
        append_activity(
            f"Tests executed for {repo_path.name}",
            {"status": result.get("status"), "runner": result.get("runner")},
        )
        return str(result.get("status"))

    def _execute_cursor_prompt(self, action: ActionRequest) -> str:
        repo_path = action.payload.get("repo_path", "")
        prompt = action.payload.get("prompt", "")
        add_cursor_prompt(repo_path, prompt)
        append_activity(f"Cursor prompt queued for {Path(repo_path).name}")
        return "queued"

    def run_in_sandbox(self, command: str) -> str:
        log_event("sandbox_request", {"command": command})
        return "sandbox_execution_stub"
