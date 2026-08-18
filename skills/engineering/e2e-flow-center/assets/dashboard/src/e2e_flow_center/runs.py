"""Read-only loaders for e2e-evidence run manifests and their evidence files.

Manifests live at results/<run-id>.json; attachments live under
results/<run-id>/evidence/<flow-id>/. Directory contents are the source of
truth for evidence; manifest artifact paths only fill gaps (e.g. htmlReport
lives outside the evidence directory).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from .common import is_relative_path, is_text


RUN_LIMIT = 50
RUN_STATUSES = {"passed", "failed", "blocked", "cancelled"}
ARTIFACT_KEYS = {"screenshot", "video", "trace", "htmlReport", "log"}
EVIDENCE_TYPES = {
    ".png": "screenshot",
    ".jpg": "screenshot",
    ".jpeg": "screenshot",
    ".gif": "screenshot",
    ".webp": "screenshot",
    ".webm": "video",
    ".mp4": "video",
    ".zip": "trace",
    ".log": "log",
    ".txt": "log",
    ".html": "report",
    ".htm": "report",
}
SUMMARY_KEYS = {
    "screenshot": "screenshots",
    "video": "videos",
    "trace": "traces",
    "report": "reports",
    "log": "logs",
}


def resolve_under_results(project_root: Path, rel_path: Any) -> Path | None:
    """Resolve a project-relative evidence path; reject anything escaping results/."""
    if not is_relative_path(rel_path):
        return None
    base = (project_root / "results").resolve()
    candidate = (project_root / rel_path).resolve()
    # resolve() follows symlinks, so a symlinked escape lands outside base and fails here.
    if candidate == base or base not in candidate.parents:
        return None
    return candidate


def _evidence_entry(project_root: Path, rel_path: str) -> dict[str, Any] | None:
    resolved = resolve_under_results(project_root, rel_path)
    if resolved is None or not resolved.is_file():
        return None
    try:
        size = resolved.stat().st_size
    except OSError:
        return None
    return {
        "type": EVIDENCE_TYPES.get(resolved.suffix.lower(), "attachment"),
        "name": resolved.name,
        "path": Path(rel_path).as_posix(),
        "size": size,
    }


def _evidence_dir(project_root: Path, run_id: Any, flow_id: Any) -> Path | None:
    """Both ids must be plain project-relative segments; absolute or '..' ids would
    replace/escape the results/ prefix when joined (e.g. flowId '/'), and NUL bytes
    would blow up is_dir()/rglob() later."""
    if not (is_relative_path(run_id) and is_relative_path(flow_id)):
        return None
    if "\x00" in run_id or "\x00" in flow_id:
        return None
    return project_root / "results" / run_id / "evidence" / flow_id


def _scan_evidence_dir(project_root: Path, run_id: str, flow_id: str) -> list[dict[str, Any]]:
    directory = _evidence_dir(project_root, run_id, flow_id)
    entries: list[dict[str, Any]] = []
    if directory is None:
        return entries
    try:
        if not directory.is_dir():
            return entries
        files = sorted(directory.rglob("*"))
    except (OSError, ValueError):
        return entries
    for file in files:
        try:
            if not file.is_file():
                continue
            rel_path = file.relative_to(project_root).as_posix()
        except (OSError, ValueError):
            continue
        entry = _evidence_entry(project_root, rel_path)
        if entry is not None:
            entries.append(entry)
    return entries


def _flow_result(project_root: Path, run_id: str, flow: dict[str, Any]) -> dict[str, Any]:
    flow_id = flow.get("flowId")
    evidence = _scan_evidence_dir(project_root, run_id, flow_id)
    seen = {entry["path"] for entry in evidence}
    warnings: list[str] = []
    artifacts = flow.get("artifacts")
    if isinstance(artifacts, dict):
        for key, value in artifacts.items():
            if key not in ARTIFACT_KEYS or not is_text(value):
                continue
            if value in seen:
                continue
            entry = _evidence_entry(project_root, value)
            if entry is None:
                warnings.append(f"清单声明的 {key} 产物缺失或不可读：{value}")
                continue
            evidence.append(entry)
            seen.add(value)
    result: dict[str, Any] = {
        "flowId": flow_id,
        "spec": flow.get("spec"),
        "status": flow.get("status"),
        "stepIds": [step for step in flow.get("stepIds") or [] if isinstance(step, str)],
        "evidence": evidence,
        "evidenceWarnings": warnings,
    }
    for key in ("error", "output"):
        if is_text(flow.get(key)):
            result[key] = flow[key]
    return result


def _run_view(project_root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    flows = [
        _flow_result(project_root, manifest["id"], flow)
        for flow in manifest.get("flows") or []
        if isinstance(flow, dict)
    ]
    summary = {"total": 0, "screenshots": 0, "videos": 0, "traces": 0, "reports": 0, "logs": 0}
    for flow in flows:
        for entry in flow["evidence"]:
            summary["total"] += 1
            key = SUMMARY_KEYS.get(entry["type"])
            if key:
                summary[key] += 1
    status = manifest.get("status")
    return {
        "id": manifest["id"],
        "createdAt": manifest.get("createdAt"),
        "status": status if status in RUN_STATUSES else "unknown",
        "command": manifest.get("command") if is_text(manifest.get("command")) else None,
        "flows": flows,
        "evidenceSummary": summary,
    }


def load_runs(project_root: Path, limit: int = RUN_LIMIT) -> dict[str, Any]:
    """Load run manifests newest-first; unparseable or malformed files are skipped."""
    results_dir = project_root / "results"
    manifests: list[dict[str, Any]] = []
    if results_dir.is_dir():
        try:
            files = sorted(results_dir.glob("run-*.json"))
        except OSError:
            files = []
        for file in files:
            try:
                data = json.loads(file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(data, dict) and is_text(data.get("id")):
                manifests.append(data)
    manifests.sort(key=lambda item: str(item.get("createdAt") or ""), reverse=True)
    total = len(manifests)
    return {
        "runs": [_run_view(project_root, manifest) for manifest in manifests[:limit]],
        "total": total,
        "limit": limit,
    }
