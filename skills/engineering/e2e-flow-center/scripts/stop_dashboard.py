#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import tempfile
import time


def trusted_session(path: Path) -> Path:
    resolved = path.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if resolved.parent != temp_root or not resolved.name.startswith("e2e-flow-center-"):
        raise ValueError("会话目录必须是系统临时目录下的 e2e-flow-center-*。")
    return resolved


def process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True


def stop_session(session: Path) -> str:
    session = trusted_session(session)
    config_path = session / "session.config.json"
    if not config_path.is_file():
        return "会话缺少配置；为避免误删，未处理。"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        pid, pgid = int(config["pid"]), int(config["pgid"])
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        return f"会话配置无效；为避免误删，未处理：{error}"
    if process_alive(pid):
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
            pass
        except PermissionError as error:
            return f"无权限终止会话进程；保留目录：{error}"
    shutil.rmtree(session)
    return "已停止并清理临时会话。"


def main() -> int:
    parser = argparse.ArgumentParser(description="停止并清理一份 e2e-flow-center 临时会话。")
    parser.add_argument("--session", required=True, type=Path)
    args = parser.parse_args()
    try:
        print(stop_session(args.session))
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
