---
name: e2e
description: 端到端业务流程的统一入口。用户说“做 e2e”“把端到端测起来”“梳理并写测试”“跑一下 e2e”“打开流程看板”“为什么 E2E 失败”，或还没指定只要抽离、只要看板、只要生成测试、只要归档证据时使用。按意图分流到四个子 skill；完整链路默认走抽离→确认→生成测试的快路径。
---

# E2E

人只记这一个入口。四个子 skill 仍是契约和实现的家；本 skill 只负责分流，以及第一次怎么用最少来回跑通。

## 子 skill

加载前按本表解析。不要把子 skill 的 Schema、硬协议或 Playwright 模式抄进本文件。

| 何时 | 加载并遵循 |
|---|---|
| 抽离或维护业务流程 YAML | [e2e-flow-extract](../e2e-flow-extract/SKILL.md) |
| 校验或打开临时看板 | [e2e-flow-center](../e2e-flow-center/SKILL.md) |
| 为 `ready` 流程写或修 Playwright | [e2e-test-gen](../e2e-test-gen/SKILL.md) |
| 跑 `active` 并归档证据 | [e2e-evidence](../e2e-evidence/SKILL.md) |

校验器和看板脚本在 `../e2e-flow-center/scripts/`。用 `python` 或 `python3` 调用；Windows 与 macOS/Linux 同一套脚本，缺依赖时安装到用户缓存 runtime，不写入目标项目。

## 分流

用户已经点名只要其中一件时，直接加载对应子 skill，不要再问要不要走完整链路。

| 用户意图 | 动作 |
|---|---|
| 只要梳理或抽流程、不写测试 | extract |
| 只要看板、报告或影响范围 | center；没有 `e2e-flows/` 则先 extract |
| 只要写或修 Playwright | test-gen；没有 `ready` 则先走快路径的抽离和确认 |
| 只要跑、重跑或看失败证据 | evidence；没有 `active` 则说明缺哪一步 |
| “做 e2e / 把端到端测起来 / 梳理并写测试” | 快路径 |
| 说不清 | 快路径，不要把四个选项甩给人 |

## 快路径

目标：用最少来回得到 1 条可跑的 P0 流程测试。不要第一次就抽完整覆盖图。

1. 确认目标项目根。
2. 没有 `e2e-flows/` 或目录为空：按 extract 做首次抽离，优先 1 条（最多 3 条）P0 身份认证或核心提交，全部 `draft`。其余区域写进报告的 uncovered，不要为此再开一轮抽离。
3. 已有 YAML：只处理用户点名的流程，或一条最高优先级的 `draft` / `ready`。
4. 向用户展示 persona、goal、入口、成功信号。用户确认后按 extract 的「确认后交给③的硬协议」升 `ready`，立即加载 test-gen。
5. Playwright 未安装：按 test-gen 规则报告阻塞并请求授权安装，不要自行 `npx` 下载。
6. 单文件全绿变为 `active` 后，问要不要打开看板或跑 evidence；不要默认再跑一遍。

确认仍在对话里完成。看板只读，不能点确认或运行。
