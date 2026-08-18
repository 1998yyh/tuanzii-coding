from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from copy import deepcopy


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "assets" / "dashboard" / "src"))
from e2e_flow_center.affected import flow_impact, git_changed_paths
from e2e_flow_center.reports import load_reports
from e2e_flow_center.runs import load_runs, resolve_under_results
from e2e_flow_center.validation import flow_view, load_flows, validation_payload


VALID_FLOW = """\
schemaVersion: 2
id: user-login
name: 用户登录
description: 已注册用户登录后进入工作台。
category: 身份认证
persona: 已注册用户
goal: 登录后看到工作台。
priority: P0
status: ready
enabled: false
review:
  mode: manual
  basis: user-confirmed
entry:
  url: /login
  requiresAuth: false
steps:
  - id: open-login
    title: 打开登录页
    action: navigate
    target: {hint: 登录路由, value: /login}
    expected: 显示登录表单。
    signal: {kind: visible, locator: {role: button, name: 登录}}
paths: [src/auth/**]
test: {source: external, spec: tests/e2e/user-login.spec.js}
sources: [src/auth/login.ts]
alwaysRunOnAffected: true
"""


def flow_project() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    """Scaffold a minimal project with e2e-flows/ and the source file VALID_FLOW references."""
    temp = tempfile.TemporaryDirectory()
    root = Path(temp.name)
    (root / "src/auth").mkdir(parents=True)
    (root / "src/auth/login.ts").write_text("export {};\n", encoding="utf-8")
    (root / "e2e-flows").mkdir()
    return temp, root


class ContractTests(unittest.TestCase):
    def project(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        return flow_project()

    def example_report(self) -> dict:
        return json.loads((SKILL_ROOT.parent / "e2e-flow-extract/assets/example-extraction-report.json").read_text(encoding="utf-8"))

    def report_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "e2e-flow-reports").mkdir()
        return temp, root

    def write_report(self, root: Path, report: dict) -> None:
        (root / "e2e-flow-reports" / f"{report['id']}.json").write_text(json.dumps(report), encoding="utf-8")

    def test_valid_flow_passes_complete_validation(self) -> None:
        temp, root = self.project()
        with temp:
            (root / "e2e-flows/user-login.yaml").write_text(VALID_FLOW, encoding="utf-8")
            records = load_flows(root)
            self.assertEqual(1, len(records))
            self.assertTrue(records[0].valid, records[0].issues)

    def test_rejects_business_file_as_test_spec(self) -> None:
        temp, root = self.project()
        with temp:
            invalid = VALID_FLOW.replace("tests/e2e/user-login.spec.js", "src/e2e/App.spec.ts")
            (root / "e2e-flows/user-login.yaml").write_text(invalid, encoding="utf-8")
            records = load_flows(root)
            self.assertFalse(records[0].valid)
            self.assertTrue(any(issue.field == "test.spec" for issue in records[0].issues))

    def test_rejects_spec_symlink_to_application_source(self) -> None:
        temp, root = self.project()
        with temp:
            spec = root / "tests/e2e/user-login.spec.js"
            spec.parent.mkdir(parents=True)
            spec.symlink_to("../../src/auth/login.ts")
            invalid = VALID_FLOW.replace("source: external", "source: existing")
            (root / "e2e-flows/user-login.yaml").write_text(invalid, encoding="utf-8")
            records = load_flows(root)
            self.assertFalse(records[0].valid)
            self.assertTrue(any(issue.field == "test.spec" for issue in records[0].issues))

    def test_rejects_literal_fixture_values_and_step_data(self) -> None:
        temp, root = self.project()
        with temp:
            invalid = VALID_FLOW.replace(
                "entry:\n  url: /login\n  requiresAuth: false\n",
                "entry:\n  url: /login\n  requiresAuth: false\nfixtures:\n  password: literal-value\n",
            ).replace(
                "    expected: 显示登录表单。",
                "    data: literal-value\n    expected: 显示登录表单。",
            )
            (root / "e2e-flows/user-login.yaml").write_text(invalid, encoding="utf-8")
            records = load_flows(root)
            self.assertFalse(records[0].valid)
            fields = {issue.field for issue in records[0].issues}
            self.assertIn("fixtures", fields)
            self.assertIn("steps[0].data", fields)

    def test_accepts_declared_environment_variable_references(self) -> None:
        temp, root = self.project()
        with temp:
            valid = VALID_FLOW.replace(
                "entry:\n  url: /login\n  requiresAuth: false\n",
                "entry:\n  url: /login\n  requiresAuth: false\nfixtures:\n  env:\n    username: E2E_USER\n  sources:\n    seed-data: existing-project-fixture\n",
            ).replace(
                "    expected: 显示登录表单。",
                "    data: fixtures.env.username\n    expected: 显示登录表单。",
            )
            (root / "e2e-flows/user-login.yaml").write_text(valid, encoding="utf-8")
            records = load_flows(root)
            self.assertTrue(records[0].valid, records[0].issues)

    def test_duplicate_step_id_is_invalid(self) -> None:
        temp, root = self.project()
        with temp:
            invalid = VALID_FLOW.replace("    signal: {kind: visible, locator: {role: button, name: 登录}}", "    signal: {kind: visible, locator: {role: button, name: 登录}}\n  - id: open-login\n    title: 重复步骤\n    action: assert\n    expected: 页面仍可见。\n    signal: {kind: visible, locator: {role: button, name: 登录}}")
            (root / "e2e-flows/user-login.yaml").write_text(invalid, encoding="utf-8")
            records = load_flows(root)
            self.assertFalse(records[0].valid)
            self.assertTrue(any(issue.field.endswith(".id") for issue in records[0].issues))

    def test_report_uses_seven_way_scenario_contract(self) -> None:
        temp, root = self.report_root()
        with temp:
            example = self.example_report()
            self.write_report(root, example)
            self.assertTrue(records := load_reports(root), "示例报告应被加载")
            self.assertTrue(records[0].valid, records[0].errors)
            example["scenarios"] = ["mixed"]
            self.write_report(root, example)
            self.assertFalse(load_reports(root)[0].valid)
            for scenario in ("inventory", "goal-retired"):
                example["scenarios"] = [scenario]
                self.write_report(root, example)
                self.assertTrue(load_reports(root)[0].valid, scenario)

    def test_report_retired_operation_contract(self) -> None:
        def retire_report() -> dict:
            report = deepcopy(self.example_report())
            report["scenarios"] = ["goal-retired"]
            change = report["flowChanges"][0]
            change["operation"] = "retired"
            change["lifecycle"] = {
                "before": {
                    "status": "ready",
                    "enabled": False,
                    "review": {"mode": "manual", "basis": "user-confirmed"},
                },
                "after": {"status": "retired", "enabled": False},
            }
            change["nextAction"] = "no-action"
            report["summary"].update(createdFlowCount=0, retiredFlowCount=1, readyFlowCount=0, draftFlowCount=0, blockedFlowCount=0)
            report["handoff"]["e2eTestGen"] = {"readyFlowIds": [], "blockedFlows": []}
            return report

        temp, root = self.report_root()
        with temp:
            self.write_report(root, retire_report())
            self.assertTrue(records := load_reports(root), "retire 报告应被加载")
            self.assertTrue(records[0].valid, records[0].errors)

            wrong_count = retire_report()
            wrong_count["summary"]["retiredFlowCount"] = 2
            self.write_report(root, wrong_count)
            self.assertFalse(load_reports(root)[0].valid)

    def test_legacy_report_without_retired_count_stays_valid(self) -> None:
        temp, root = self.report_root()
        with temp:
            legacy = deepcopy(self.example_report())
            legacy["summary"].pop("retiredFlowCount")
            self.write_report(root, legacy)
            self.assertTrue(records := load_reports(root), "旧格式报告应被加载")
            self.assertTrue(records[0].valid, records[0].errors)

    def test_report_rejects_parent_path(self) -> None:
        temp, root = self.report_root()
        with temp:
            example = self.example_report()
            example["flowChanges"][0]["evidence"][0]["path"] = "../secret.txt"
            self.write_report(root, example)
            self.assertFalse(load_reports(root)[0].valid)

    def test_report_enforces_cross_field_contracts(self) -> None:
        def handoff_action_mismatch(report: dict) -> None:
            report["flowChanges"][0]["lifecycle"]["after"] = {
                "status": "ready",
                "enabled": False,
                "review": {"mode": "manual", "basis": "user-confirmed"},
            }
            report["flowChanges"][0]["nextAction"] = "no-action"
            report["summary"].update(readyFlowCount=1, draftFlowCount=0, blockedFlowCount=0)
            report["handoff"]["e2eTestGen"] = {"readyFlowIds": ["user-login"], "blockedFlows": []}

        cases = [
            ("created-at", lambda report: report.update(createdAt="not-a-timestamp")),
            ("validation-errors", lambda report: report["validation"].update(errors=[42])),
            ("missing-flow-field", lambda report: report["flowChanges"][0]["flow"].pop("successSignal")),
            ("invalid-evidence", lambda report: report["flowChanges"][0]["evidence"][0].update(reason="", lineEnd=3)),
            ("unknown-covered-flow", lambda report: report["coverage"]["covered"][0].update(flowIds=["unknown-flow"])),
            ("malformed-lifecycle", lambda report: report["flowChanges"][0]["lifecycle"].update(after="ready")),
            ("unhashable-covered-flow", lambda report: report["coverage"]["covered"][0].update(flowIds=[{}])),
            ("malformed-uncertainty", lambda report: report.update(uncertainties=[{"severity": "blocking", "summary": "x", "question": "y", "evidencePaths": [], "blocksFlowIds": [{}]}])),
            ("unhashable-handoff-id", lambda report: report["handoff"]["e2eTestGen"].update(readyFlowIds=[{}])),
            ("handoff-action-mismatch", handoff_action_mismatch),
            ("missing-unable-to-determine-uncertainty", lambda report: report.update(scenarios=["unable-to-determine"])),
        ]
        for name, mutate in cases:
            with self.subTest(name=name):
                temp, root = self.report_root()
                with temp:
                    report = self.example_report()
                    mutate(report)
                    self.write_report(root, report)
                    self.assertFalse(load_reports(root)[0].valid)

    def test_source_validated_ready_report_requires_full_passed_validation(self) -> None:
        temp, root = self.report_root()
        with temp:
            report = deepcopy(self.example_report())
            report["approvalMode"] = "source-validated"
            report["validation"] = {"level": "light", "status": "passed", "errors": []}
            report["summary"].update(readyFlowCount=1, draftFlowCount=0, blockedFlowCount=0)
            change = report["flowChanges"][0]
            change["lifecycle"]["after"] = {
                "status": "ready",
                "enabled": False,
                "review": {
                    "mode": "source-validated",
                    "basis": "source-evidence-and-schema-validation",
                },
            }
            change["nextAction"] = "handoff-to-e2e-test-gen"
            report["handoff"]["e2eTestGen"] = {"readyFlowIds": ["user-login"], "blockedFlows": []}
            self.write_report(root, report)
            self.assertFalse(load_reports(root)[0].valid)

    def test_flow_view_exposes_sanitized_steps_only(self) -> None:
        temp, root = self.project()
        with temp:
            (root / "e2e-flows/user-login.yaml").write_text(VALID_FLOW, encoding="utf-8")
            document = load_flows(root)[0].document
            view = flow_view(document)
            self.assertEqual(1, len(view["steps"]))
            step = view["steps"][0]
            self.assertEqual({"id", "title", "expected"}, set(step))
            self.assertEqual("打开登录页", step["title"])

    def test_payload_survives_non_dict_yaml(self) -> None:
        # 列表/标量顶层的 YAML 是合法的"无效文件"：载荷必须给出错误而不是 500。
        temp, root = self.project()
        with temp:
            (root / "e2e-flows/broken.yaml").write_text("- a\n- b\n", encoding="utf-8")
            (root / "e2e-flows/scalar.yaml").write_text("42\n", encoding="utf-8")
            payload = validation_payload(root)
            self.assertEqual(2, payload["invalidFlowCount"])
            for record in payload["flows"]:
                self.assertFalse(record["valid"])
                self.assertIsNone(record["flow"])
                self.assertNotIn("affected", record)


class RunManifestTests(unittest.TestCase):
    RUN_ID = "run-20260814T090000Z-a1b2c3"

    def project(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "results").mkdir()
        return temp, root

    def write_manifest(self, root: Path, manifest: dict, run_id: str | None = None) -> None:
        (root / "results" / f"{run_id or self.RUN_ID}.json").write_text(json.dumps(manifest), encoding="utf-8")

    def valid_manifest(self) -> dict:
        return {
            "schemaVersion": 1,
            "id": self.RUN_ID,
            "createdAt": "2026-08-14T09:00:00Z",
            "status": "failed",
            "command": "npx playwright test tests/e2e/user-login.spec.ts",
            "flows": [
                {
                    "flowId": "user-login",
                    "spec": "tests/e2e/user-login.spec.ts",
                    "status": "failed",
                    "stepIds": ["open-login"],
                    "error": "expect(locator).toBeVisible() failed",
                    "artifacts": {
                        "htmlReport": f"results/{self.RUN_ID}/html-report/index.html",
                        "log": f"results/{self.RUN_ID}/evidence/user-login/run.log",
                    },
                }
            ],
        }

    def test_load_runs_scans_evidence_and_merges_artifacts(self) -> None:
        temp, root = self.project()
        with temp:
            evidence_dir = root / "results" / self.RUN_ID / "evidence" / "user-login"
            evidence_dir.mkdir(parents=True)
            (evidence_dir / "open-login.png").write_bytes(b"\x89PNG")
            (evidence_dir / "replay.webm").write_bytes(b"webm")
            (evidence_dir / "trace.zip").write_bytes(b"zip")
            (evidence_dir / "run.log").write_text("log\n", encoding="utf-8")
            report_dir = root / "results" / self.RUN_ID / "html-report"
            report_dir.mkdir(parents=True)
            (report_dir / "index.html").write_text("<html></html>\n", encoding="utf-8")
            self.write_manifest(root, self.valid_manifest())

            payload = load_runs(root)
            self.assertEqual(1, payload["total"])
            run = payload["runs"][0]
            self.assertEqual(self.RUN_ID, run["id"])
            self.assertEqual("failed", run["status"])
            flow = run["flows"][0]
            self.assertEqual("user-login", flow["flowId"])
            self.assertEqual("expect(locator).toBeVisible() failed", flow["error"])
            by_type = {}
            for entry in flow["evidence"]:
                by_type.setdefault(entry["type"], []).append(entry)
            self.assertEqual(1, len(by_type["screenshot"]))
            self.assertEqual(1, len(by_type["video"]))
            self.assertEqual(1, len(by_type["trace"]))
            # run.log is both on disk and declared in artifacts; it must not duplicate.
            self.assertEqual(1, len(by_type["log"]))
            self.assertEqual(1, len(by_type["report"]))
            summary = run["evidenceSummary"]
            self.assertEqual(5, summary["total"])
            self.assertEqual(1, summary["screenshots"])
            self.assertEqual(1, summary["traces"])
            self.assertEqual([], flow["evidenceWarnings"])

    def test_load_runs_warns_on_missing_declared_artifact(self) -> None:
        temp, root = self.project()
        with temp:
            manifest = self.valid_manifest()
            manifest["flows"][0]["artifacts"] = {"screenshot": f"results/{self.RUN_ID}/evidence/user-login/gone.png"}
            self.write_manifest(root, manifest)
            flow = load_runs(root)["runs"][0]["flows"][0]
            self.assertEqual([], flow["evidence"])
            self.assertEqual(1, len(flow["evidenceWarnings"]))
            self.assertIn("gone.png", flow["evidenceWarnings"][0])

    def test_load_runs_skips_garbage_and_sorts_newest_first(self) -> None:
        temp, root = self.project()
        with temp:
            (root / "results" / "run-broken.json").write_text("{not json", encoding="utf-8")
            (root / "results" / "run-noid.json").write_text(json.dumps({"createdAt": "2026-08-15T00:00:00Z"}), encoding="utf-8")
            older = self.valid_manifest()
            older["id"] = "run-20260801T000000Z-older"
            older["createdAt"] = "2026-08-01T00:00:00Z"
            self.write_manifest(root, older, run_id=older["id"])
            newer = self.valid_manifest()
            self.write_manifest(root, newer)
            payload = load_runs(root)
            self.assertEqual(2, payload["total"])
            self.assertEqual(self.RUN_ID, payload["runs"][0]["id"])
            self.assertEqual("run-20260801T000000Z-older", payload["runs"][1]["id"])

    def test_evidence_resolution_confines_to_results(self) -> None:
        temp, root = self.project()
        with temp:
            evidence = root / "results" / self.RUN_ID / "evidence" / "user-login"
            evidence.mkdir(parents=True)
            self.assertIsNotNone(resolve_under_results(root, f"results/{self.RUN_ID}/evidence/user-login/run.log"))
            for bad in ("../secret.txt", "results/../../secret.txt", "/etc/passwd", "e2e-flows/user-login.yaml", "results", "results/"):
                self.assertIsNone(resolve_under_results(root, bad), bad)
            # A symlink inside results/ pointing outside must be rejected after resolve().
            outside = root.parent / f"{root.name}-outside.txt"
            outside.write_text("secret\n", encoding="utf-8")
            try:
                (root / "results" / "link.txt").symlink_to(outside)
                self.assertIsNone(resolve_under_results(root, "results/link.txt"))
            finally:
                outside.unlink()

    def test_scan_rejects_hostile_manifest_ids(self) -> None:
        # 绝对路径 / '..' 的 flowId 或 runId 若直接参与 pathlib 拼接会替换 results/ 前缀并扫全盘。
        temp, root = self.project()
        with temp:
            manifest = self.valid_manifest()
            manifest["flows"][0]["flowId"] = "/"
            self.write_manifest(root, manifest)
            flow = load_runs(root)["runs"][0]["flows"][0]
            # 恶意 id 原样透传展示，但绝不参与目录扫描。
            self.assertEqual("/", flow["flowId"])
            self.assertEqual([], flow["evidence"])

            hostile = self.valid_manifest()
            hostile["id"] = "/tmp"
            hostile["flows"][0]["flowId"] = "../../../etc"
            self.write_manifest(root, hostile, run_id="run-20260816T000000Z-hostile")
            run = [item for item in load_runs(root)["runs"] if item["id"] == "/tmp"][0]
            self.assertEqual([], run["flows"][0]["evidence"])


class AffectedTests(unittest.TestCase):
    def project(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        return flow_project()

    def test_glob_matching_and_always_run_reason(self) -> None:
        document = {"paths": ["src/auth/**"], "alwaysRunOnAffected": False}
        affected, reasons = flow_impact(document, ["src/auth/login.ts"])
        self.assertTrue(affected)
        self.assertEqual(["path-match"], reasons)
        affected, _ = flow_impact(document, ["src/other/page.ts"])
        self.assertFalse(affected)
        document["alwaysRunOnAffected"] = True
        affected, reasons = flow_impact(document, ["src/other/page.ts"])
        self.assertTrue(affected)
        self.assertEqual(["always-run"], reasons)
        affected, reasons = flow_impact(document, [])
        self.assertFalse(affected)
        self.assertEqual([], reasons)

    def test_double_star_matches_zero_or_more_levels(self) -> None:
        document = {"paths": ["src/**/login.ts"], "alwaysRunOnAffected": False}
        self.assertTrue(flow_impact(document, ["src/login.ts"])[0])
        self.assertTrue(flow_impact(document, ["src/a/b/login.ts"])[0])
        self.assertFalse(flow_impact(document, ["src/a/b/logout.ts"])[0])

    def test_repeated_double_star_terminates_quickly(self) -> None:
        # 连排 '**/' 曾让旧正则灾难回溯（12 个 '**/' 对深路径挂起超 10 秒）；段式 DP 必须毫秒级。
        import time

        document = {"paths": ["/".join(["**"] * 12 + ["checkout.ts"])], "alwaysRunOnAffected": False}
        deep = "/".join(["node_modules"] + [f"pkg{i}" for i in range(25)] + ["file.tsx"])
        start = time.monotonic()
        affected, reasons = flow_impact(document, [deep, "a/b/c/checkout.ts"])
        elapsed = time.monotonic() - start
        self.assertTrue(affected)
        self.assertEqual(["path-match"], reasons)
        self.assertLess(elapsed, 5.0)

    def test_monorepo_subdirectory_paths_are_project_relative(self) -> None:
        # git diff 输出仓库根相对路径、ls-files 默认 cwd 相对；统一裁剪后只留项目内、项目相对的变更。
        import subprocess

        temp = tempfile.TemporaryDirectory()
        repo = Path(temp.name)
        with temp:
            (repo / "sub" / "src").mkdir(parents=True)
            (repo / "sub" / "src" / "login.ts").write_text("v1\n", encoding="utf-8")
            (repo / "outside.ts").write_text("v1\n", encoding="utf-8")
            for args in (
                ["git", "init", "-q"],
                ["git", "config", "user.email", "test@example.com"],
                ["git", "config", "user.name", "test"],
                ["git", "add", "-A"],
                ["git", "commit", "-qm", "init"],
            ):
                subprocess.run(args, cwd=repo, check=True)
            (repo / "sub" / "src" / "login.ts").write_text("v2\n", encoding="utf-8")  # 已跟踪改动（项目内）
            (repo / "sub" / "src" / "new.ts").write_text("x\n", encoding="utf-8")  # 未跟踪（项目内）
            (repo / "outside2.ts").write_text("x\n", encoding="utf-8")  # 项目外，不得泄漏
            paths, available = git_changed_paths(repo / "sub")
            self.assertTrue(available)
            self.assertEqual(["src/login.ts", "src/new.ts"], paths)

    def test_git_unavailable_outside_repository(self) -> None:
        temp, root = self.project()
        with temp:
            paths, available = git_changed_paths(root)
            self.assertFalse(available)
            self.assertEqual([], paths)

    def test_payload_marks_affected_flows(self) -> None:
        import subprocess

        temp, root = self.project()
        with temp:
            (root / "e2e-flows/user-login.yaml").write_text(VALID_FLOW, encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            # Untracked source file under the flow's paths glob makes it affected.
            (root / "src/auth/login.ts").write_text("export {};\n", encoding="utf-8")
            payload = validation_payload(root)
            self.assertTrue(payload["gitAvailable"])
            self.assertIn("src/auth/login.ts", payload["changedPaths"])
            flow = payload["flows"][0]
            self.assertTrue(flow["affected"])
            self.assertEqual(["always-run", "path-match"], flow["reasons"])


if __name__ == "__main__":
    unittest.main()
