# 抽离报告 JSON 契约

每一次 `e2e-flow-extract` 调用都写入一份不可变的报告快照，供人类、CI 和② `e2e-flow-center` 的“抽离报告”页面共同消费。

报告的唯一目录是目标项目根 `e2e-flow-reports/`，文件名为 `<report-id>.json`。它记录“某次分析做了什么”，不是流程定义；流程的唯一规范来源仍是 `e2e-flows/*.yaml`。

创建报告时先复制 [完整样例](../assets/example-extraction-report.json)，再替换为当前调用的真实、可证明且已脱敏的数据。

## 写入与安全规则

- `schemaVersion` 固定为整数 `1`。
- `id` 必须匹配 `^extract-\d{8}T\d{6}Z-[a-z0-9]{6,12}$`，例如 `extract-20260813T074531Z-a1b2c3`。
- `createdAt` 为 UTC ISO-8601 时间；报告按此字段降序展示，不创建会产生竞争的 `latest.json`。
- 先写入同目录临时文件，完成 JSON 解析后再原子替换为最终文件；已存在的报告不得覆盖或修改。
- 所有 `path`、`flowPath` 和 `evidence.path` 都相对项目根，禁止绝对路径和 `..`。
- 不得写入源文件全文、代码片段、真实用户输入、密码、token、Cookie、完整请求头、真实邮箱或机器绝对路径。证据只记录相对文件路径、可选行号和简短理由。

## 完整结构

```json
{
  "schemaVersion": 1,
  "id": "extract-20260813T074531Z-a1b2c3",
  "createdAt": "2026-08-13T07:45:31Z",
  "scenarios": ["first-extraction"],
  "approvalMode": "manual",
  "validation": {
    "level": "light",
    "status": "passed",
    "errors": []
  },
  "summary": {
    "createdFlowCount": 0,
    "semanticUpdatedFlowCount": 0,
    "provenanceUpdatedFlowCount": 0,
    "unchangedFlowCount": 0,
    "retiredFlowCount": 0,
    "readyFlowCount": 0,
    "draftFlowCount": 0,
    "blockedFlowCount": 0
  },
  "flowChanges": [],
  "coverage": { "covered": [], "uncovered": [] },
  "uncertainties": [],
  "handoff": {
    "e2eTestGen": { "readyFlowIds": [], "blockedFlows": [] }
  }
}
```

所有顶层字段均必填。

### `scenarios`

| 值 | 含义 |
|---|---|
| `first-extraction` | 首次建立流程基线。 |
| `inventory` | 已有流程盘点：只梳理覆盖、漂移和存疑，不改流程或生命周期。 |
| `added-flow` | 在已有项目中确认了独立的新目标。 |
| `changed-flow` | 已有流程的业务语义发生变化。 |
| `goal-retired` | 业务目标下线：流程被设为 `status: retired` 保留为历史契约。 |
| `implementation-change` | 只更新实现溯源或影响范围。 |
| `unable-to-determine` | 缺少变更基线、源码证据或产品规则，不能安全判定或修改流程。 |

`scenarios` 是非空、去重的上述枚举数组，记录本次分析实际涉及的每一种分流结果。一次调用可以同时包含新增流程、原流程改动和纯实现变化，因此不能用 `mixed` 这类笼统值掩盖差异。②页面将每个值分别展示；③据此区分需要重建业务测试的 `changed-flow`、只需复核选择器的 `implementation-change`，以及绝不可移交的 `unable-to-determine`。`inventory` 与 `goal-retired` 同样不移交③：盘点不改流程，下线流程保持停用。

当某个候选因无法判断而未修改流程时，必须包含 `unable-to-determine`，并在 `uncertainties` 中写明证据、问题和阻塞原因。`unable-to-determine` 不得让任何对应候选进入 `handoff.e2eTestGen.readyFlowIds`。

### `validation`

| 字段 | 类型 | 规则 |
|---|---|---|
| `level` | string | `full`、`light` 或 `unavailable`。`source-validated` 报告中只要有 `ready` 流程，自动验收必须为 `full` 且 `status: passed`；所有候选均保持草稿的受阻尝试可以记录 `unavailable` 或 `not-run`。 |
| `status` | string | `passed`、`failed` 或 `not-run`。 |
| `errors` | array[string] | 无错误时为空数组；仅记录脱敏错误摘要。 |

### `summary`

所有计数字段是非负整数，必须与 `flowChanges` 和 `handoff` 可推导出的结果一致。

- `createdFlowCount`：operation 为 `created` 的数量。
- `semanticUpdatedFlowCount`：operation 为 `semantic-updated` 的数量。
- `provenanceUpdatedFlowCount`：operation 为 `provenance-updated` 的数量。
- `unchangedFlowCount`：operation 为 `unchanged` 的数量。
- `retiredFlowCount`：operation 为 `retired` 的数量。该字段为后加：校验时旧报告缺省视为 `0`，新报告必须显式写入。
- `readyFlowCount` 和 `draftFlowCount`：本次受影响流程写入后的状态数量。
- `blockedFlowCount`：`handoff.e2eTestGen.blockedFlows` 的数量。

### `flowChanges`

每项代表本次分析涉及的一条流程。`flowChanges` 可以为空，但报告必须改用 `coverage.uncovered` 或 `uncertainties` 说明原因。`inventory` 盘点调用通常不改流程：`flowChanges` 为空或全部为 `unchanged`，盘点结论写入 `coverage` 与 `uncertainties`。

```json
{
  "flowId": "user-login",
  "flowPath": "e2e-flows/user-login.yaml",
  "operation": "created",
  "lifecycle": {
    "before": null,
    "after": {
      "status": "draft",
      "enabled": false,
      "review": {
        "mode": "manual",
        "basis": "pending-user-confirmation"
      }
    }
  },
  "flow": {
    "name": "用户登录",
    "persona": "已注册用户",
    "goal": "登录后看到工作台，并显示本人昵称。",
    "entryUrl": "/login",
    "successSignal": "工作台页显示当前用户昵称。"
  },
  "evidence": [
    {
      "path": "src/pages/login/LoginForm.tsx",
      "lineStart": 24,
      "lineEnd": 56,
      "reason": "登录表单和提交后的工作台导航。"
    }
  ],
  "nextAction": "await-user-confirmation"
}
```

| 字段 | 类型 | 规则 |
|---|---|---|
| `flowId` | string | 对应 YAML 的 id。 |
| `flowPath` | string | 必须为 `e2e-flows/<flow-id>.yaml`。 |
| `operation` | string | `created`、`semantic-updated`、`provenance-updated`、`retired` 或 `unchanged`。`retired` 表示业务目标下线：`lifecycle.before` 必填，`lifecycle.after` 为 `status: retired`、`enabled: false`。 |
| `lifecycle.before` | object / null | 新流程为 `null`；否则记录分析前的 `status`、`enabled`、`review`。 |
| `lifecycle.after` | object | 记录写入后的 `status`、`enabled`、`review`。 |
| `flow` | object | 面向页面展示的脱敏业务概览：`name`、`persona`、`goal`、`entryUrl`、`successSignal` 均必填。 |
| `evidence` | array | 至少一个项目相对路径和理由；行号可选，提供时为正整数且 `lineEnd ≥ lineStart`。 |
| `nextAction` | string | `await-user-confirmation`、`handoff-to-e2e-test-gen`、`review-test-selectors`、`no-action` 或 `blocked`。 |

`lifecycle.after.status: ready` 只有两种合法来源：`review.mode: manual` + `basis: user-confirmed`，或 `review.mode: source-validated` + `basis: source-evidence-and-schema-validation`。

### `coverage` 与 `uncertainties`

```json
{
  "coverage": {
    "covered": [
      {
        "area": "身份认证",
        "flowIds": ["user-login"],
        "reason": "登录路由、表单和工作台导航均已检查。"
      }
    ],
    "uncovered": [
      {
        "area": "第三方单点登录",
        "reason": "路由指向外部身份提供商，当前仓库无完成后的可观察结果。",
        "evidencePaths": ["src/auth/sso.ts"]
      }
    ]
  },
  "uncertainties": [
    {
      "id": "sso-return-signal",
      "severity": "blocking",
      "summary": "无法从仓库确认第三方登录返回后的成功页面。",
      "evidencePaths": ["src/auth/sso.ts"],
      "question": "请确认登录返回后用户应看到的页面和成功标志。",
      "blocksFlowIds": []
    }
  ]
}
```

- `coverage.covered[].flowIds` 必须引用 `flowChanges` 中的流程 id。
- `coverage.uncovered[].evidencePaths` 和 `uncertainties[].evidencePaths` 均为项目相对路径。
- `severity` 为 `info`、`warning` 或 `blocking`；`blocking` 存疑的流程不能在自动验收中进入 `ready`。
- `blocksFlowIds` 可为空，但不能引用不存在的流程 id。

### `handoff`

```json
{
  "handoff": {
    "e2eTestGen": {
      "readyFlowIds": ["user-login"],
      "blockedFlows": [
        {
          "flowId": "password-reset",
          "reason": "uncertain-business-semantics"
        }
      ]
    }
  }
}
```

- `readyFlowIds` 仅包含已重新读取验证为 `status: ready` 的流程。
- `readyFlowIds` 中的每项必须在对应 `flowChanges` 中标为 `nextAction: handoff-to-e2e-test-gen`；反过来，标为该动作的流程也必须位于该数组。`blockedFlows` 不得与其重叠。
- `nextAction: review-test-selectors` 仅用于报告中仍为 `active` 的纯实现变化测试维护项，不进入 `readyFlowIds`。
- `blockedFlows[].reason` 取值为：`awaiting-user-confirmation`、`missing-source-evidence`、`uncertain-business-semantics`、`full-schema-validation-unavailable`、`schema-validation-failed` 或 `write-verification-failed`。
- `readyFlowIds` 为空是有效结果。②页面必须将其显示为“本次没有可交给测试生成的流程”，而不是错误。
- 当①调用③时，调用方必须传递此不可变报告的 id。③只读取 `e2e-flow-reports/<report-id>.json` 中的 `readyFlowIds`，以及 `flowChanges` 里 `nextAction: review-test-selectors` 的维护项；不得自行选择“最新”报告，也不得接收 `blockedFlows`。

## ②页面消费规则

②读取项目根 `e2e-flow-reports/*.json`，按 `createdAt` 倒序展示。它必须将 JSON parse/schema 失败的文件显示为“报告文件无效”，不能因为一份坏报告阻塞其他报告或尝试修改它。

页面展示的状态、计数、证据和移交项必须从报告 JSON 读取；可额外读取对应的当前 YAML 标记“报告快照与当前状态不一致”，但不得改写报告或 YAML。
