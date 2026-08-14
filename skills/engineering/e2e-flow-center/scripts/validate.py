#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


SOURCE = Path(__file__).resolve().parents[1] / "assets" / "dashboard" / "src"
sys.path.insert(0, str(SOURCE))
from e2e_flow_center.validation import validation_payload  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="完整校验目标项目的 e2e-flows/。")
    parser.add_argument("--project", required=True, type=Path, help="目标项目根目录")
    args = parser.parse_args()
    project = args.project.resolve()
    if not project.is_dir():
        parser.error(f"项目目录不存在：{project}")
    payload = validation_payload(project)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["flowDirectoryExists"] and payload["invalidFlowCount"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
