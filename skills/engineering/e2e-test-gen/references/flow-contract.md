# ③消费的流程契约

本文件是③可独立分发时所需的最小 Schema 摘要。规范来源仍是①的 `flow-schema.md`；修改流程版本或这些字段的规则时，同步更新两处。

## 可接收状态

- 初次测试生成只接收 `status: ready`，且 `review` 必须是 `manual/user-confirmed` 或 `source-validated/source-evidence-and-schema-validation`。
- 单文件实跑通过后，③才可写 `status: active`；保留 `review`。
- `draft`、`retired`、无效流程不接收。已 `active` 的流程仅在用户明确指名，或①报告的 `nextAction: review-test-selectors` 明确移交时维护 spec，且不改变状态。

## 执行字段

- `entry.url` 与 `entry.requiresAuth`：从哪里启动和认证前置。
- `fixtures`：只能是 `env`（安全别名到环境变量名）和 `sources`（声明式安全来源类型）；不含真实凭据。`steps[].data` 只能引用存在的 `fixtures.env.<别名>`，不得含字面量数据。
- `steps[]`：每项有 `id`、业务 `title`、`action`、`expected`、`signal`；每个 id 映射一个 `test.step`。
- `signal.kind` 为 `visible`、`text` 或 `url`；从源码确认 role、label、testId、文本或稳定路由。
- `sources` 是必须存在的项目相对证据文件；`paths` 供影响分析，不是 selector。

## 测试落点

- `test.spec` 是项目相对 E2E spec 路径：必须位于顶层 `e2e/`、`playwright/` 或 `test(s)/e2e/`、`test(s)/playwright/` 下，文件名必须为 `*.e2e.*` 或 `*.spec.*` 的 JavaScript/TypeScript 文件，并且从项目根到该文件不含符号链接。完整校验不通过时③不得写入。
- `test.source: external` 表示①登记、待③创建；创建并确认 spec 存在后，③只可把它改为 `existing`。
- `test.source: existing` 表示 spec 必须存在且先读后改。③不得改 `test.spec`、业务语义或 `review`。

## 报告移交

调用方传入 `<report-id>` 时读取项目根 `e2e-flow-reports/<report-id>.json`。只消费 `handoff.e2eTestGen.readyFlowIds` 与 `nextAction: review-test-selectors`；先重新读取当前 YAML 和完整校验结果，再执行。不要选择“最新”报告，也不要接收 `blockedFlows`。
