# Changelog

本文件记录 tuanzii Claude Code 插件的重要变更。插件版本以 `.claude-plugin/plugin.json` 和 `.claude-plugin/marketplace.json` 为准。

## [3.3.1] - 2026-08-17

### 修复

- 抽离报告契约补齐与七类分流一一对应的枚举：`scenarios` 新增 `inventory`（已有流程盘点）与 `goal-retired`（业务目标下线），`operation` 新增 `retired`，修复盘点/下线场景无法如实填写报告的自相矛盾；`summary.retiredFlowCount` 向后兼容，旧报告缺省视为 `0`。
- 修正 e2e-flow-center 文档与实现的矛盾：移除不存在的看板"运行按钮"描述，frontmatter 的"Git 影响范围"更正为"影响路径"；e2e-evidence 移交说明移除看板不支持的"结果关联"。
- [3.3.0] 条目补登 `approvalMode: source-validated` 自动验收管线说明。

### 重构

- e2e-flow-center 看板后端抽取 `common.py` 共享模块，统一生命周期/review 校验与路径、文本守卫，消除 `validation.py` 与 `reports.py` 之间的逐字重复；合并 `app.py` 路由的 token 交换逻辑。
- 统一四个 E2E skill 的 `agents/openai.yaml` 口径（中文描述 + implicit invocation）；移除 dashboard `pyproject.toml` 中不生效的 pytest 配置。

## [3.3.0] - 2026-08-16

### 新增

- 新增 E2E 流程 Skill 套件：`e2e-flow-extract`、`e2e-flow-center`、`e2e-test-gen` 与 `e2e-evidence`。
- 套件覆盖从源码抽离业务流程、Schema 校验与临时看板、Playwright 测试生成，到运行证据归档与失败解释的完整协作链路。
- 流程 Schema 采用 v2，限制 E2E spec 写入位置，并要求测试数据只引用受控环境变量别名。
- 抽离支持 `approvalMode: source-validated` 自动验收管线：关键业务字段均有源码证据、无存疑且完整 Schema 校验通过的流程可直接推进 `ready`，并在流程 `review` 与报告 `approvalMode` 字段留下验收溯源，供已授权的 CI / 自动化管线显式启用。

## [3.1.0] - 2026-08-11

### 流程精简

- 移除 `writing-plans` skill；`brainstorming` 完成并获得用户确认后，改由主会话直接产出细粒度实施计划。
- 移除 `writing-skills` skill 及其配套参考资料、示例和渲染脚本。

### 变更

- 更新 `brainstorming`、`subagent-driven-development` 和 `using-tuanzii`，使流程不再依赖已移除的 planning/skill-authoring skill。
- 将 `verification-before-completion` 从重复的强制规则精简为证据门禁：按结论选择充分检查，报告最新证据，并披露未验证项和剩余风险。
- 将 Superpowers 衍生 skill 清单从 11 项调整为 9 项，并同步更新归属说明。

### 文档

- 通过 `deepinit` 增量刷新 `CLAUDE.md`，补充插件发现链路、可执行验证命令和 skill 清单同步规则。
- 更新工程流程索引及当前项目上下文版本。
- 忽略 `.reasonix/` 生成的本地会话元数据，避免进入版本控制。
