from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest
from copy import deepcopy


SKILL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_ROOT / "assets" / "dashboard" / "src"))
from e2e_flow_center.reports import load_reports
from e2e_flow_center.validation import load_flows


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


class ContractTests(unittest.TestCase):
    def project(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        (root / "src/auth").mkdir(parents=True)
        (root / "src/auth/login.ts").write_text("export {};\n", encoding="utf-8")
        (root / "e2e-flows").mkdir()
        return temp, root

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

    def test_report_uses_five_way_scenario_contract(self) -> None:
        temp, root = self.report_root()
        with temp:
            example = self.example_report()
            self.write_report(root, example)
            records = load_reports(root)
            self.assertTrue(records[0].valid, records[0].errors)
            example["scenarios"] = ["mixed"]
            self.write_report(root, example)
            self.assertFalse(load_reports(root)[0].valid)

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


if __name__ == "__main__":
    unittest.main()
