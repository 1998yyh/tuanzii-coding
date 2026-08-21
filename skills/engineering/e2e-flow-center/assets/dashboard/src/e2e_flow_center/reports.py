from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import re
from typing import Any

from .common import LIFECYCLE_STATUSES, is_relative_path, is_text, review_issues


REPORT_ID_RE = re.compile(r"^extract-\d{8}T\d{6}Z-[a-z0-9]{6,12}$")
SCENARIOS = {
    "first-extraction",
    "inventory",
    "added-flow",
    "changed-flow",
    "goal-retired",
    "implementation-change",
    "unable-to-determine",
}
OPERATIONS = {"created", "semantic-updated", "provenance-updated", "retired", "unchanged"}
NEXT_ACTIONS = {"await-user-confirmation", "handoff-to-e2e-test-gen", "review-test-selectors", "no-action", "blocked"}
BLOCKED_REASONS = {"awaiting-user-confirmation", "missing-source-evidence", "uncertain-business-semantics", "full-schema-validation-unavailable", "schema-validation-failed", "write-verification-failed"}


@dataclass
class ReportRecord:
    filename: str
    document: dict[str, Any] | None = None
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return self.document is not None and not self.errors

    def listing(self) -> dict[str, Any]:
        if not self.valid:
            return {"filename": self.filename, "valid": False, "errors": self.errors}
        assert self.document is not None
        return {
            "filename": self.filename,
            "valid": True,
            "id": self.document["id"],
            "createdAt": self.document["createdAt"],
            "scenarios": self.document["scenarios"],
            "approvalMode": self.document["approvalMode"],
            "validation": self.document["validation"],
            "summary": self.document["summary"],
        }


def _is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _is_utc_timestamp(value: Any) -> bool:
    if not is_text(value) or not value.endswith("Z"):
        return False
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() == timezone.utc.utcoffset(parsed)


def _lifecycle_errors(snapshot: Any, prefix: str) -> list[str]:
    if not isinstance(snapshot, dict):
        return [f"{prefix} 必须是对象。"]
    errors: list[str] = []
    status = snapshot.get("status")
    if status not in LIFECYCLE_STATUSES:
        errors.append(f"{prefix}.status 不合法。")
    for field_name, message in review_issues(snapshot.get("review"), status):
        errors.append(f"{prefix}.{field_name} {message}")
    return errors


def _after_status(change: Any) -> Any:
    """Dig out lifecycle.after.status without assuming any intermediate shape."""
    if not isinstance(change, dict):
        return None
    lifecycle = change.get("lifecycle")
    if not isinstance(lifecycle, dict):
        return None
    after = lifecycle.get("after")
    if not isinstance(after, dict):
        return None
    return after.get("status")


def _errors(document: Any, filename: str) -> list[str]:
    if not isinstance(document, dict):
        return ["JSON 顶层必须是对象。"]
    required = {"schemaVersion", "id", "createdAt", "scenarios", "approvalMode", "validation", "summary", "flowChanges", "coverage", "uncertainties", "handoff"}
    errors: list[str] = []
    missing = required - document.keys()
    if missing:
        errors.append("缺少字段：" + "、".join(sorted(missing)))
    if document.get("schemaVersion") != 1:
        errors.append("schemaVersion 必须为 1。")
    report_id = document.get("id")
    if not isinstance(report_id, str) or not REPORT_ID_RE.fullmatch(report_id):
        errors.append("id 格式不合法。")
    elif filename != f"{report_id}.json":
        errors.append("文件名必须与报告 id 一致。")
    if not _is_utc_timestamp(document.get("createdAt")):
        errors.append("createdAt 必须是 UTC ISO-8601 时间。")
    scenarios = document.get("scenarios")
    if not isinstance(scenarios, list) or not scenarios or len(scenarios) != len(set(scenarios)) or not set(scenarios) <= SCENARIOS:
        errors.append("scenarios 必须是非空、去重的七类分流枚举数组。")
    if document.get("approvalMode") not in {"manual", "source-validated"}:
        errors.append("approvalMode 不合法。")
    validation = document.get("validation")
    if not isinstance(validation, dict) or validation.get("level") not in {"full", "light", "unavailable"} or validation.get("status") not in {"passed", "failed", "not-run"} or not isinstance(validation.get("errors"), list) or not all(is_text(item) for item in validation.get("errors", [])):
        errors.append("validation 不合法。")
    summary = document.get("summary")
    if not isinstance(summary, dict) or not all(type(value) is int and value >= 0 for value in summary.values()):
        errors.append("summary 必须只包含非负整数。")
    changes = document.get("flowChanges")
    if not isinstance(changes, list):
        return errors + ["flowChanges 必须是数组。"]
    ids: set[str] = set()
    operations: list[str] = []
    ready_ids: set[str] = set()
    actions_by_id: dict[str, str] = {}
    after_statuses_by_id: dict[str, str] = {}
    for index, change in enumerate(changes):
        prefix = f"flowChanges[{index}]"
        if not isinstance(change, dict):
            errors.append(f"{prefix} 必须是对象。")
            continue
        flow_id = change.get("flowId")
        if not isinstance(flow_id, str) or not flow_id or flow_id in ids:
            errors.append(f"{prefix}.flowId 必须唯一。")
        else:
            ids.add(flow_id)
        if change.get("operation") not in OPERATIONS:
            errors.append(f"{prefix}.operation 不合法。")
        else:
            operations.append(change["operation"])
        if flow_id and change.get("flowPath") != f"e2e-flows/{flow_id}.yaml":
            errors.append(f"{prefix}.flowPath 必须与 flowId 对应。")
        lifecycle = change.get("lifecycle")
        operation = change.get("operation")
        if not isinstance(lifecycle, dict) or "after" not in lifecycle:
            errors.append(f"{prefix}.lifecycle.after 缺失。")
        else:
            before = lifecycle.get("before")
            if operation == "created":
                if before is not None:
                    errors.append(f"{prefix}.lifecycle.before 对 created 必须为 null。")
            else:
                errors.extend(_lifecycle_errors(before, f"{prefix}.lifecycle.before"))
            after = lifecycle["after"]
            errors.extend(_lifecycle_errors(after, f"{prefix}.lifecycle.after"))
            if isinstance(after, dict) and isinstance(flow_id, str):
                after_status = after.get("status")
                if isinstance(after_status, str):
                    after_statuses_by_id[flow_id] = after_status
                if after_status == "ready":
                    ready_ids.add(flow_id)
        flow = change.get("flow")
        required_flow_fields = ("name", "persona", "goal", "entryUrl", "successSignal")
        if not isinstance(flow, dict) or any(not is_text(flow.get(field)) for field in required_flow_fields):
            errors.append(f"{prefix}.flow 缺少必填业务概览字段。")
        evidence = change.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{prefix}.evidence 必须至少有一项。")
        else:
            for evidence_index, item in enumerate(evidence):
                evidence_prefix = f"{prefix}.evidence[{evidence_index}]"
                if not isinstance(item, dict) or not is_relative_path(item.get("path")) or not is_text(item.get("reason")):
                    errors.append(f"{evidence_prefix} 必须含项目相对路径和脱敏理由。")
                    continue
                line_start, line_end = item.get("lineStart"), item.get("lineEnd")
                if line_start is not None and not _is_positive_int(line_start):
                    errors.append(f"{evidence_prefix}.lineStart 必须为正整数。")
                if line_end is not None and (not _is_positive_int(line_end) or line_start is None or not _is_positive_int(line_start) or line_end < line_start):
                    errors.append(f"{evidence_prefix}.lineEnd 必须是不小于 lineStart 的正整数。")
        if change.get("nextAction") not in NEXT_ACTIONS:
            errors.append(f"{prefix}.nextAction 不合法。")
        elif isinstance(flow_id, str):
            actions_by_id[flow_id] = change["nextAction"]
    if isinstance(summary, dict):
        after_statuses = [status for status in (_after_status(change) for change in changes) if status is not None]
        expected = {
            "createdFlowCount": operations.count("created"),
            "semanticUpdatedFlowCount": operations.count("semantic-updated"),
            "provenanceUpdatedFlowCount": operations.count("provenance-updated"),
            "unchangedFlowCount": operations.count("unchanged"),
            "readyFlowCount": len(ready_ids),
            "draftFlowCount": after_statuses.count("draft"),
        }
        for key, value in expected.items():
            if summary.get(key) != value:
                errors.append(f"summary.{key} 与 flowChanges 不一致。")
        # retiredFlowCount 是后加字段:旧报告缺省视为 0,保持向后兼容。
        if summary.get("retiredFlowCount", 0) != operations.count("retired"):
            errors.append("summary.retiredFlowCount 与 flowChanges 不一致。")
    if document.get("approvalMode") == "source-validated" and ready_ids and (
        not isinstance(validation, dict) or validation.get("level") != "full" or validation.get("status") != "passed"
    ):
        errors.append("source-validated 且存在 ready 流程时必须完成 full 且 passed 的校验。")
    handoff = document.get("handoff")
    test_gen = handoff.get("e2eTestGen") if isinstance(handoff, dict) else None
    if not isinstance(test_gen, dict) or not isinstance(test_gen.get("readyFlowIds"), list) or not isinstance(test_gen.get("blockedFlows"), list):
        errors.append("handoff.e2eTestGen 不合法。")
    else:
        ready_flow_ids = test_gen["readyFlowIds"]
        if not all(isinstance(flow_id, str) for flow_id in ready_flow_ids) or len(ready_flow_ids) != len(set(ready_flow_ids)):
            errors.append("readyFlowIds 必须是去重的流程 id 数组。")
        handed_off = set(ready_flow_ids) if all(isinstance(flow_id, str) for flow_id in ready_flow_ids) else set()
        if not handed_off <= ready_ids:
            errors.append("readyFlowIds 只能包含状态为 ready 的流程。")
        if any(actions_by_id.get(flow_id) != "handoff-to-e2e-test-gen" for flow_id in handed_off):
            errors.append("readyFlowIds 中的流程必须标记 handoff-to-e2e-test-gen。")
        if any(flow_id not in handed_off for flow_id, action in actions_by_id.items() if action == "handoff-to-e2e-test-gen"):
            errors.append("标记 handoff-to-e2e-test-gen 的流程必须位于 readyFlowIds。")
        if any(after_statuses_by_id.get(flow_id) != "active" for flow_id, action in actions_by_id.items() if action == "review-test-selectors"):
            errors.append("review-test-selectors 仅能移交 active 流程的测试维护。")
        if isinstance(summary, dict) and summary.get("blockedFlowCount") != len(test_gen["blockedFlows"]):
            errors.append("summary.blockedFlowCount 与 blockedFlows 不一致。")
        blocked_ids: set[str] = set()
        for index, blocked in enumerate(test_gen["blockedFlows"]):
            if not isinstance(blocked, dict) or not isinstance(blocked.get("flowId"), str) or blocked.get("flowId") not in ids or blocked.get("reason") not in BLOCKED_REASONS:
                errors.append(f"handoff.e2eTestGen.blockedFlows[{index}] 不合法。")
            else:
                blocked_ids.add(blocked["flowId"])
        if handed_off & blocked_ids:
            errors.append("同一流程不能同时位于 readyFlowIds 和 blockedFlows。")
    coverage = document.get("coverage")
    if not isinstance(coverage, dict) or not isinstance(coverage.get("covered"), list) or not isinstance(coverage.get("uncovered"), list):
        errors.append("coverage 必须含 covered 与 uncovered 数组。")
    else:
        for index, item in enumerate(coverage["covered"]):
            flow_ids = item.get("flowIds") if isinstance(item, dict) else None
            if not isinstance(item, dict) or not is_text(item.get("area")) or not is_text(item.get("reason")) or not isinstance(flow_ids, list) or not all(isinstance(flow_id, str) for flow_id in flow_ids) or not set(flow_ids) <= ids:
                errors.append(f"coverage.covered[{index}] 必须引用 flowChanges 中的流程。")
        for index, item in enumerate(coverage["uncovered"]):
            if not isinstance(item, dict) or not is_text(item.get("area")) or not is_text(item.get("reason")) or not isinstance(item.get("evidencePaths", []), list) or any(not is_relative_path(path) for path in item.get("evidencePaths", [])):
                errors.append(f"coverage.uncovered[{index}] 只能包含脱敏说明和项目相对证据路径。")
    uncertainties = document.get("uncertainties")
    if not isinstance(uncertainties, list):
        errors.append("uncertainties 必须是数组。")
    else:
        for index, item in enumerate(uncertainties):
            evidence_paths = item.get("evidencePaths") if isinstance(item, dict) else None
            blocked_ids = item.get("blocksFlowIds") if isinstance(item, dict) else None
            valid = (
                isinstance(item, dict)
                and item.get("severity") in {"info", "warning", "blocking"}
                and is_text(item.get("summary"))
                and is_text(item.get("question"))
                and isinstance(evidence_paths, list)
                and all(is_relative_path(path) for path in evidence_paths)
                and isinstance(blocked_ids, list)
                and all(isinstance(flow_id, str) for flow_id in blocked_ids)
                and set(blocked_ids) <= ids
            )
            if not valid:
                errors.append(f"uncertainties[{index}] 不合法或含非项目相对路径。")
        if "unable-to-determine" in scenarios and not uncertainties:
            errors.append("unable-to-determine 场景必须记录至少一项 uncertainty。")
    return errors


def load_reports(project_root: Path) -> list[ReportRecord]:
    report_dir = project_root / "e2e-flow-reports"
    if not report_dir.is_dir():
        return []
    records: list[ReportRecord] = []
    for file_path in report_dir.glob("*.json"):
        try:
            document = json.loads(file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            records.append(ReportRecord(file_path.name, None, [f"无法解析 JSON：{error}"]))
            continue
        records.append(ReportRecord(file_path.name, document, _errors(document, file_path.name)))
    return sorted(records, key=lambda record: record.document.get("createdAt", "") if record.document else "", reverse=True)


def report_by_id(project_root: Path, report_id: str) -> ReportRecord | None:
    if not REPORT_ID_RE.fullmatch(report_id):
        return None
    file_path = project_root / "e2e-flow-reports" / f"{report_id}.json"
    if not file_path.is_file():
        return None
    try:
        document = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return ReportRecord(file_path.name, None, [f"无法解析 JSON：{error}"])
    return ReportRecord(file_path.name, document, _errors(document, file_path.name))
