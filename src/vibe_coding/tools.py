from __future__ import annotations

import subprocess
from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


ROOT = Path(__file__).resolve().parents[2]
BLOCKED_PATH_PARTS = {".git", ".venv", "__pycache__"}
BLOCKED_FILE_NAMES = {".env"}


def _safe_path(path: str) -> Path:
    target = (ROOT / path).resolve()
    if ROOT not in (target, *target.parents):
        raise ValueError("Path is outside the project.")
    rel = target.relative_to(ROOT)
    if any(part in BLOCKED_PATH_PARTS for part in rel.parts):
        raise ValueError("Path is blocked.")
    if target.name in BLOCKED_FILE_NAMES:
        raise ValueError("This file is blocked.")
    return target


def _command_is_blocked(command: str) -> bool:
    blocked_fragments = (
        "rm -rf",
        "sudo ",
        "chmod -R",
        "chown -R",
        "git reset",
        "git checkout",
        "git clean",
        "mkfs",
        ":(){",
    )
    return any(fragment in command for fragment in blocked_fragments)


class ListFilesInput(BaseModel):
    max_depth: int = Field(default=3, description="Maximum directory depth to list.")


class ListFilesTool(BaseTool):
    name: str = "list_files"
    description: str = "List project files, excluding blocked local files."
    args_schema: type[BaseModel] = ListFilesInput

    def _run(self, max_depth: int = 3) -> str:
        files: list[str] = []
        for path in sorted(ROOT.rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(ROOT)
            if len(rel.parts) > max_depth:
                continue
            if any(part in BLOCKED_PATH_PARTS for part in rel.parts):
                continue
            if path.name in BLOCKED_FILE_NAMES:
                continue
            files.append(str(rel))
        return "\n".join(files) or "(no files)"


class ReadFileInput(BaseModel):
    path: str = Field(description="Project-relative file path.")
    max_chars: int = Field(default=20000, description="Maximum characters to return.")


class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "Read a UTF-8 text file from the project."
    args_schema: type[BaseModel] = ReadFileInput

    def _run(self, path: str, max_chars: int = 20000) -> str:
        target = _safe_path(path)
        if not target.exists():
            return f"File not found: {path}"
        if not target.is_file():
            return f"Not a file: {path}"
        text = target.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + "\n...<truncated>"
        return text


class WriteFileInput(BaseModel):
    path: str = Field(description="Project-relative file path.")
    content: str = Field(description="Full file content to write.")


class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = "Write a UTF-8 text file inside the project."
    args_schema: type[BaseModel] = WriteFileInput

    def _run(self, path: str, content: str) -> str:
        target = _safe_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {target.relative_to(ROOT)} ({len(content)} chars)"


class RunCommandInput(BaseModel):
    command: str = Field(description="Shell command to run in the project directory.")
    timeout: int = Field(default=60, description="Timeout in seconds.")


class RunCommandTool(BaseTool):
    name: str = "run_command"
    description: str = "Run a shell command in the project directory."
    args_schema: type[BaseModel] = RunCommandInput

    def _run(self, command: str, timeout: int = 60) -> str:
        if _command_is_blocked(command):
            return f"Blocked command: {command}"
        result = subprocess.run(
            command,
            cwd=ROOT,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        output = [f"$ {command}", f"exit_code={result.returncode}"]
        if result.stdout:
            output.append("stdout:\n" + result.stdout[-12000:])
        if result.stderr:
            output.append("stderr:\n" + result.stderr[-12000:])
        return "\n".join(output)


class GitDiffInput(BaseModel):
    pass


class GitDiffTool(BaseTool):
    name: str = "git_diff"
    description: str = "Show current git diff for project files."
    args_schema: type[BaseModel] = GitDiffInput

    def _run(self) -> str:
        return RunCommandTool()._run("git diff -- . ':!.env' ':!.venv' ':!.git'", timeout=30)
