---
name: e2e-evidence
description: 运行已激活的 Playwright E2E 流程，配置或核验截图、视频、Trace、HTML 报告与日志证据，写入项目根 `results/` 并基于证据解释失败。用户要求“跑一下流程”“重跑失败”“收集截图/Trace/视频”“为什么 E2E 失败”或明确要求启用已验证流程时使用。不要用于抽离/修改业务流程、生成或修复测试代码、启动流程看板、修改业务源码；缺少测试时移交 e2e-test-gen。
---

# E2E Evidence

④负责可复核的运行结果，而不是制造绿灯。先用现有测试与证据回答“发生了什么”，再决定是否需要①修订业务契约或③修复测试。

## 套件角色与边界

| 编号 | Skill | 职责 |
|---|---|---|
| ① | `e2e-flow-extract` | 定义和维护流程 YAML 的业务语义。 |
| ② | `e2e-flow-center` | 提供完整校验和临时只读看板。 |
| ③ | `e2e-test-gen` | 生成/修复测试，并把通过实跑的 `ready` 流程推进为 `active`。 |
| ④ | `e2e-evidence` | 本 Skill：运行、保存证据、解释失败；获授权后启用已验证流程。 |

- 默认只运行 `status: active` 且 `enabled: true` 的流程。`draft`、`ready` 或缺少 spec 的流程不运行，移交③或①。
- 对 `active + enabled: false`，仅当用户明确要求一次性验证或启用该具体流程时才直接运行；不要先把它设为 `enabled: true`。
- 除 `enabled` 外不得修改 YAML。只有流程仍为 `active`、证据校验通过且用户明确同意启用时，才可写入 `enabled: true`；保留 `status`、`review` 和所有业务字段。
- 不写或修复正式测试代码，不改业务代码、依赖、锁文件或看板。用户明确要求“配置/修复 E2E 证据”时，才可最小化修改项目的 `playwright.config.*`。
- 证据、结果 JSON、命令摘要和对话中都不得包含凭据、token、Cookie、完整请求头、真实邮箱、绝对机器路径或源码全文。

## 开始前

1. 确认目标项目根、用户要运行的流程和一次性验证/启用意图。范围不清楚时不要运行“全部”。
2. 读取 [流程 Schema](../e2e-flow-extract/references/flow-schema.md)，并在需要配置、收集或解释证据时读取 [Playwright 证据规则](references/playwright-evidence.md)。
3. 检查 `e2e-flows/`、对应 `test.spec`、已有 `results/`、Playwright 配置和项目运行命令。②可用时先运行完整校验器；无效 YAML 不得作为可运行流程。
4. 按状态筛选：常规运行仅选 `active + enabled: true`；一次性验证可选用户点名的 `active + enabled: false`；其他状态说明阻塞并移交。
5. 纯“运行”请求不得顺手改配置。只有用户要求配置/修复证据，或在当前证据缺失时明确授权变更后，才进入配置步骤。

## 配置并核验证据

保持目标项目既有的配置风格和 reporter。配置或修复证据时，只补齐足以在失败后保存截图、视频、Trace、HTML 报告和日志的最小设置；不要覆盖用户已有的 `use`、`reporter`、projects、webServer 或输出目录。详情见 [Playwright 证据规则](references/playwright-evidence.md)。

需要验证新配置时，可以创建一条**精确定位、故意失败的临时测试**，运行后检查五类证据可读取，再立即删除该临时文件。仅在用户授权配置/修复证据时使用这一步；不修改任何正式 spec，不留下临时测试，也不把故意失败计入正式流程结果。

## 运行、归档与解释

1. 为本次运行生成不可冲突的 `run-<UTC时间戳>-<随机短后缀>`，在项目根写入 [结果清单](references/playwright-evidence.md#结果清单)，并让产物归入 `results/<run-id>/evidence/<flow-id>/`。不要维护 `latest.json` 或覆盖历史运行。
2. 用项目既有命令执行精确选中的 spec / test；记录脱敏后的命令、flow id、spec、开始结束时间、退出结果和相对证据路径。不要把环境变量值拼进命令或清单。
3. 利用 `test.step` 中的 flow step id，将截图、视频、Trace、HTML 报告和日志关联到失败步骤。若产物缺失，只报告缺失，不假装已验证。
4. 基于证据区分：产品行为与 YAML 契约不符 → ①；选择器/spec/fixture 问题 → ③；环境、服务、网络或测试数据问题 → 说明可复现条件和证据，不编造根因。
5. 运行失败时不改变 `status` 或 `enabled`，不删除失败证据，也不放宽测试。运行通过也不自动启用流程。

## 启用流程

用户明确说“启用 `<flow-id>`”并且该流程已完成一次可复核的成功运行时，按以下顺序处理：

1. 重新读取 YAML，确认仍是 `active`；确认本次或指定的成功结果清单完整且对应该 flow id。
2. 写入 `enabled: true`，不修改任何其他字段。
3. 重新读取并运行②完整校验器（可用时）；验证失败则回退为 `enabled: false` 并报告原因。
4. 在结果清单和对话摘要中记录用户授权、依据 run id 和最终状态。

用户只说“跑一下”或“看看结果”不是启用授权；即使通过也保持 `enabled: false`。

## 汇报与移交

每次结束报告：运行 id、选中的流程、执行结果、每类证据的相对路径、失败步骤与证据支持的判断、配置改动（若有）、以及 `enabled` 是否变化。

- 流程语义、入口、步骤或信号不正确：移交① `e2e-flow-extract`。
- spec、locator、fixture 或 Playwright 测试实现需要修复：移交③ `e2e-test-gen`。
- 用户要查看看板、流程目录或抽离报告：移交② `e2e-flow-center`。
