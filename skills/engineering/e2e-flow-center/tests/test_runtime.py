from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from runtime import process_alive, runtime_cache_dir, venv_python  # noqa: E402


class RuntimeTests(unittest.TestCase):
    def test_venv_python_uses_scripts_on_windows(self) -> None:
        root = Path("C:/cache/runtime")
        self.assertEqual(root / "Scripts" / "python.exe", venv_python(root, platform="win32"))
        self.assertEqual(root / "bin" / "python", venv_python(root, platform="linux"))

    def test_runtime_cache_dir_uses_localappdata_on_windows(self) -> None:
        windows = runtime_cache_dir(
            platform="win32",
            environ={"LOCALAPPDATA": r"C:\Users\dev\AppData\Local"},
        )
        self.assertEqual(Path(r"C:\Users\dev\AppData\Local") / "e2e-flow-center" / "runtime", windows)
        posix = runtime_cache_dir(platform="linux", environ={}, home=Path("/home/dev"))
        self.assertEqual(Path("/home/dev/.cache/e2e-flow-center/runtime"), posix)

    def test_runtime_override_env_wins(self) -> None:
        override = runtime_cache_dir(
            platform="win32",
            environ={"E2E_FLOW_CENTER_RUNTIME": "/tmp/custom-runtime", "LOCALAPPDATA": "C:/ignored"},
        )
        self.assertEqual(Path("/tmp/custom-runtime"), override)

    def test_process_alive_for_current_and_invalid_pids(self) -> None:
        self.assertTrue(process_alive(os.getpid()))
        self.assertFalse(process_alive(0))
        self.assertFalse(process_alive(-1))


if __name__ == "__main__":
    unittest.main()
