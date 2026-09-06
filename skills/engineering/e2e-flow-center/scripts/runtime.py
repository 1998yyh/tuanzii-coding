#!/usr/bin/env python3
"""Shared interpreter + process helpers for e2e-flow-center scripts.

Dashboard and the complete validator must use the same user-cache runtime so
Windows, macOS and Linux can invoke `python` or `python3` without installing
into the target project.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import signal
import subprocess
import sys
import time


SKILL_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_TEMPLATE = SKILL_ROOT / "assets" / "dashboard"
REQUIRED_PYTHON = (3, 11)


def venv_python(venv_dir: Path, *, platform: str | None = None) -> Path:
    """Return the venv interpreter path for this OS."""
    if (platform or sys.platform) == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def runtime_cache_dir(
    *,
    platform: str | None = None,
    environ: dict[str, str] | None = None,
    home: Path | None = None,
) -> Path:
    """Keep FastAPI/PyYAML in the user cache, never in the target project."""
    env = os.environ if environ is None else environ
    override = env.get("E2E_FLOW_CENTER_RUNTIME")
    if override:
        return Path(override)
    if (platform or sys.platform) == "win32":
        base = env.get("LOCALAPPDATA")
        root = Path(base) if base else (home or Path.home()) / "AppData" / "Local"
        return Path(root) / "e2e-flow-center" / "runtime"
    return (home or Path.home()) / ".cache" / "e2e-flow-center" / "runtime"


def current_has(modules: tuple[str, ...]) -> bool:
    return all(importlib.util.find_spec(name) is not None for name in modules)


def _probe(executable: Path, modules: tuple[str, ...]) -> bool:
    if not executable.is_file():
        return False
    code = "; ".join(f"import {name}" for name in modules)
    probe = subprocess.run([str(executable), "-c", code], capture_output=True)
    return probe.returncode == 0


def ensure_runtime_python(modules: tuple[str, ...]) -> Path:
    """Return an interpreter that can import *modules*.

    Prefers E2E_FLOW_CENTER_PYTHON, then the current interpreter, then a
    user-cache venv installed from the dashboard package.
    """
    if sys.version_info < REQUIRED_PYTHON:
        raise RuntimeError(
            f"e2e-flow-center 需要 Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+，当前是 {sys.version.split()[0]}。"
        )
    override = os.environ.get("E2E_FLOW_CENTER_PYTHON")
    if override:
        path = Path(override)
        if not path.is_file():
            raise RuntimeError(f"E2E_FLOW_CENTER_PYTHON 不是可执行文件：{path}")
        return path
    if current_has(modules):
        return Path(sys.executable)
    cache_dir = runtime_cache_dir()
    executable = venv_python(cache_dir)
    if not executable.is_file():
        cache_dir.parent.mkdir(parents=True, exist_ok=True)
        import venv

        venv.EnvBuilder(with_pip=True, clear=False).create(cache_dir)
    if not _probe(executable, modules):
        result = subprocess.run(
            [str(executable), "-m", "pip", "install", "--disable-pip-version-check", str(DASHBOARD_TEMPLATE)],
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError("无法在用户缓存安装 e2e-flow-center 的 Python 依赖。")
    if not _probe(executable, modules):
        raise RuntimeError(f"用户缓存解释器无法导入 {', '.join(modules)}：{executable}")
    return executable


def reexec_if_needed(modules: tuple[str, ...], script: Path | None = None) -> None:
    """Re-run the current script with a capable interpreter."""
    runtime = ensure_runtime_python(modules)
    if runtime.resolve() == Path(sys.executable).resolve():
        return
    target = Path(script or sys.argv[0]).resolve()
    raise SystemExit(subprocess.call([str(runtime), str(target), *sys.argv[1:]]))


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        STILL_ACTIVE = 259
        ERROR_ACCESS_DENIED = 5
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if handle:
            try:
                code = wintypes.DWORD()
                if ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code)) == 0:
                    return False
                return code.value == STILL_ACTIVE
            finally:
                ctypes.windll.kernel32.CloseHandle(handle)
        return ctypes.windll.kernel32.GetLastError() == ERROR_ACCESS_DENIED
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def stop_process_tree(pid: int, pgid: int) -> str | None:
    """Stop the recorded process tree. Return an error message, or None on success/already dead."""
    if not process_alive(pid):
        return None
    if sys.platform == "win32":
        result = subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            capture_output=True,
            text=True,
        )
        deadline = time.monotonic() + 4
        while process_alive(pid) and time.monotonic() < deadline:
            time.sleep(0.1)
        if process_alive(pid):
            return f"无法终止会话进程 {pid}：{result.stderr.strip() or result.stdout.strip() or result.returncode}"
        return None
    try:
        if os.getpgid(pid) != pgid:
            return "进程组与会话记录不符；为避免误杀，未处理。"
        os.killpg(pgid, signal.SIGTERM)
        deadline = time.monotonic() + 4
        while process_alive(pid) and time.monotonic() < deadline:
            time.sleep(0.1)
        if process_alive(pid):
            os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        return None
    except PermissionError as error:
        return f"无权限终止会话进程；保留目录：{error}"
    return None
