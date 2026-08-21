---
name: e2e-flow-extract
description: 从源码、路由、已有测试和产品文档中抽离或维护端到端业务流程。用户要求“梳理核心业务流程”“有哪些端到端场景”“把流程抽成 YAML”，或说明新项目从未建流程、旧项目新增功能、已有流程的业务行为发生变化时使用。将流程写入项目根 e2e-flows/，只产出或更新业务流程定义；不要用于生成 Playwright 测试、启动临时看板、运行测试或排查失败。
---

# E2E Flow Extract

将代码中的用户旅程整理为供后续测试和看板使用的流程 YAML。流程描述的是用户想完成什么、在哪里开始、如何观察成功，而不是点击坐标或 CSS 选择器脚本。

## 套件角色

本 Skill 中的①②③④始终指以下四个独立 Skill。使用编号移交前，先按本表解析；不要假设单独加载本 Skill 的模型已经知道这些代号。

| 编号 | Skill | 职责 |
|---|---|---|
| ① | `e2e-flow-extract` | 本 Skill：抽离与维护流程的业务定义。 |
| ② | `e2e-flow-center` | 启动临时看板，并提供完整 Schema 校验器。 |
| ③ | `e2e-test-gen` | 生成并实跑 Playwright 测试。 |
| ④ | `e2e-evidence` | 运行流程、收集并解释测试证据。 |

先完整阅读 [流程 Schema](references/flow-schema.md)、[完整流程样例](assets/example-flow.yaml) 和 [抽离报告契约](references/extraction-report-schema.md)。创建或语义更新流程时，以完整样例为字段基线，再替换为当前项目中有证据支撑的值；不要凭记忆从零拼 YAML。每次抽离还要写一份可由②页面展示的报告 JSON；报告字段以 `assets/example-extraction-report.json` 为基线。需要区分「新目标 / 语义变化 / 纯实现变化」，或决定一条候选该不该建模时，再阅读 [抽离方法](references/extraction-guide.md)。这些文件共同约束本 Skill 的输出。

## 边界

- 流程的唯一规范来源是目标项目根目录的 `e2e-flows/*.yaml`。不要创建 `flows/` 副本，也不要把 YAML 复制到看板目录。
- 每次抽离的审计快照写入项目根 `e2e-flow-reports/<report-id>.json`。报告不是第二份流程定义，不能被用来反向覆盖 `e2e-flows/`。
- 只处理流程的业务定义及其允许的生命周期字段。不要写 Playwright spec、修改业务代码、修改 `playwright.config`、安装或启动看板。
- 默认以人工确认模式运行：所有新流程以 `status: draft` 创建。用户确认业务语义后，才把指定流程标为 `ready`。
- 凭据、token、Cookie、真实邮箱、个人信息和请求头不得写入 YAML、报告或示例。只记录环境变量名和脱敏的数据来源说明。
- 不能从源码证明的内容必须标记为存疑；不要用想象补齐接口、选择器、跳转或用户权限。

## 验收模式

流程是否可推进到 `ready` 由本次调用的 `approvalMode` 决定。没有明确声明时一律使用 `manual`；不要把“这是 CI”“用户未回复”或“任务紧急”推断为自动验收授权。

| `approvalMode` | 适用场景 | `draft → ready` 的前置条件 |
|---|---|---|
| `manual`（默认） | 人工协作、探索性抽离 | 用户明确确认流程的 persona、goal、entry 和成功结果。 |
| `source-validated` | 已授权的 CI / 自动化开发管线 | 本次调用明确传入 `approvalMode: source-validated`；每个关键业务字段和 signal 均有源码证据；不存在存疑项；并且 Schema 校验通过。 |

自动化调用必须显式包含 `approvalMode: source-validated`，例如：`以 approvalMode: source-validated 抽离当前分支的受影响流程，并将可验证条目交给测试生成。` 这是管线授予的验收权限，不是缺少人工回复时的默认行为。

无论模式如何，①都不设置 `active`。自动验收必须在流程 YAML 中写入 `review.mode: source-validated` 和 `review.basis: source-evidence-and-schema-validation`，使后续步骤能分辨它不是人工确认。

## 开始前的分流

先确定目标项目根目录，并检查 `e2e-flows/` 是否存在、是否包含有效流程，以及用户的请求属于哪一类。不要只根据目录是否存在猜测项目历史。

| 场景 | 识别方式 | 本 Skill 的动作 |
|---|---|---|
| 首次抽离 | 没有 `e2e-flows/`，或目录为空且用户确认尚未建立流程 | 从零建立覆盖图；人工模式创建少量高价值 `draft`，自动模式只将证据充分且校验通过的条目设为 `ready` |
| 已有流程盘点 | 已有有效 YAML，用户只要求梳理/盘点，未提供新功能或变更主张 | 读取全部 YAML 与最小必要源码；只报告覆盖、漂移和存疑，默认不改流程或生命周期 |
| 旧项目新增流程 | 已有 YAML，新增的是一个独立的角色 + 可感知目标 | 保留旧流程；只为新目标创建新的 `draft` YAML |
| 原流程有改动 | 已有 YAML 的 persona、goal、entry、关键步骤或可观察结果发生业务变化 | 更新同一份 YAML，重新设为 `draft` |
| 业务目标下线 | 源码能证实入口和完成目标已被移除，或用户明确说明该目标已下线 | 保留 YAML 作为历史契约，设为 `status: retired`，不删除文件也不移交③ |
| 纯实现变化 | 路径语义未变，只是组件、文案、选择器或实现重构 | 不改变流程语义或生命周期；更新 `sources` / `paths`（若需要）并移交③复核测试 |
| 无法判断 | 缺少变更基线、源码证据或产品规则 | 不修改现有流程；报告存疑项并向用户询问 |

`retired` 流程默认保持停用。只有用户明确要求恢复该业务目标时，才根据当前源码重新评审：先回到 `draft`、`review.mode: manual` / `review.basis: pending-user-confirmation`；只有显式 `source-validated` 调用满足全部自动验收门槛时，才可直接重回 `ready`。不得用“源码又出现了相似页面”自行恢复。

## 取证和建模

1. 阅读最小必要范围：README、路由和导航、页面或视图、服务端控制器/接口定义、权限/状态逻辑、已有 E2E 测试。优先用快速文本搜索定位入口，再阅读相关文件，而不是扫描整个仓库。
2. 列出候选旅程：`谁（persona）→ 想完成什么（goal）→ 从哪里开始（entry）→ 做哪些业务动作 → 看见什么结果（expected/signal）`。
3. 用“一角色 + 一可感知目标”合并候选项。例如“管理员创建成员后成员出现在列表中”是一条流程；不要按控制器、API 或文件分别创建多条。
4. 对每条候选回到源码确认：路由/入口、数据或认证前置条件、能作为断言线索的可观察信号、影响路径和来源文件。
5. 只保留可被源码支撑的核心流程。宁可交付 3–5 条有证据的流程，也不要罗列所有按钮。

## 三类项目工作流

### 1. 新项目：从未抽离流程

1. 创建项目根 `e2e-flows/`；不要创建看板、测试或占位流程。
2. 建立覆盖图：入口页面、主要 persona、关键目标、已覆盖区域、无法确认区域。
3. 按风险和用户价值排序，先抽身份认证、关键交易/提交、核心查询或管理目标等流程；没有证据的功能不纳入。
4. 为每条流程写 `e2e-flows/<flow-id>.yaml`：人工模式均为 `draft`；自动模式仅将通过“验收模式”全部门槛的条目写为 `ready`，其余保留 `draft`。
5. 写入抽离报告 JSON，明确这是首次基线、共创建多少条、哪些区域未覆盖，以及每条流程是待人工确认还是已由源码验收。

### 2. 旧项目：新增流程

1. 先读取全部现有 YAML，建立 `id → persona/goal/entry/sources/paths` 索引，避免按新文件名误判为新流程。
2. 查看用户指定的功能、当前工作区变更和相关路由/页面。若有明确 Git 基线，使用它辅助定位；没有基线时，仅将其作为当前源码分析，不声称知道历史差异。
3. 判断新增功能是否带来了新的可感知目标或新的角色路径。仅新增 API、字段、组件或按钮不足以创建新流程。
4. 若确为独立目标，创建一个新的 YAML：人工模式为 `draft`；自动模式仅在所有自动验收门槛通过时设为 `ready`。不要更改无关已有流程的 status。
5. 若它只是扩展已有目标，按“原流程有改动”处理；若只是实现细节，保持流程语义不变并报告给③。

### 3. 旧项目：原流程有改动

1. 以已有 YAML 中的 `sources`、`paths`、`entry`、`steps` 和 `signal` 为检查清单，读取对应源码和相关变更。
2. 将变化归类并在报告中给出证据：

   - **业务语义变化**：角色、权限前置、用户目标、入口、关键业务动作、成功条件或影响范围发生变化。
   - **纯实现变化**：组件迁移、选择器/文案变化、内部 API 重构，且用户目标与成功条件未变。
   - **不确定**：源码无法证明当前行为，或产品要求在代码外。

3. 对业务语义变化，原地更新同一份 `<flow-id>.yaml`，先重置为 `status: draft`；自动模式也不例外。随后只有自动验收门槛通过时，才能在同一次有序操作中推进为 `ready`，否则保持 `draft`。保留稳定的 `id`，除非它已无法表达流程；若需要拆分或合并流程，先在报告中说明并请求用户确认，避免悄悄丢失溯源。
4. 对纯实现变化，不降级 `status`。仅在来源或影响范围已过期时更新 `sources` / `paths`，并在报告中列出“需③复核测试”的流程。
5. 对不确定变化，不修改流程定义或生命周期；把具体问题、已检查文件和所需产品确认写进报告。

## 写入流程 YAML

写入前逐项对照 `references/flow-schema.md` 的轻量自检。特别检查：

- `id` 是小写 kebab-case，文件名与 id 一致；新流程不与现有 id 重复。
- `sources` 和 `paths` 均为项目根相对路径；每个 `sources` 文件真实存在且被本次分析使用。
- 每个步骤都有用户可理解的标题和可观察的 `expected`；每个 `signal` 在源码中有依据。
- `fixtures` 只能使用 Schema 的 `env` / `sources` 受限结构；`steps[].data` 只能引用已登记的 `fixtures.env.<别名>`，不放入任何真实值。
- `test.spec` 必须是 Schema 允许的 E2E spec 路径；路径不合规时不要创建或改写任何文件。
- 人工模式下新建或业务语义更新的流程都是 `draft`；自动模式下只有通过全部证据与 Schema 门槛的条目可成为 `ready`。
- 仅实现层变化时，不伪造语义更新，不创建重复流程，也不改变 `status`。

完整校验器属于② `e2e-flow-center` Skill，不属于目标项目。②可用时，从它的 Skill 目录调用：

```bash
python3 <e2e-flow-center-skill>/scripts/validate.py --project <target-root>
```

不要在目标项目中查找或安装②。②不可用时只做上述轻量自检，并在报告中写入 `validation.level: unavailable`；`approvalMode: source-validated` 下必须保持 `draft`，不得自动验收或移交③。

## 确认、自动验收与状态推进

抽离完成后不要自动把流程标为 `ready`。向用户逐条展示 persona、goal、入口和成功结果，并请求确认。只有用户明确确认的条目可由本 Skill 从 `draft` 改为 `ready`。不要把任何流程标为 `active`。

### 确认后交给③的硬协议

用户可能把确认和后续意图合在一句话中，例如“这几条对，去写测试”。按以下顺序处理，不能跳步：

1. 解析用户明确确认的流程 id；确认范围不清楚时，先请求澄清，不要推测全部 `draft` 都已确认。
2. 重新读取这些 YAML。对仍为 `draft` 的已确认流程，在同一次写入中设为 `status: ready`，并写入：

   ```yaml
   review:
     mode: manual
     basis: user-confirmed
   ```

   已是 `ready` 的流程不重复改写；先验证其 `review` 合法后继续。`active`、`retired` 或状态/确认范围不一致的流程不得借此协议推进。
3. 重新读取并验证写入结果；②可用时运行完整校验。新推进的流程若写入、复读或该流程自身的校验失败，回退为 `draft`、`review.mode: manual` 与 `review.basis: pending-user-confirmation`；回退也失败时如实报告当前落盘状态。
4. 依照“写入可视化报告”创建并原子写入报告后，只有已验证为 `ready` 且列入该报告 `handoff.e2eTestGen.readyFlowIds` 的流程，才可移交③。移交时传递明确的 `<report-id>`；③不得自行猜测“最新”报告。
5. 任何仍为 `draft`、写入失败、Schema 校验失败、未获确认或未进入 `readyFlowIds` 的流程都不得移交③；在报告中说明阻塞原因。

当用户只说“去写测试”而没有确认当前 `draft` 的业务语义时，不改变状态，直接说明③的前置条件未满足，并请用户先确认流程或由①继续修订。

### 自动验收后交给③的硬协议

仅在 `approvalMode: source-validated` 已被显式声明时使用本协议：

1. 对每条候选重新核验 entry、关键步骤、expected/signal、sources 和 paths；任何未证实或有歧义的业务字段都标为存疑。
2. 运行完整 Schema 校验器；若②不可用，完成轻量自检并在报告中标记“未完整校验”，此时流程必须保持 `draft`，不得自动验收。
3. 只有没有存疑项且完整校验通过的流程，才写入 `status: ready`，并写入：

   ```yaml
   review:
     mode: source-validated
     basis: source-evidence-and-schema-validation
   ```

4. 重新读取并验证该 YAML。只有已持久化为 `ready` 且 review 溯源正确的流程，才可列入本次报告的 `handoff.e2eTestGen.readyFlowIds`。
5. 任一证据、校验或写入步骤失败时，保留或回退为 `draft`，并且不得移交③。报告原子写入后，向③传递该明确的 `<report-id>`；③只消费该报告中的 `readyFlowIds`。

自动模式不会要求人工确认，但必须在报告中列出自动验收的流程、使用的证据和被保留为 `draft` 的原因。

## 写入可视化报告

流程 YAML 写入和状态验证结束后，先构建一份报告 JSON，再由这份 JSON 生成对话中的 Markdown 摘要。不要只输出对话文本；②的临时看板只能读取持久化报告。

1. 以 `assets/example-extraction-report.json` 和 `references/extraction-report-schema.md` 为字段基线，创建一个 `schemaVersion: 1` 的报告。
2. 生成不会冲突的报告 id：`extract-<UTC时间戳>-<随机短后缀>`，例如 `extract-20260813T074531Z-a1b2c3`；写入 `e2e-flow-reports/<report-id>.json`。不要维护或覆盖 `latest.json`。
3. 使用临时文件写入后原子替换为最终文件，避免②读到半截 JSON。报告 JSON 一经写入不可修改；后续抽离创建新快照。
4. `scenarios` 必须逐项记录本次实际命中的分流类别，与「开始前的分流」一一对应：`first-extraction`（首次抽离）、`inventory`（已有流程盘点）、`added-flow`（旧项目新增流程）、`changed-flow`（原流程有改动）、`goal-retired`（业务目标下线）、`implementation-change`（纯实现变化）、`unable-to-determine`（无法判断）。一次调用命中多类时使用去重数组，不使用笼统的 `mixed`；无法判断的候选必须同时写入 `uncertainties`，且不得移交③。
5. 每一条流程变更都记录 operation、变更前后生命周期、业务概览、源码证据和下一步动作；同时记录覆盖区域、未覆盖区域、存疑项、校验结果及③的移交清单。
6. 报告只能保存项目相对路径和脱敏说明，不能保存源码全文、真实凭据、token、Cookie、完整用户输入或绝对机器路径。
7. 如果本次没有创建或更新流程，仍写一份报告，使用空 `flowChanges` 和明确的 `uncovered` / `uncertainties` 原因。这能让页面说明“为什么没有结果”。
8. 报告的 `handoff.e2eTestGen` 是①→③的机器接口。需要自动或跨 Skill 移交时，调用方必须传递这个不可变报告的 id；③只读取 `e2e-flow-reports/<report-id>.json`，不自动选择最新文件。

当用户要求“用页面看抽离报告”“打开流程抽离报告”或类似表达时，先确保本次 JSON 已成功写入，然后移交② `e2e-flow-center`。①不启动 Web 服务；②以临时 localhost 看板读取 `e2e-flow-reports/` 并显示报告。

## 对话摘要格式

每次结束都使用以下结构。它是报告 JSON 的面向人的摘要，字段和值必须与 JSON 一致，不能再独立编造一份结论：

```markdown
# E2E 流程抽离报告

项目：<project-root>
场景：<scenarios 中实际命中的类别，以逗号分隔>
验收模式：manual | source-validated
报告：`e2e-flow-reports/<report-id>.json`

## 结果

| 流程 | 操作 | 状态 | 证据 |
|---|---|---|---|
| <id> | 创建 / 语义更新 / 仅更新溯源 / 下线 / 未修改 | <status, review.basis> | <关键 sources> |

## 流程概览

- `<id>`：<persona> 要 <goal>；从 <entry> 开始；成功信号是 <signal>。

## 需用户确认

- <manual 模式下每个 draft 的业务语义问题；自动模式下写“自动验收，无人工确认步骤”，或列出需人工处理的存疑项>

## 未覆盖与存疑

- <区域、原因、已检查证据、需要的确认>

## 移交

- <需要③生成或复核测试的流程；没有则写“当前不移交”>
```

当 `approvalMode: source-validated` 时，在摘要末尾额外输出报告 JSON 中 `handoff.e2eTestGen` 的等价 YAML 块。只把已复读验证为 `ready` 的流程放进 `readyFlowIds`；所有其他候选必须带原因列在 `blockedFlows`。

```yaml
handoff:
  e2eTestGen:
    readyFlowIds:
      - <flow-id>
    blockedFlows:
      - flowId: <flow-id>
        reason: <awaiting-user-confirmation | missing-source-evidence | uncertain-business-semantics | full-schema-validation-unavailable | schema-validation-failed | write-verification-failed>
```

`readyFlowIds` 为空是有效结果，代表本次不应调用③。不要为了让自动化管线继续而把 `draft` 放进 `readyFlowIds`。

## 移交规则

- 用户已确认业务语义并希望生成或补齐 Playwright 测试：先按“确认后交给③的硬协议”把已确认流程持久化为 `ready`，原子写入包含 `readyFlowIds` 的报告后，携带该 `report-id` 移交 `e2e-test-gen`。
- 用户希望查看影响范围、流程目录、临时 Web 看板或抽离报告页面：先确认 `e2e-flow-reports/<report-id>.json` 已原子写入，再移交 `e2e-flow-center`。
- 用户要求运行、重跑、收集截图/Trace 或解释失败：移交 `e2e-evidence`。
