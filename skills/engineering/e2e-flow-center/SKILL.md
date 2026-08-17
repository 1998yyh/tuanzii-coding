---
name: e2e-flow-center
description: 为已有 e2e-flows/ 的项目按需启动临时、本机的 E2E 流程看板，查看流程状态、影响路径和 e2e-flow-reports/ 抽离报告，或运行完整流程 Schema 校验时使用。用户提到“打开流程看板”“可视化流程”“看抽离报告”“哪些流程受影响”“校验 e2e-flows”时应使用。看板只读项目数据，绝不在目标项目安装 Web 应用、修改 YAML 或改 package.json；需要抽离流程时移交 e2e-flow-extract，需要写测试时移交 e2e-test-gen，需要运行或排障时移交 e2e-evidence。
---

# E2E Flow Center

②是四个 E2E Skill 的临时只读控制台和完整 Schema 校验器。它从自身携带的 Python 模板启动 `127.0.0.1` 看板；目标项目始终只是数据源，不会得到看板目录、依赖、配置文件或 YAML 副本。

## 套件角色与边界

| 编号 | Skill | 负责什么 |
|---|---|---|
| ① | `e2e-flow-extract` | 创建或维护 `e2e-flows/*.yaml`，并写不可变抽离报告。 |
| ② | `e2e-flow-center` | 本 Skill：完整校验、临时看板和只读数据展示。 |
| ③ | `e2e-test-gen` | 为 `ready` 流程生成并实跑 Playwright。 |
| ④ | `e2e-evidence` | 运行、收集证据、解释失败，并在获准时启用流程。 |

②绝不写入流程 YAML、报告 JSON、测试、业务代码、`playwright.config`、`package.json`、锁文件或 `node_modules`。流程或报告有误时，将错误显示在看板和命令输出中，不能“顺手修复”。

## 先读的契约

每次调用先阅读 [流程 Schema](../e2e-flow-extract/references/flow-schema.md)。用户要查看抽离报告、或报告页面发生变化时，再阅读 [抽离报告契约](../e2e-flow-extract/references/extraction-report-schema.md)。这两份文档定义数据；`scripts/validate.py` 是流程 Schema 的可执行实现。修改任一 Schema 规则时必须同改文档、校验器、看板展示和测试，避免静默漂移。

## 调用前自检与分流

1. 确认目标项目根目录；不要从工作区父目录猜测。
2. 检查 `e2e-flows/`。目录不存在或没有流程时，不启动空看板来替代分析：移交①。
3. 若用户的目标是生成/补齐 Playwright 测试，移交③；若是运行、重跑、截图、Trace 或失败诊断，移交④。④需要界面时可要求②先启动或复用当前项目的会话。
4. 对已有流程运行完整校验。无效 YAML 不阻止只读看板启动，但必须在结果中明确数量和错误，且不得宣称流程可执行。

## 完整校验

从 Skill 目录运行：

```bash
python3 scripts/validate.py --project <target-project-root>
```

校验器输出 JSON：每个 `e2e-flows/<id>.yaml` 的状态、面向字段的错误和汇总；只要存在错误便以非零状态退出。它检查版本、id/文件名、必填字段、步骤与 signal、相对路径、来源文件、状态/review 一致性和 `enabled` 的结构前置条件。它不会验证业务语义是否正确，也不会启动测试。

①在 `approvalMode: source-validated` 下必须成功运行该校验器，才能将流程推进为 `ready`；若②不可用，①必须保留 `draft`。

## 启动临时看板

```bash
python3 scripts/start_dashboard.py --project <target-project-root>
```

启动脚本会：清理该项目的失效会话、复制看板运行副本到系统临时目录、生成随机会话 token 和端口、绑定 `127.0.0.1`、通过受 token 保护的健康检查后输出 URL。URL 仅供当前本机浏览器打开；首次打开会将 token 换为 HttpOnly 会话 Cookie 并跳转到无 token 的地址。

看板提供：

- 流程目录：状态、类别、是否启用、Schema 错误、来源和影响路径。
- 抽离报告：`/reports/extraction` 展示 `e2e-flow-reports/*.json`，并逐项展示 `scenarios` 中的七种分流结果；不能把纯实现变化或无法判断折叠成业务变更。
- 报告详情：流程前后生命周期、证据路径与理由、覆盖/存疑和对③的移交。无效报告仅显示文件名与脱敏错误。

服务端只提供 `GET /api/health`、`GET /api/flows`、`GET /api/extraction-reports` 和 `GET /api/extraction-reports/<report-id>`。最后一个接口只接受契约规定的 report id，绝不接受任意文件路径。②自身不提供运行入口，也不直接执行项目命令；运行、重跑或排障一律移交④。

## 关闭与清理

```bash
python3 scripts/stop_dashboard.py --session <system-temp>/e2e-flow-center-<session-id>
python3 scripts/cleanup_stale_sessions.py --project <target-project-root>
```

停止脚本只终止它记录的进程组，随后删除相应的系统临时会话目录。清理脚本只处理同一项目、已失效的会话。任何路径不匹配、PID 不属于会话或项目根不一致时，保留目录并报告，而不是冒险终止或删除。

## 汇报格式

结束时报告：看板 URL（若已启动）、有效/无效流程数量、可执行流程数量（`active` 且 `enabled: true`）、有效/无效报告数量，以及下一步移交。若可执行流程是 0，要明确说明原因；缺少测试时移交③，而不要假装②已经运行了测试。
