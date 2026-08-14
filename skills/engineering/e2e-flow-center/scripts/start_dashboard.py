#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import venv
import webbrowser


SKILL_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_TEMPLATE = SKILL_ROOT / "assets" / "dashboard"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def runtime_python() -> Path:
    """Keep FastAPI in the user cache, never in the target project."""
    override = os.environ.get("E2E_FLOW_CENTER_PYTHON")
    if override:
        return Path(override)
    cache_dir = Path.home() / ".cache" / "e2e-flow-center" / "runtime"
    executable = cache_dir / "bin" / "python"
    if not executable.exists():
        cache_dir.parent.mkdir(parents=True, exist_ok=True)
        venv.EnvBuilder(with_pip=True, clear=False).create(cache_dir)
    probe = subprocess.run([str(executable), "-c", "import fastapi, uvicorn, yaml"], capture_output=True)
    if probe.returncode != 0:
        result = subprocess.run(
            [str(executable), "-m", "pip", "install", "--disable-pip-version-check", str(DASHBOARD_TEMPLATE)],
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError("无法在用户缓存安装 e2e-flow-center 的 Python 依赖。")
    return executable


def health_check(port: int, token: str, timeout: float = 12.0) -> bool:
    deadline = time.monotonic() + timeout
    request = urllib.request.Request(
        f"http://127.0.0.1:{port}/api/health", headers={"X-E2E-Flow-Center-Token": token}
    )
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(request, timeout=1) as response:
                return response.status == 200
        except OSError:
            time.sleep(0.15)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="从 Skill 启动临时 E2E Flow Center 看板。")
    parser.add_argument("--project", required=True, type=Path, help="目标项目根目录")
    parser.add_argument("--no-open", action="store_true", help="只输出 URL，不打开浏览器")
    args = parser.parse_args()
    project = args.project.resolve()
    if not project.is_dir():
        parser.error(f"项目目录不存在：{project}")
    if not (project / "e2e-flows").is_dir():
        parser.error("项目没有 e2e-flows/；请先使用 e2e-flow-extract。")

    from cleanup_stale_sessions import cleanup_project_sessions

    cleanup_project_sessions(project)
    session = Path(tempfile.mkdtemp(prefix="e2e-flow-center-"))
    runtime = runtime_python()
    dashboard = session / "dashboard"
    shutil.copytree(DASHBOARD_TEMPLATE, dashboard)
    port, token = free_port(), secrets.token_urlsafe(32)
    environment = os.environ.copy()
    environment.update({
        "E2E_FLOW_CENTER_PROJECT": str(project),
        "E2E_FLOW_CENTER_TOKEN": token,
        "PYTHONPATH": str(dashboard / "src") + os.pathsep + environment.get("PYTHONPATH", ""),
    })
    command = [str(runtime), "-m", "uvicorn", "e2e_flow_center.app:create_app", "--factory", "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"]
    process = subprocess.Popen(command, cwd=dashboard, env=environment, start_new_session=True)
    config = {"project": str(project), "port": port, "token": token, "pid": process.pid, "pgid": process.pid, "startedAt": time.time()}
    (session / "session.config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    if not health_check(port, token):
        process.terminate()
        raise RuntimeError(f"看板健康检查失败；临时会话保留在 {session} 以便诊断。")
    url = f"http://127.0.0.1:{port}/?token={token}"
    print(json.dumps({"url": url, "session": str(session)}, ensure_ascii=False))
    if not args.no_open:
        webbrowser.open(url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
