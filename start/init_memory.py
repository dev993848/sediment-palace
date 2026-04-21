from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

AGENTS = ("codex", "opencode", "qwen", "kimi", "claude")
SCOPES = ("local", "global")


def _now_stamp() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def _backup(path: Path) -> Path | None:
    if not path.exists():
        return None
    backup_path = path.with_suffix(path.suffix + f".bak.{_now_stamp()}")
    shutil.copy2(path, backup_path)
    return backup_path


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        return {}
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return parsed


def _save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _toml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _build_codex_block(repo_root: Path, workspace: Path) -> str:
    repo = _toml_string(str(repo_root))
    root = _toml_string(str(workspace))
    return (
        "[mcp_servers.sediment_palace]\n"
        'command = "python"\n'
        'args = [ "-m", "sediment_palace.main" ]\n'
        f"cwd = {repo}\n\n"
        "[mcp_servers.sediment_palace.env]\n"
        f"SEDIMENT_PROJECT_ROOT = {root}\n"
    )


def _replace_codex_block(original: str, block: str) -> str:
    lines = original.splitlines()
    out: list[str] = []
    i = 0
    skipping = False
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("[mcp_servers.sediment_palace]"):
            skipping = True
            i += 1
            continue
        if skipping and stripped.startswith("[") and stripped.endswith("]"):
            skipping = False
        if not skipping:
            out.append(line)
        i += 1

    text = "\n".join(out).rstrip()
    if text:
        text += "\n\n"
    text += block.strip() + "\n"
    return text


def ensure_dependencies(repo_root: Path, *, auto_install: bool) -> None:
    missing: list[str] = []
    try:
        __import__("yaml")
    except Exception:
        missing.append("pyyaml")
    try:
        __import__("sediment_palace")
    except Exception:
        missing.append("sediment_palace")

    if not missing:
        print("Dependencies: OK")
        return

    print(f"Missing dependencies: {', '.join(sorted(set(missing)))}")
    if not auto_install:
        raise RuntimeError("Dependencies are missing. Re-run without --no-install-deps.")

    print("Installing dependencies: python -m pip install -e .[dev]")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
        cwd=str(repo_root),
        check=True,
    )
    print("Dependencies installed.")


def initialize_memory_layout(workspace: Path) -> None:
    from sediment_palace.infrastructure.filesystem_memory_repository import (
        FileSystemMemoryRepository,
    )

    repo = FileSystemMemoryRepository(project_root=workspace)
    repo.ensure_layout()


def sync_agent_bootstrap(repo_root: Path, workspace: Path, *, dry_run: bool) -> str:
    source = repo_root / "AGENT_BOOTSTRAP.md"
    target = workspace / "AGENT_BOOTSTRAP.md"
    if not source.exists():
        return f"AGENT_BOOTSTRAP sync skipped: source not found at {source}"

    if source.resolve() == target.resolve():
        return f"AGENT_BOOTSTRAP already in place: {target}"

    if dry_run:
        action = "update" if target.exists() else "create"
        return f"[dry-run] AGENT_BOOTSTRAP => {action} {target}"

    target.parent.mkdir(parents=True, exist_ok=True)
    backup = _backup(target)
    shutil.copy2(source, target)
    message = f"AGENT_BOOTSTRAP synced: {target}"
    if backup:
        message += f" (backup: {backup})"
    return message


def sync_agent_instruction_files(
    repo_root: Path,
    workspace: Path,
    agents: list[str],
    *,
    dry_run: bool,
) -> list[str]:
    source = repo_root / "AGENT_BOOTSTRAP.md"
    if not source.exists():
        return [f"Instruction files skipped: source not found at {source}"]

    source_text = source.read_text(encoding="utf-8")
    header = "<!-- AUTO-GENERATED: sync with AGENT_BOOTSTRAP.md -->\n\n"
    content = header + source_text

    target_files: dict[str, list[str]] = {
        "codex": ["AGENTS.md", "CODEX.md"],
        "claude": ["CLAUDE.md", "AGENTS.md"],
        "qwen": ["QWEN.md", "AGENTS.md"],
        "opencode": ["AGENTS.md", "OPENCODE.md"],
        "kimi": ["AGENTS.md", "KIMI.md"],
    }
    planned: set[str] = set()
    for agent in agents:
        for name in target_files.get(agent, []):
            planned.add(name)

    results: list[str] = []
    for rel_name in sorted(planned):
        target = workspace / rel_name
        if dry_run:
            action = "update" if target.exists() else "create"
            results.append(f"[dry-run] instructions => {action} {target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        backup = _backup(target)
        target.write_text(content, encoding="utf-8")
        message = f"instructions synced: {target}"
        if backup:
            message += f" (backup: {backup})"
        results.append(message)
    return results


def update_codex(repo_root: Path, workspace: Path, dry_run: bool, scope: str) -> str:
    path = workspace / ".codex" / "config.toml" if scope == "local" else Path.home() / ".codex" / "config.toml"
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    block = _build_codex_block(repo_root=repo_root, workspace=workspace)
    updated = _replace_codex_block(original, block)
    if dry_run:
        return f"[dry-run] codex => {path}"
    path.parent.mkdir(parents=True, exist_ok=True)
    backup = _backup(path)
    path.write_text(updated, encoding="utf-8")
    return f"codex => {path}" + (f" (backup: {backup})" if backup else "")


def update_claude(repo_root: Path, workspace: Path, dry_run: bool, scope: str) -> str:
    _ = repo_root
    path = workspace / ".mcp.json" if scope == "local" else Path.home() / ".claude.json"
    data = _load_json(path)
    mcp = data.setdefault("mcpServers", {})
    if not isinstance(mcp, dict):
        raise ValueError("Invalid .claude.json: mcpServers must be an object")
    mcp["sediment_palace"] = {
        "command": "python",
        "args": ["-m", "sediment_palace.main"],
        "env": {"SEDIMENT_PROJECT_ROOT": str(workspace)},
        "type": "stdio",
    }
    if dry_run:
        return f"[dry-run] claude => {path}"
    backup = _backup(path)
    _save_json(path, data)
    return f"claude => {path}" + (f" (backup: {backup})" if backup else "")


def update_qwen(repo_root: Path, workspace: Path, dry_run: bool, scope: str) -> str:
    path = workspace / ".qwen" / "settings.json" if scope == "local" else Path.home() / ".qwen" / "settings.json"
    data = _load_json(path)
    mcp = data.setdefault("mcpServers", {})
    if not isinstance(mcp, dict):
        raise ValueError("Invalid qwen settings: mcpServers must be an object")
    mcp["sediment_palace"] = {
        "command": "python",
        "args": ["-m", "sediment_palace.main"],
        "cwd": str(repo_root),
        "env": {"SEDIMENT_PROJECT_ROOT": str(workspace)},
    }
    if dry_run:
        return f"[dry-run] qwen => {path}"
    backup = _backup(path)
    _save_json(path, data)
    return f"qwen => {path}" + (f" (backup: {backup})" if backup else "")


def update_opencode(repo_root: Path, workspace: Path, dry_run: bool, scope: str) -> str:
    path = (
        workspace / ".opencode" / "opencode.json"
        if scope == "local"
        else Path.home() / ".config" / "opencode" / "opencode.json"
    )
    data = _load_json(path)
    mcp = data.setdefault("mcp", {})
    if not isinstance(mcp, dict):
        raise ValueError("Invalid opencode config: mcp must be an object")
    mcp["sediment_palace"] = {
        "command": ["python", "-m", "sediment_palace.main"],
        "enabled": True,
        "type": "local",
        "cwd": str(repo_root),
        "env": {"SEDIMENT_PROJECT_ROOT": str(workspace)},
    }
    if dry_run:
        return f"[dry-run] opencode => {path}"
    backup = _backup(path)
    _save_json(path, data)
    return f"opencode => {path}" + (f" (backup: {backup})" if backup else "")


def update_kimi(repo_root: Path, workspace: Path, dry_run: bool, scope: str) -> str:
    _ = repo_root
    if scope == "local":
        existing = workspace / ".kimi" / "settings.json"
        data = _load_json(existing)
        mcp = data.setdefault("mcpServers", {})
        if not isinstance(mcp, dict):
            raise ValueError("Invalid kimi settings: mcpServers must be an object")
        mcp["sediment_palace"] = {
            "command": "python",
            "args": ["-m", "sediment_palace.main"],
            "env": {"SEDIMENT_PROJECT_ROOT": str(workspace)},
        }
        if dry_run:
            return f"[dry-run] kimi => {existing}"
        backup = _backup(existing)
        _save_json(existing, data)
        return f"kimi => {existing}" + (f" (backup: {backup})" if backup else "")

    candidates = [
        Path.home() / ".kimi" / "settings.json",
        Path.home() / ".kimicode" / "settings.json",
        Path.home() / ".config" / "kimi" / "settings.json",
    ]
    existing = next((p for p in candidates if p.exists()), None)
    if existing is None:
        template_dir = workspace / ".kimi"
        template_path = template_dir / "kimi_code_mcp_template.json"
        payload = {
            "mcpServers": {
                "sediment_palace": {
                    "command": "python",
                    "args": ["-m", "sediment_palace.main"],
                    "env": {"SEDIMENT_PROJECT_ROOT": str(workspace)},
                }
            }
        }
        if dry_run:
            return f"[dry-run] kimi => config not found. Would create template at {template_path}"
        template_dir.mkdir(parents=True, exist_ok=True)
        template_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return "kimi => global config not found; generated template: " f"{template_path}"

    data = _load_json(existing)
    mcp = data.setdefault("mcpServers", {})
    if not isinstance(mcp, dict):
        raise ValueError("Invalid kimi settings: mcpServers must be an object")
    mcp["sediment_palace"] = {
        "command": "python",
        "args": ["-m", "sediment_palace.main"],
        "env": {"SEDIMENT_PROJECT_ROOT": str(workspace)},
    }
    if dry_run:
        return f"[dry-run] kimi => {existing}"
    backup = _backup(existing)
    _save_json(existing, data)
    return f"kimi => {existing}" + (f" (backup: {backup})" if backup else "")


def parse_agents(raw: str | None) -> list[str]:
    if not raw:
        return []
    items = [p.strip().lower() for p in raw.split(",") if p.strip()]
    unique: list[str] = []
    for item in items:
        if item not in AGENTS:
            raise ValueError(f"Unknown agent: {item}. Allowed: {', '.join(AGENTS)}")
        if item not in unique:
            unique.append(item)
    return unique


def interactive_agents() -> list[str]:
    print("Select agents (comma-separated): codex, opencode, qwen, kimi, claude")
    raw = input("> ").strip()
    return parse_agents(raw)


def interactive_workspace(default_workspace: Path) -> Path:
    print(f"Workspace path [{default_workspace}]:")
    raw = input("> ").strip()
    return Path(raw) if raw else default_workspace


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize SedimentPalace memory integration for local agents.",
    )
    parser.add_argument(
        "--workspace",
        help="Target working folder where memory should operate (SEDIMENT_PROJECT_ROOT).",
    )
    parser.add_argument(
        "--agents",
        help="Comma-separated list: codex,opencode,qwen,kimi,claude",
    )
    parser.add_argument(
        "--scope",
        choices=SCOPES,
        default="local",
        help="Config scope: local (default, writes to workspace) or global (writes to user profile).",
    )
    parser.add_argument(
        "--no-install-deps",
        action="store_true",
        help="Only check dependencies; do not install automatically.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without writing files.",
    )
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[1]
    default_workspace = Path.cwd().resolve()

    workspace = Path(args.workspace).resolve() if args.workspace else interactive_workspace(default_workspace).resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    agents = parse_agents(args.agents) if args.agents else interactive_agents()
    if not agents:
        raise ValueError("No agents selected.")

    auto_install = not args.no_install_deps
    ensure_dependencies(repo_root=repo_root, auto_install=auto_install)
    if args.dry_run:
        print(f"[dry-run] memory layout => {workspace / 'memory'}")
    else:
        initialize_memory_layout(workspace)
        print(f"Memory layout initialized: {workspace / 'memory'}")
    print(sync_agent_bootstrap(repo_root=repo_root, workspace=workspace, dry_run=args.dry_run))
    for line in sync_agent_instruction_files(
        repo_root=repo_root,
        workspace=workspace,
        agents=agents,
        dry_run=args.dry_run,
    ):
        print(line)

    updaters = {
        "codex": update_codex,
        "opencode": update_opencode,
        "qwen": update_qwen,
        "kimi": update_kimi,
        "claude": update_claude,
    }

    print(f"Repository root: {repo_root}")
    print(f"Workspace root: {workspace}")
    print(f"Agents: {', '.join(agents)}")
    print("")

    for agent in agents:
        updater = updaters[agent]
        message = updater(repo_root=repo_root, workspace=workspace, dry_run=args.dry_run, scope=args.scope)
        print(message)

    print("")
    if args.dry_run:
        print("Dry-run completed.")
    else:
        print("Initialization completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
