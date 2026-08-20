# Changelog

本文件记录 tuanzii Claude Code 插件的重要变更。插件版本以 `.claude-plugin/plugin.json` 和 `.claude-plugin/marketplace.json` 为准。

## [4.2.0] - 2026-08-20

### 新增

- e2e-flow-center 证据中心执行日志支持在线打开：log 文件改为新标签页内联查看（`text/plain`），不再强制下载；仅 Trace 与未知类型附件保留强制下载。
- e2e-evidence 证据契约调整：截图策略由 `only-on-failure` 改为 `on`——每次运行（无论成败）都保留截图；视频与 Trace 保持 `retain-on-failure` 不变。

## [4.1.0] - 2026-08-20

### 新增

- e2e-flow-center 看板抽离报告升级为叙事视图：报告头展示 headline（缺省时按 summary 自动拼一句话总结）、六格摘要条（新建/语义更新/仅溯源/下线/待确认/阻塞）、变更卡片墙、覆盖区域与存疑双栏、移交 e2e-test-gen 区块（含阻塞原因中文标签）。
- 变更卡片承载生命周期芯片（before → after + 验收依据）、可选契约字段 `fieldChanges` 的字段级 diff（del/ins 对照）、源码证据 chips（`path:行号` + 理由）与下一步动作中文标签。
- 报告 ↔ 看板双向联动：变更卡片上的 flowId 点击跳回三栏看板并选中该流程；从报告进入看板时详情页提供"← 返回抽离报告"入口。
- 状态漂移提示：对比报告快照与当前 `e2e-flows/` YAML，快照后 status / enabled 发生变化时在卡片头部标注。
- 看板视觉重做：引入 Fira Sans / Fira Code 字体，报告列表按钮改为时间 + 场景 + 变更/阻塞计数 + 短 id。

### 修复

- 移除 `.claude-plugin/plugin.json` skills 数组中重复的 `./skills/grilling/grilling` 条目（41 → 40），CLAUDE.md 计数与 4.0.0 changelog 条目同步勘误。

## [4.0.0] - 2026-08-18

### 破坏性变更

- 移除 8 个 superpowers 衍生 skill：`subagent-driven-development`、`finishing-a-development-branch`、`using-git-worktrees`、`test-driven-development`、`systematic-debugging`、`verification-before-completion`、`dispatching-parallel-agents` 与路由元规则 `using-tuanzii`；`skills/process/` 仅保留 `brainstorming`，skill 总数 48 → 40（2026-08-19 勘误：原登记 "49 → 41" 系 4.0.0 编辑时 `grilling` 条目手滑重复一行所致，重复条目已于同日移除）。
- `brainstorming` 加 `disable-model-invocation: true`：模型不再默认调用，仅用户显式 `/tuanzii:brainstorming` 触发。
- 移除 `docs/superpowers/` 流程产物目录；`brainstorming` 设计文档落盘路径不变，运行时自建。

### 新增

- e2e-flow-center 看板升级为三栏工作台：左栏搜索与分类导航（含变更文件面板），中栏流程详情（hero、状态/影响/优先级徽章、业务步骤、测试来源、影响路径、校验诊断），右栏运行记录与单次运行结果；顶部双视图切换保留抽离报告左右布局。
- 运行历史与证据中心：扫描 `results/*.json` 运行清单（按时间倒序，上限 50 条，载荷带 total），逐流程展开结果与错误；证据模态框支持截图网格、视频回放与 Trace/日志/HTML 报告下载，Esc 关闭、焦点圈定、返回焦点；清单声明却缺失的产物显示警告。
- Git 影响徽章：只读对比工作区变更（相对 HEAD 的改动与未跟踪文件）和流程 `paths`，标注受影响流程及原因（`path-match` / `always-run`）；非 git 仓库自动降级。
- 服务端新增 `GET /api/runs` 与带鉴权的 `GET /evidence/<path>`（限定 `results/` 内、防路径穿越与符号链接逃逸）；`/api/flows` 载荷新增 `changedPaths` / `gitAvailable`，流程暴露 steps 脱敏视图（仅 id/title/expected，步骤数据永不出服务器）。

### 修复

- 修复视图切换失效：`.workspace` 的 `display:grid` 压过 UA 的 `[hidden]`，导致流程看板与抽离报告叠在同一页渲染。
- 修复非 dict 顶层 YAML（列表/标量）打挂 `/api/flows` 与 `/api/health`：此类文件现在正常显示为无效并给出错误，而非整个载荷 500。
- 修复运行清单 `flowId` / `id` 为绝对路径或含 `..` 时，证据目录扫描逃逸 `results/` 前缀并遍历全盘的问题。
- 流程 `paths` 的 glob 匹配由正则翻译改为段式 DP，消除连排 `**/` 模式的灾难回溯（曾可挂起请求 10 秒以上）。
- `_run_git` 捕获 `UnicodeDecodeError`：非 UTF-8 文件名降级为"git 不可用"，不再 500。
- `/api/health` 不再执行 git 子进程与影响分析，大仓库下启动健康检查不再超时导致健康服务器被误杀。
- git 变更路径统一为仓库根相对并按项目前缀裁剪，修复 monorepo 子目录下受影响判定的路径基准混乱与项目外变更泄漏。

### 文档

- e2e-flow-center SKILL.md 能力描述、接口清单与 evals 触发用例同步（新增 3 例共 8 例）；契约测试 21 → 25 项；CLAUDE.md 架构与表格同步。

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
