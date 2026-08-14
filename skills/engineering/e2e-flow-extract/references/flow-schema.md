# 流程 YAML Schema

本文件是 `e2e-flows/*.yaml` 的共同契约。它描述业务意图和测试线索，不是可直接执行的测试 DSL。流程的唯一规范来源始终是目标项目根目录的 `e2e-flows/`。

创建或修订文件前，先从 [完整可复制样例](../assets/example-flow.yaml) 开始。该样例包含全部必填字段和常用可选字段；复制后必须把所有示例业务名称、路径、来源和测试落点替换为当前项目中已验证的证据，不能原样带入。

## 套件角色

| 编号 | Skill | 生命周期职责 |
|---|---|---|
| ① | `e2e-flow-extract` | 在人工确认或显式 `source-validated` 自动验收后将流程持久化为 `ready`；业务语义变化时保持 `enabled: false`，并按验收模式重新评审。 |
| ② | `e2e-flow-center` | 提供临时看板和完整 Schema 校验器；只读流程。 |
| ③ | `e2e-test-gen` | 只接收 `ready` 流程；实跑通过后将其设为 `active`，并在创建 spec 后同步测试落点状态。 |
| ④ | `e2e-evidence` | 只在 `active`、证据校验通过且用户同意后设 `enabled: true`。 |

①向③移交是有序操作：①必须先写入并重新读取确认 `status: ready`，然后才能移交。`draft`、`retired`、校验失败、未获人工确认的手动流程，或未达到自动验收门槛的流程都不得交给③。

## 文件与基本规则

- 每个文件只定义一条流程，文件名必须是 `<id>.yaml`。
- 所有路径均相对目标项目根目录；禁止绝对路径和 `..`。
- `schemaVersion` 当前固定为整数 `2`。版本 1 的 `fixtures` 与 `data` 不能被结构化地证明不含秘密值，因此不再通过完整校验；迁移时按下面的 `fixtures` 结构重写。
- 未明确为可选的字段均为必填。
- 所有文本应面向业务读者；不要把接口路径、CSS 类或 Playwright 代码当作业务步骤。

## 顶层字段

| 字段 | 类型 | 规则和用途 |
|---|---|---|
| `schemaVersion` | integer | 固定为 `2`。 |
| `id` | string | 小写 kebab-case：`^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$`。 |
| `name` | string | 面向人的简短流程名称。 |
| `description` | string | 一句话说明流程和价值。 |
| `category` | string | 业务分类，如“身份认证”“订单管理”。 |
| `persona` | string | 执行流程的用户角色，而非技术帐号名。 |
| `goal` | string | 该角色能感知的业务目标及成功结果。 |
| `priority` | string | `P0`、`P1`、`P2` 或 `P3`。 |
| `status` | string | `draft`、`ready`、`active` 或 `retired`。 |
| `enabled` | boolean | 看板/运行器的独立运行开关。 |
| `review` | object | 可选；记录 `ready` 的人工或自动验收来源。自动验收的 `ready` 流程必须提供。 |
| `entry` | object | 流程入口与认证前置条件。 |
| `fixtures` | object | 可选；只能以受限的 `env` / `sources` 结构描述安全输入。 |
| `steps` | array | 至少一个面向业务的步骤。 |
| `paths` | array[string] | 至少一个项目相对 glob，用于影响分析。 |
| `test` | object | 预期或已有的测试落点。 |
| `sources` | array[string] | 至少一个真实的项目相对源码/测试/文档文件。 |
| `tags` | array[string] | 可选；如 `冒烟`、`回归`。 |
| `alwaysRunOnAffected` | boolean | 变更命中 `paths` 时是否默认入选。 |

## 入口、前置数据和步骤

```yaml
entry:
  url: /login
  requiresAuth: false

fixtures:
  env:
    username: E2E_USER
    password: E2E_PASSWORD
  sources:
    login-user: existing-project-fixture

steps:
  - id: open-login
    title: 打开登录页
    action: navigate
    target:
      hint: 登录页路由
      value: /login
    expected: 页面显示账号与密码输入框和登录按钮。
    signal:
      kind: visible
      locator: { role: button, name: 登录 }
```

### `entry`

| 字段 | 类型 | 规则 |
|---|---|---|
| `url` | string | 必填。相对路由或用于分析的入口 URL；必须能在源码或路由配置中找到依据。 |
| `requiresAuth` | boolean | 必填。是否需要在进入前建立认证状态。 |

认证依赖的真实帐号只写在本机环境变量或安全数据源中，绝不能进入 YAML。

### `fixtures`

`fixtures` 可省略；提供时只允许以下两组字段，不能添加自由文本、凭据字段或任意嵌套对象：

```yaml
fixtures:
  env:
    username: E2E_USER
    password: E2E_PASSWORD
  sources:
    login-user: existing-project-fixture
```

- `env` 是 `小写 kebab-case 别名 → 环境变量名` 的对象；环境变量名必须匹配 `^[A-Z][A-Z0-9_]*$`。③只读取这些变量的值，绝不打印或回写。
- `sources` 是 `小写 kebab-case 别名 → 来源类型` 的对象；来源类型只能是 `existing-project-fixture`、`external-safe-data-source` 或 `not-required`。它只声明如何寻找安全数据，不携带数据本身。

禁止写入密码、token、会话 ID、Cookie、真实邮箱、电话号码、身份证件、完整请求头或任何可直接使用的私密值。完整校验器会拒绝 `env` / `sources` 以外的字段，也会拒绝不符合环境变量名或来源类型的值。

### `review`

`review` 记录流程为什么能进入 `ready`，避免 CI 自动验收被误认为人工确认。

```yaml
# 人工模式中的待确认草稿
review:
  mode: manual
  basis: pending-user-confirmation

# 人工确认后的 ready 流程
review:
  mode: manual
  basis: user-confirmed

# 仅当调用显式启用 approvalMode: source-validated 时允许
review:
  mode: source-validated
  basis: source-evidence-and-schema-validation
```

| 字段 | 类型 | 规则 |
|---|---|---|
| `mode` | string | `manual` 或 `source-validated`。 |
| `basis` | string | `manual` 时为 `pending-user-confirmation` 或 `user-confirmed`；`source-validated` 时必须为 `source-evidence-and-schema-validation`。 |

对 `status: ready` 且 `review.mode: source-validated` 的流程，完整 Schema 校验通过是必需条件。未启用自动模式、存在存疑项或无法运行完整校验器时，①必须写为 `draft`，不得伪造自动验收溯源。

### `steps`

每个步骤都必须包含：

- `id`：在该流程中唯一的小写 kebab-case 标识。
- `title`：用户正在完成的业务行为。
- `action`：`navigate`、`fill`、`click`、`select`、`upload`、`wait` 或 `assert`。
- `expected`：此步骤完成后可观察的业务结果。
- `signal`：支撑后续断言的可观察线索。

`target` 和 `data` 按 action 需要提供：

- `target.hint` 是面向人和代码复核的定位说明；对 `navigate`、`fill`、`click`、`select`、`upload` 必填。
- `target.value` 可用于稳定的路由、选项或已有的领域值；不要写 CSS/XPath。
- `data` 只能是 `fixtures.env.<别名>` 引用，或由这些引用组成的对象/数组；每个引用都必须存在于 `fixtures.env`。例如：

  ```yaml
  data:
    username: fixtures.env.username
    password: fixtures.env.password
  ```

  不得在 `data` 中放任何字面量、账号、密码、token 或其他秘密值。

一个步骤可以代表一段连贯的业务操作，例如“填写测试账号并提交”。③会回到源码决定具体填写和点击动作；不要为了模拟代码执行而把它拆成 CSS 级指令。

### `signal`

| `kind` | 必填字段 | 说明 |
|---|---|---|
| `visible` | `locator` | 元素可见是成功线索。 |
| `text` | `locator` | 某个区域显示预期业务文本；具体文本由 `expected` 或 locator 的语义说明。 |
| `url` | `value` | 页面到达稳定的相对路由或 URL。 |

`locator` 至少使用一组稳定的可访问性或测试线索：`{ role, name? }`、`{ label }`、`{ testId }` 或 `{ text }`。优先 role、label、testId。若源码只有不稳定选择器，保留为存疑并在报告中说明；不要把深层 CSS 或 `nth-child` 写进 YAML。

## 溯源、影响范围与测试落点

```yaml
paths:
  - src/auth/**
  - src/pages/login/**

test:
  source: external
  spec: tests/e2e/user-login.spec.js

sources:
  - src/auth/login-controller.ts
  - src/pages/login/LoginForm.tsx

tags: [冒烟]
alwaysRunOnAffected: true
```

- `paths` 用于 Git 影响分析，应覆盖实现该业务目标的主要目录；不要使用 `**` 这种无边界 glob。
- `sources` 是本次推断的证据文件，必须真实存在。它可以包含路由、页面、控制器、测试或 README。
- `test.spec` 是预期或现有 E2E spec 的项目相对路径。它必须位于顶层 `e2e/`、`playwright/`，或 `test(s)/e2e/`、`test(s)/playwright/` 下，且文件名为 `*.e2e.<js|ts|jsx|tsx|mjs|cjs|mts|cts>` 或 `*.spec.<js|ts|jsx|tsx|mjs|cjs|mts|cts>`；路径中的任何目录和最终文件都不得是符号链接。这能避免③把业务源码误认为可写测试文件。`test.source: external` 表示①登记了待③创建的落点；`existing` 表示该 spec 已存在。③成功创建 `test.spec` 后，只可把同一路径的 `test.source` 从 `external` 改为 `existing`，不改动其他流程语义。`existing` 的 spec 必须存在。
- `alwaysRunOnAffected: true` 只表示命中影响路径时的默认选择，不能绕过 `enabled: false`。

## 生命周期和变更规则

```text
draft --人工确认，①写入--> ready --③实跑通过--> active
draft --显式自动验收 + 证据齐全 + 完整校验通过，①写入--> ready
active --④证据校验通过且用户同意--> enabled: true
ready / active --业务语义变化，①更新--> draft + enabled: false
```

| 情况 | ①的写入行为 |
|---|---|
| 新流程 | 创建 `draft`、`enabled: false`。 |
| 用户确认草稿 | 将确认的 `draft` 改为 `ready`，并写入 `review.mode: manual` / `review.basis: user-confirmed`。 |
| 显式自动验收 | 仅在证据齐全、无存疑、完整校验通过时设为 `ready`，并写入 `review.mode: source-validated`。 |
| 已有流程新增独立目标 | 新建另一条 `draft`，不影响旧流程。 |
| 已有流程业务语义变化 | 原地更新同一 id，并先设 `status: draft`、`enabled: false`；显式自动验收的全部门槛通过后，才可在同一次有序操作中重新设为 `ready`。 |
| 纯实现变化 | 可更新 `sources` / `paths`；不改变 `status` 或 `enabled`。 |
| 业务目标下线 | 保留原 YAML，设为 `status: retired`、`enabled: false`，不删除文件也不移交③。 |
| `retired` 流程恢复 | 仅在用户明确要求恢复该目标后，按当前源码重新评审；默认写回 `draft`、`enabled: false` 与 `manual/pending-user-confirmation`，显式自动验收且通过全部门槛时才可重回 `ready`。 |

只有③可以将 `ready` 推进为 `active`，并在创建 spec 后执行上述唯一允许的 `test.source: external → existing` 同步。③不得接收 `draft` 或 `retired` 流程。只有④在证据校验通过、且用户明确同意时可以设 `enabled: true`。①绝不设 `active` 或 `enabled: true`。

## 轻量自检

没有②的完整校验器时，①至少检查：文件名与 id 一致、必填字段存在、enum 合法、步骤 id 唯一、来源文件存在、路径是相对路径、`test.spec` 是受限 E2E spec 路径、`fixtures` 只有受限结构且 `data` 只引用其 `env` 别名，以及 review 与 status 一致。人工模式下新建/语义更新流程处于 `draft` 且未启用。自动模式缺少②的完整校验器时，流程也必须保持 `draft` 且未启用。完整校验器可用时，它是可执行事实；本文件必须随之更新。
