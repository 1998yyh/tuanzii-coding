---
name: e2e-test-gen
description: 根据项目根 `e2e-flows/*.yaml` 和源码生成、补齐或修复可执行的 Playwright E2E 测试，并在单文件实跑通过后将已确认的 `ready` 流程推进为 `active`。用户要求“根据流程生成测试”“补 Playwright 测试”“为 ready 流程写测试”或因纯实现变化需要复核选择器时使用。不要用于抽离或修改业务流程、启动看板、运行已启用流程收集证据、修改业务代码、修改 `playwright.config` 或启用流程。
---

# E2E Test Generation

③将①提供的流程契约翻译为真实测试代码。流程 YAML 描述意图；生成测试前必须回到源码确认页面、选择器、数据和运行方式，不能把 YAML 的 `target.hint` 当作可直接执行的 locator。

## 套件角色与边界

| 编号 | Skill | 职责 |
|---|---|---|
| ① | `e2e-flow-extract` | 抽离/维护业务流程，并将确认后的流程设为 `ready`。 |
| ② | `e2e-flow-center` | 提供完整流程校验器与临时只读看板。 |
| ③ | `e2e-test-gen` | 本 Skill：写、修并实跑 Playwright 测试；仅在通过后推进生命周期。 |
| ④ | `e2e-evidence` | 运行 `active` 流程、收集证据、解释失败，并在获得明确同意后启用流程。 |

- 只写通过完整 Schema 校验的 `test.spec` 指向的 E2E 测试文件、③被授权的 `status: ready → active`，以及成功创建 spec 后同一路径的 `test.source: external → existing`。不要改业务代码、其他流程字段、`review`、`enabled`、`playwright.config`、依赖、锁文件或看板。
- 初次生成只接收已复读验证为 `ready` 的流程。`draft`、`retired`、无效 YAML 和未通过确认的流程一律移交①。
- 已是 `active` 的流程只在用户明确要求补齐或复核测试时维护其 spec；保留现有 `status` 与 `enabled`，不得重复推进生命周期。
- 测试数据只从 YAML 已登记的环境变量或安全数据源读取。不得硬编码账号、密码、token、Cookie、真实邮箱或请求头，也不得把它们输出到日志或报告。

## 开始前

1. 确认目标项目根目录、用户给出的流程 id 或①传入的 `<report-id>`，并检查 `e2e-flows/`、Playwright 配置和现有测试。没有明确范围时不要把所有流程都当作已移交。
2. 阅读本 Skill 携带的 [流程消费契约](references/flow-contract.md)。创建或修改 spec 时再阅读 [Playwright 模式](references/playwright-patterns.md)。
3. 按以下顺序解析移交范围：

   - 用户或调用方明确给出流程 id 时，以这些 id 为准。
   - 调用方给出 `<report-id>` 时，只读取 `e2e-flow-reports/<report-id>.json`：接收 `handoff.e2eTestGen.readyFlowIds` 中的流程，并接收 `flowChanges` 里 `nextAction: review-test-selectors` 的流程作已授权的 `active` 测试维护；绝不接收 `blockedFlows`。
   - 不要自行选择“最新”报告。`approvalMode: source-validated` 的调用既没有明确 id 也没有 `<report-id>` 时，输出机器可读阻塞原因，不等待人工确认也不猜测范围；人工调用才请求澄清。

4. 使用②的完整校验器（可用时）校验流程：

   ```bash
   python3 <e2e-flow-center-skill>/scripts/validate.py --project <target-root>
   ```

   ②不可用时完成轻量自检并明确说明；无效流程不得生成或推进。不要在目标项目中寻找或安装②。
5. 对每条流程重新读取 YAML，核对 `status`、`entry`、`fixtures`、`steps`、`signal`、`sources` 和 `test`。再读取路由、页面、表单/状态逻辑及已有测试，确认真实交互与可观察结果。

## 生成与维护

只有 `test.spec` 位于顶层 `e2e/`、`playwright/` 或 `test(s)/e2e/`、`test(s)/playwright/` 下、为 `*.e2e.*` 或 `*.spec.*` 的 JavaScript/TypeScript 文件，且从项目根到该文件的路径不含符号链接，才可按其项目相对路径写入 spec；完整校验失败时一律阻塞，不能把任意项目文件当测试修改。`test.source: external` 表示可创建该文件；`existing` 表示必须先读取并最小化修改已有文件。③创建 spec 并确认文件存在后，将同一 YAML 的 `test.source` 设为 `existing`；即使后续测试失败，真实存在的 spec 也不再是“待创建”。`external` 但文件已存在时，先读取它并同步为 `existing`。文件不存在、路径越界或项目没有可用的 Playwright 运行环境时，说明阻塞原因，不伪造通过结果。

每条流程遵循以下规则：

- 每个 YAML `steps[].id` 必须对应一个 `test.step`，名称携带该 id；以此供④把截图、Trace 和失败对应回业务步骤。
- 断言必须验证 YAML 的 `expected` / `signal` 所代表的用户可感知结果，而不是只断言 HTTP 状态码、内部 store 或函数调用。
- 优先从源码选择 role、label、test id 或稳定文本；不要用深层 CSS、XPath、`nth-child`、坐标或猜测的 locator。
- 对认证、seed data 和文件上传，只使用项目已有 fixture、storage state 或由 `steps[].data` 引用的 YAML `fixtures.env` 环境变量名。缺少安全测试数据时阻塞并移交①/用户，不要接受 YAML 字面量、创建真实账号或写入秘密值。
- 从源码发现 YAML 的目标、入口、期望结果或 signal 已不真实时，停止修改业务契约并移交①；只修正能证明为纯选择器/实现变化的测试代码。①报告中 `review-test-selectors` 的移交是对这类 `active` 流程维护的明确授权。
- 共享 auth setup、fixture 或 helper 只在它们已存在时复用。需要创建 `test.spec` 外的测试支持文件时，先说明范围并请求明确授权；不要暗中扩大写入面。
- 不要用 `test.skip`、`test.fixme`、空测试、恒真断言、过宽的等待或吞掉异常来制造“通过”。

## 实跑与生命周期

生成或修改后，先确认目标项目清单和本地可执行文件已提供 Playwright，再按既有包管理器和配置实跑该单一 spec（通常为不安装依赖的 `npx playwright test <test.spec>`）。不得让 `npx` 为本次运行下载依赖；运行时缺失时报告阻塞，只有用户明确授权后才可安装。除非用户明确要求只生成不运行，否则测试生成包含这次单文件验证。

1. 先报告并处理可由③解决的选择器或测试同步问题，再重跑；不要改业务代码来迁就测试。
2. 失败、跳过、无法启动、缺少环境变量、不能收集所需数据或用户要求不运行时，保留原流程状态。对 `ready` 流程不得标记 `active`。
3. 单文件全绿后，重新读取 YAML。只有它仍为 `ready` 且本次运行确实执行了该流程的测试，才将其写为 `status: active`；保留 `enabled: false` 和原有 `review`。
4. 写入后重新读取并验证。目标流程自身的写入、复读、`status` / `review` 校验，或②完整校验中归属该流程的错误失败时，恢复到最后一个有效的 `ready` 快照并报告阻塞；回退失败时如实报告当前落盘状态。若完整校验仅报告无关流程错误，不伪造“项目全绿”，也不盲目回退已验证的目标流程。
5. 维护既有 `active` 流程时不改 `status` / `enabled`；实跑失败则报告失败并移交④解释证据或①修订业务契约。

测试通过并变为 `active` 不等于允许运行：只有④在证据校验通过且用户明确同意时，才可设置 `enabled: true`。

## 汇报与移交

每次结束说明：目标流程、spec 路径、实际执行的步骤 id、运行命令与结果、是否推进为 `active`、未解决的 signal/数据/环境阻塞项。不要把测试输出中的秘密值复制到对话或项目文件。

- 没有合格的 `ready` 流程或发现业务契约问题：移交① `e2e-flow-extract`。
- 用户要看流程/报告或临时看板：移交② `e2e-flow-center`。
- `active` 流程需要常规运行、截图/视频/Trace、失败解释或启用：移交④ `e2e-evidence`。
