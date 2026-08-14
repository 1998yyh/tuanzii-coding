#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def cleanup_project_sessions(project: Path) -> list[str]:
    """Remove only dead, trusted sessions belonging to this exact project."""
    project = project.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    messages: list[str] = []
    for session in temp_root.glob("e2e-flow-center-*"):
        if not session.is_dir() or session.parent != temp_root:
            continue
        config_path = session / "session.config.json"
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
            if Path(config["project"]).resolve() != project:
                continue
            pid = int(config["pid"])
        except (OSError, ValueError, KeyError, json.JSONDecodeError):
            messages.append(f"保留 {session.name}：配置不可信或不完整。")
            continue
        if _alive(pid):
            continue
        shutil.rmtree(session)
        messages.append(f"已清理失效会话 {session.name}。")
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description="清理指定项目遗留的失效 e2e-flow-center 会话。")
    parser.add_argument("--project", required=True, type=Path)
    args = parser.parse_args()
    if not args.project.is_dir():
        parser.error(f"项目目录不存在：{args.project}")
    for message in cleanup_project_sessions(args.project):
        print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
