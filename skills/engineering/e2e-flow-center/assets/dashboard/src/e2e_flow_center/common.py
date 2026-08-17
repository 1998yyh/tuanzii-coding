"""Shared lifecycle, review-provenance and path/text rules for flows and reports."""
from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any


LIFECYCLE_STATUSES = {"draft", "ready", "active", "retired"}
REVIEW_ALLOWED_BASIS = {
    "manual": {"pending-user-confirmation", "user-confirmed"},
    "source-validated": {"source-evidence-and-schema-validation"},
}


def is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_relative_path(value: Any) -> bool:
    """Accept only project-relative POSIX paths; reject absolute, '..', backslashes and '.'."""
    if not is_text(value) or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and ".." not in path.parts and str(path) not in {"", "."}


def review_issues(review: Any, status: Any) -> list[tuple[str, str]]:
    """Validate review provenance against the flow status. Returns (field, message) pairs."""
    issues: list[tuple[str, str]] = []
    if review is None:
        if status in {"ready", "active"}:
            issues.append(("review", f"status 为 {status} 时必须记录验收来源。"))
        return issues
    if not isinstance(review, dict):
        issues.append(("review", "必须是对象。"))
        return issues
    mode, basis = review.get("mode"), review.get("basis")
    if mode not in REVIEW_ALLOWED_BASIS:
        issues.append(("review.mode", "必须是 manual 或 source-validated。"))
        return issues
    if basis not in REVIEW_ALLOWED_BASIS[mode]:
        issues.append(("review.basis", "与 review.mode 的组合不合法。"))
    if status in {"ready", "active"} and basis == "pending-user-confirmation":
        issues.append(("review.basis", "待人工确认的流程不能是 ready 或 active。"))
    return issues


def enabled_issues(enabled: Any, status: Any) -> list[str]:
    """The 'only active flows may be enabled' invariant for YAML docs and report snapshots."""
    if type(enabled) is not bool:
        return ["必须是布尔值。"]
    if enabled and status != "active":
        return ["只有 active 流程才可以启用。"]
    return []
