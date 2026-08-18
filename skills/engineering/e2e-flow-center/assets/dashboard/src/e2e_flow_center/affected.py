"""Read-only git working-tree change detection and flow impact matching."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any
import re
import subprocess


@lru_cache(maxsize=512)
def _segment_pattern(segment: str) -> re.Pattern[str]:
    """Translate wildcards inside one path segment; '*' and '?' never cross '/'."""
    parts: list[str] = []
    for char in segment:
        if char == "*":
            parts.append("[^/]*")
        elif char == "?":
            parts.append("[^/]")
        else:
            parts.append(re.escape(char))
    return re.compile("".join(parts) + r"\Z")


def _glob_match(pattern_parts: tuple[str, ...], path_parts: tuple[str, ...]) -> bool:
    """Segment-wise glob match: a lone '**' segment matches zero or more whole
    segments. The old regex translation stacked ambiguous '(?:.*/)?' groups and
    backtracked catastrophically on repeated '**/' patterns; this DP is O(P*D)."""
    width = len(path_parts)
    dp = [False] * (width + 1)
    dp[width] = True
    for part in reversed(pattern_parts):
        nxt = [False] * (width + 1)
        if part == "**":
            reachable = False
            for j in range(width, -1, -1):
                reachable = reachable or dp[j]
                nxt[j] = reachable
        else:
            regex = _segment_pattern(part)
            for j in range(width):
                nxt[j] = dp[j + 1] and regex.match(path_parts[j]) is not None
        dp = nxt
    return dp[0]


@lru_cache(maxsize=4096)
def _glob_matches(pattern: str, path: str) -> bool:
    return _glob_match(tuple(pattern.split("/")), tuple(path.split("/")))


def _run_git(project_root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError, UnicodeDecodeError):
        # UnicodeDecodeError is a ValueError, not an OSError: non-UTF-8 filenames in
        # text=True output must degrade to "git unavailable", not crash the payload.
        return None
    return result.stdout if result.returncode == 0 else None


def git_changed_paths(project_root: Path) -> tuple[list[str], bool]:
    """Project-relative uncommitted changes plus untracked files. Returns (paths, git_available)."""
    if _run_git(project_root, "rev-parse", "--is-inside-work-tree") is None:
        return [], False
    top = _run_git(project_root, "rev-parse", "--show-toplevel")
    if top is None:
        return [], True
    try:
        relative = project_root.resolve().relative_to(Path(top.strip()).resolve())
    except ValueError:
        # project_root outside its own repository (exotic setups); nothing is project-relative.
        return [], True
    prefix = "" if str(relative) == "." else relative.as_posix()
    marker = f"{prefix}/" if prefix else ""
    chunks = [
        # All three outputs are repository-root relative; names outside project_root are dropped below.
        # Working tree vs HEAD (staged + unstaged); fails on repositories with no commits yet.
        _run_git(project_root, "diff", "--name-only", "-z", "HEAD") or "",
        # Staged entries are all we have when HEAD does not exist.
        _run_git(project_root, "diff", "--name-only", "-z", "--cached") or "",
        _run_git(project_root, "ls-files", "--others", "--exclude-standard", "--full-name", "-z") or "",
    ]
    paths = {
        path[len(marker):] if marker else path
        for chunk in chunks
        for path in chunk.split("\0")
        if path and (not marker or path.startswith(marker))
    }
    return sorted(paths), True


def flow_impact(document: dict[str, Any], changed_paths: list[str]) -> tuple[bool, list[str]]:
    """Match a flow's path globs against changed files. Returns (affected, reasons)."""
    reasons: list[str] = []
    if changed_paths and document.get("alwaysRunOnAffected") is True:
        reasons.append("always-run")
    patterns = [pattern for pattern in document.get("paths") or [] if isinstance(pattern, str)]
    if any(
        _glob_matches(pattern, path)
        for pattern in patterns
        for path in changed_paths
    ):
        reasons.append("path-match")
    return bool(reasons), reasons
