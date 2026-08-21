from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath
import re
from typing import Any

import yaml

from .affected import flow_impact, git_changed_paths
from .common import LIFECYCLE_STATUSES, is_relative_path, is_text, review_issues


FLOW_ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
ENV_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
FIXTURE_KEY_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
E2E_SPEC_RE = re.compile(r"^.+\.(?:e2e|spec)\.(?:[cm]?[jt]sx?)$")
FLOW_SCHEMA_VERSION = 2
PRIORITIES = {"P0", "P1", "P2", "P3"}
ACTIONS = {"navigate", "fill", "click", "select", "upload", "wait", "assert"}
SIGNAL_KINDS = {"visible", "text", "url"}
TARGET_ACTIONS = {"navigate", "fill", "click", "select", "upload"}
FIXTURE_SOURCE_KINDS = {
    "existing-project-fixture",
    "external-safe-data-source",
    "not-required",
}


@dataclass
class Issue:
    field: str
    message: str


@dataclass
class FlowRecord:
    path: str
    document: dict[str, Any] | None = None
    issues: list[Issue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not self.issues

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "valid": self.valid,
            # 非 dict 的 YAML（列表/标量）也是合法的"无效文件"，必须展示错误而不是炸掉载荷
            "flow": flow_view(self.document) if isinstance(self.document, dict) else None,
            "issues": [asdict(issue) for issue in self.issues],
        }


def _issue(issues: list[Issue], field_name: str, message: str) -> None:
    issues.append(Issue(field_name, message))


# test.step 名称必须以 kebab-case 步骤 id 开头（如 'open-login：打开登录页'），
# 与③《Playwright 模式》的步骤映射约定一致，供本校验器机械核对 spec ↔ YAML 步骤
SPEC_STEP_ID_RE = re.compile(r"test\.step\(\s*['\"]([a-z][a-z0-9]*(?:-[a-z0-9]+)*)")


def _spec_step_ids(spec_path: Path) -> set[str]:
    """抽取 spec 中 test.step('<id>…') 名称开头的步骤 id；读不到按空集处理。"""
    try:
        text = spec_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    return set(SPEC_STEP_ID_RE.findall(text))


def _contains_symlink(project_root: Path, path: Path) -> bool:
    """Reject every link in a writable path, including the final spec file."""
    try:
        relative = path.relative_to(project_root)
    except ValueError:
        return True
    current = project_root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            return True
    return False


def _safe_e2e_test_spec_path(project_root: Path, value: Any) -> bool:
    """Only permit clearly named E2E specs, never arbitrary project files."""
    if not is_relative_path(value):
        return False
    path = PurePosixPath(value)
    directories = path.parts[:-1]
    top_level = directories[0] if directories else ""
    in_safe_e2e_root = top_level in {"e2e", "playwright"} or (
        top_level in {"test", "tests"} and any(part in {"e2e", "playwright"} for part in directories)
    )
    return (
        E2E_SPEC_RE.fullmatch(path.name) is not None
        and in_safe_e2e_root
        and not _contains_symlink(project_root, project_root / path)
    )


def _validate_fixtures(document: dict[str, Any], issues: list[Issue]) -> dict[str, str]:
    """Validate a declarative fixture registry with no place for literal secrets."""
    fixtures = document.get("fixtures")
    if fixtures is None:
        return {}
    if not isinstance(fixtures, dict):
        _issue(issues, "fixtures", "若提供，必须是声明环境变量和安全数据来源的对象。")
        return {}
    unknown = set(fixtures) - {"env", "sources"}
    if unknown:
        _issue(issues, "fixtures", "只允许 env 和 sources；不要写入凭据或其他字面量数据。")

    env = fixtures.get("env", {})
    valid_env: dict[str, str] = {}
    if env is not None:
        if not isinstance(env, dict):
            _issue(issues, "fixtures.env", "必须是“安全名称 → 环境变量名”的对象。")
        else:
            for key, value in env.items():
                if not isinstance(key, str) or not FIXTURE_KEY_RE.fullmatch(key):
                    _issue(issues, f"fixtures.env.{key}", "名称必须是小写 kebab-case。")
                elif not isinstance(value, str) or not ENV_NAME_RE.fullmatch(value):
                    _issue(issues, f"fixtures.env.{key}", "值必须是环境变量名，不能是秘密值。")
                else:
                    valid_env[key] = value

    sources = fixtures.get("sources", {})
    if sources is not None:
        if not isinstance(sources, dict):
            _issue(issues, "fixtures.sources", "必须是“安全名称 → 声明式来源类型”的对象。")
        else:
            for key, value in sources.items():
                if not isinstance(key, str) or not FIXTURE_KEY_RE.fullmatch(key):
                    _issue(issues, f"fixtures.sources.{key}", "名称必须是小写 kebab-case。")
                if value not in FIXTURE_SOURCE_KINDS:
                    _issue(
                        issues,
                        f"fixtures.sources.{key}",
                        "必须是 existing-project-fixture、external-safe-data-source 或 not-required。",
                    )
    return valid_env


def _validate_step_data(value: Any, env: dict[str, str], issues: list[Issue], prefix: str) -> None:
    """Accept only references to declared environment-variable aliases."""
    if isinstance(value, str):
        parts = value.split(".")
        if len(parts) != 3 or parts[:2] != ["fixtures", "env"] or parts[2] not in env:
            _issue(issues, prefix, "只能引用已声明的 fixtures.env.<名称>，不能包含字面量数据。")
        return
    if isinstance(value, list):
        if not value:
            _issue(issues, prefix, "数据引用数组不能为空。")
        for index, item in enumerate(value):
            _validate_step_data(item, env, issues, f"{prefix}[{index}]")
        return
    if isinstance(value, dict):
        if not value:
            _issue(issues, prefix, "数据引用对象不能为空。")
        for key, item in value.items():
            _validate_step_data(item, env, issues, f"{prefix}.{key}")
        return
    _issue(issues, prefix, "只能是 fixtures.env 引用或由这类引用组成的对象/数组。")


def _validate_review(document: dict[str, Any], issues: list[Issue]) -> None:
    for field_name, message in review_issues(document.get("review"), document.get("status")):
        _issue(issues, field_name, message)


def _validate_steps(steps: Any, env: dict[str, str], issues: list[Issue]) -> None:
    if not isinstance(steps, list) or not steps:
        _issue(issues, "steps", "必须是至少含一个步骤的数组。")
        return
    step_ids: set[str] = set()
    for index, step in enumerate(steps):
        prefix = f"steps[{index}]"
        if not isinstance(step, dict):
            _issue(issues, prefix, "必须是对象。")
            continue
        step_id = step.get("id")
        if not is_text(step_id) or not FLOW_ID_RE.fullmatch(step_id):
            _issue(issues, f"{prefix}.id", "必须是小写 kebab-case。")
        elif step_id in step_ids:
            _issue(issues, f"{prefix}.id", "在同一流程中重复。")
        else:
            step_ids.add(step_id)
        for key in ("title", "expected"):
            if not is_text(step.get(key)):
                _issue(issues, f"{prefix}.{key}", "必须是非空业务文本。")
        action = step.get("action")
        if action not in ACTIONS:
            _issue(issues, f"{prefix}.action", "不是受支持的业务动作。")
        if action in TARGET_ACTIONS:
            target = step.get("target")
            if not isinstance(target, dict) or not is_text(target.get("hint")):
                _issue(issues, f"{prefix}.target.hint", "此动作必须有面向人的定位说明。")
        if "data" in step:
            _validate_step_data(step["data"], env, issues, f"{prefix}.data")
        signal = step.get("signal")
        if not isinstance(signal, dict) or signal.get("kind") not in SIGNAL_KINDS:
            _issue(issues, f"{prefix}.signal", "必须含 visible、text 或 url 类型的可观察信号。")
            continue
        if signal["kind"] == "url":
            if not is_text(signal.get("value")):
                _issue(issues, f"{prefix}.signal.value", "url 信号必须有稳定路由或 URL。")
        else:
            locator = signal.get("locator")
            valid_locator = isinstance(locator, dict) and any(
                is_text(locator.get(key)) for key in ("role", "label", "testId", "text")
            )
            if not valid_locator:
                _issue(issues, f"{prefix}.signal.locator", "必须有 role、label、testId 或 text 线索。")


def validate_document(document: Any, project_root: Path, path: str) -> list[Issue]:
    issues: list[Issue] = []
    if not isinstance(document, dict):
        return [Issue("document", "YAML 顶层必须是对象。")]
    required_text = ("id", "name", "description", "category", "persona", "goal")
    if document.get("schemaVersion") != FLOW_SCHEMA_VERSION:
        _issue(issues, "schemaVersion", f"当前必须为整数 {FLOW_SCHEMA_VERSION}。")
    flow_id = document.get("id")
    if not is_text(flow_id) or not FLOW_ID_RE.fullmatch(flow_id):
        _issue(issues, "id", "必须是小写 kebab-case。")
    elif path != f"e2e-flows/{flow_id}.yaml":
        _issue(issues, "id", "文件名必须与 id 一致，且使用 .yaml 后缀。")
    for key in required_text:
        if not is_text(document.get(key)):
            _issue(issues, key, "必须是非空文本。")
    if document.get("priority") not in PRIORITIES:
        _issue(issues, "priority", "必须为 P0、P1、P2 或 P3。")
    if document.get("status") not in LIFECYCLE_STATUSES:
        _issue(issues, "status", "必须为 draft、ready、active 或 retired。")
    _validate_review(document, issues)

    entry = document.get("entry")
    if not isinstance(entry, dict):
        _issue(issues, "entry", "必须是对象。")
    else:
        if not is_text(entry.get("url")):
            _issue(issues, "entry.url", "必须是非空入口路由或 URL。")
        if type(entry.get("requiresAuth")) is not bool:
            _issue(issues, "entry.requiresAuth", "必须是布尔值。")
    fixture_env = _validate_fixtures(document, issues)
    _validate_steps(document.get("steps"), fixture_env, issues)

    paths = document.get("paths")
    if not isinstance(paths, list) or not paths:
        _issue(issues, "paths", "必须是至少含一个项目相对 glob 的数组。")
    else:
        for index, value in enumerate(paths):
            if not is_relative_path(value) or value == "**":
                _issue(issues, f"paths[{index}]", "必须是有边界的项目相对 glob。")
    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        _issue(issues, "sources", "必须是至少含一个真实来源文件的数组。")
    else:
        for index, value in enumerate(sources):
            if not is_relative_path(value):
                _issue(issues, f"sources[{index}]", "必须是项目相对文件路径。")
            elif not (project_root / value).is_file():
                _issue(issues, f"sources[{index}]", "来源文件在项目中不存在。")
    test = document.get("test")
    if not isinstance(test, dict) or test.get("source") not in {"external", "existing"}:
        _issue(issues, "test.source", "必须为 external 或 existing。")
    elif not _safe_e2e_test_spec_path(project_root, test.get("spec")):
        _issue(
            issues,
            "test.spec",
            "必须位于顶层 e2e/playwright 或 test(s)/e2e/playwright 下、文件名为 *.e2e.* 或 *.spec.*，且路径中不能有符号链接。",
        )
    elif test["source"] == "existing" and not (project_root / test["spec"]).is_file():
        _issue(issues, "test.spec", "标为 existing 的测试文件必须存在。")
    elif test["source"] == "existing":
        # spec 存在时机械核对：YAML 步骤 id 必须以名称前缀形式出现在 test.step 中
        spec_step_ids = _spec_step_ids(project_root / test["spec"])
        steps = document.get("steps")
        if isinstance(steps, list):
            for index, step in enumerate(steps):
                step_id = step.get("id") if isinstance(step, dict) else None
                if isinstance(step_id, str) and FLOW_ID_RE.fullmatch(step_id) and step_id not in spec_step_ids:
                    _issue(
                        issues,
                        f"steps[{index}].id",
                        f"spec 中缺少以 {step_id} 开头的 test.step（步骤 id 必须出现在 test.step 名称开头）。",
                    )
    if "alwaysRunOnAffected" not in document or type(document.get("alwaysRunOnAffected")) is not bool:
        _issue(issues, "alwaysRunOnAffected", "必须是布尔值。")
    if "tags" in document and (not isinstance(document["tags"], list) or not all(is_text(tag) for tag in document["tags"])):
        _issue(issues, "tags", "若提供，必须是文本数组。")
    return issues


def load_flows(project_root: Path) -> list[FlowRecord]:
    flow_dir = project_root / "e2e-flows"
    if not flow_dir.is_dir():
        return []
    records: list[FlowRecord] = []
    for file_path in sorted(flow_dir.glob("*.yaml")):
        relative = file_path.relative_to(project_root).as_posix()
        try:
            document = yaml.safe_load(file_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as error:
            records.append(FlowRecord(relative, None, [Issue("document", f"无法解析 YAML：{error}")]))
            continue
        records.append(FlowRecord(relative, document, validate_document(document, project_root, relative)))
    return records


def _step_view(step: Any) -> dict[str, Any] | None:
    """Business-facing step summary; data, targets and locators never leave the server."""
    if not isinstance(step, dict):
        return None
    return {"id": step.get("id"), "title": step.get("title"), "expected": step.get("expected")}


def flow_view(document: dict[str, Any]) -> dict[str, Any]:
    """Expose a dashboard-safe summary; fixtures and step data never leave the server."""
    fields = ("id", "name", "description", "category", "persona", "goal", "priority", "status", "entry", "paths", "sources", "test", "tags")
    view = {key: document.get(key) for key in fields}
    view["steps"] = [
        step_view
        for step in document.get("steps") or []
        if (step_view := _step_view(step)) is not None
    ]
    return view


def flow_counts(records: list[FlowRecord]) -> tuple[int, int]:
    """(valid, invalid) counts shared by the payload and the health endpoint."""
    valid = sum(record.valid for record in records)
    return valid, len(records) - valid


def validation_payload(project_root: Path) -> dict[str, Any]:
    records = load_flows(project_root)
    valid, invalid = flow_counts(records)
    changed_paths, git_available = git_changed_paths(project_root)
    flows: list[dict[str, Any]] = []
    for record in records:
        view = record.to_dict()
        if isinstance(record.document, dict):
            affected, reasons = flow_impact(record.document, changed_paths)
            view["affected"] = affected
            view["reasons"] = reasons
        flows.append(view)
    return {
        "project": str(project_root),
        "flowDirectoryExists": (project_root / "e2e-flows").is_dir(),
        "validFlowCount": valid,
        "invalidFlowCount": invalid,
        "flows": flows,
        "changedPaths": changed_paths,
        "gitAvailable": git_available,
    }
