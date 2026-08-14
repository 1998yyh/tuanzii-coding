# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**tuanzii** 是一个 Claude Code Marketplace 插件项目。它以 git 远程市场的形式分发，使自定义 Skills 可通过 Claude Code 的 `/plugins` 命令被发现和安装。

## 安装

```bash
claude plugin marketplace add 1998yyh/tuanzii-coding
claude plugin install tuanzii@tuanzii
```

前置依赖：已安装的 Claude Code。插件以托管 bundle 形式安装，跟随 git 远程版本更新；本仓库不再提供本地符号链接注册脚本（`setup.sh` / `setup.ps1` 已移除）。

## 架构

```
.claude-plugin/
  plugin.json            # 插件清单（name: tuanzii），含 skills 数组显式列出全部 48 个 skill 路径
  marketplace.json       # 本地 marketplace 清单（新版 Claude Code 市场规范要求，含独立 metadata.version）
skills/                  # Skills 目录，按用途分组子目录，每个 skill 一个文件夹，入口为 SKILL.md
  git/                   # Git 工具（7 个）
    git-commit/          # 智能 Git 提交
    git-rollback/        # 交互式回滚
    git-cleanBranches/   # 分支清理
    git-worktree/        # Worktree 管理
    resolving-merge-conflicts/  # 解决 merge/rebase 冲突 ※
    git-guardrails-claude-code/ # 钩子拦截危险 git 命令 ※
    setup-pre-commit/    # Husky + lint-staged 预提交钩子 ※
  process/               # 工程流程（9 个，衍生自 obra/superpowers v6.0.3，MIT，见 NOTICE.superpowers.md）
    brainstorming/       # 需求探索 → 设计文档
    subagent-driven-development/  # subagent 逐任务实现 + 评审（含 scripts/、prompt 模板）
    finishing-a-development-branch/  # 分支收尾
    using-git-worktrees/ # 隔离工作区
    test-driven-development/  # TDD 铁律
    systematic-debugging/  # 四阶段根因调试（含辅助脚本/技术文档）
    verification-before-completion/  # 完成声明前的证据门禁
    dispatching-parallel-agents/  # 并行派 agent
    using-tuanzii/       # Skill 路由元规则（含各平台 references/）
  grilling/              # 追问与领域建模（4 个，衍生自 mattpocock/skills，MIT，见 NOTICE.mattpocock-skills.md）
    grilling/            # 连环追问核心引擎（design tree / frontier 机制）
    grill-me/            # /grill-me 入口（user-invoked）
    grill-with-docs/     # /grill-with-docs 入口：追问 + 沉淀文档（user-invoked）
    domain-modeling/     # 领域建模：CONTEXT.md 词汇表与 ADR（含格式文档）
  engineering/           # 工程流水线与 E2E 流程管理（19 个；其中 15 个衍生自 mattpocock/skills ※）
    ask-matt/            # skill 路由入口
    codebase-design/     # 深模块设计共享词汇库
    code-review/         # 双轴评审（规范 + spec）
    diagnosing-bugs/     # 疑难 bug 诊断循环（含 HITL 脚本模板）
    improve-codebase-architecture/  # 架构改进扫描 + HTML 报告
    implement/           # 按 spec/工单实现
    prototype/           # 一次性原型
    research/            # 一手资料调研落盘
    tdd/                 # 测试驱动开发（含 mocking/tests 文档）
    to-spec/             # 对话 → spec 发布
    to-tickets/          # 计划 → tracer-bullet 工单
    triage/              # issue/PR 状态机分诊
    wayfinder/           # 超大规模工作的决策工单地图
    wizard/              # 生成交互式 bash 向导（含 template.sh）
    setup-matt-pocock-skills/  # 工程流水线一次性初始化
    e2e-flow-extract/    # 从源码抽离和维护 E2E 业务流程 YAML
    e2e-flow-center/     # E2E 流程 Schema 校验与临时只读看板
    e2e-test-gen/        # 为 ready 流程生成并验证 Playwright 测试
    e2e-evidence/        # 运行 active 流程并归档可复核证据
  productivity/          # 效率（5 个，衍生自 mattpocock/skills ※）
    handoff/             # 对话交接文档
    teach/               # 工作区内教学（含格式文档）
    to-questionnaire/    # 决策 → 问卷
    wait-what/           # 重新表达未讲清的消息
    writing-for-agents/  # 写给 agent 的文档（含 SKILL-MECHANICS.md）
  writing/
    humanizer-zh/        # 去除文本 AI 写作痕迹（衍生自 op7418/Humanizer-zh，MIT，见 NOTICE.humanizer-zh.md）
  misc/                  # 杂项（2 个，衍生自 mattpocock/skills ※）
    migrate-to-shoehorn/ # 测试 as 断言 → shoehorn
    scaffold-exercises/  # 课程练习目录脚手架
  project/
    deepinit/            # 深度初始化 CLAUDE.md（替代内置 /init，含 references/）
output-styles/           # 输出风格规则，每个风格一个 .md 文件
  engineer-professional.md   # 专业工程师
  laowang-engineer.md        # 老王暴躁技术流
  leibus-engineer.md         # 雷布斯发布会风格
  nekomata-engineer.md       # 猫娘工程师
  ojousama-engineer.md       # 傲娇大小姐
  rem-engineer.md            # 蕾姆女仆工程师
hooks/
  hooks.json             # Claude Code 钩子声明（当前无注册钩子）
monitors/
  monitors.json          # 监控配置（当前为空数组）
docs/
  superpowers/           # superpowers 流程产物（plans/ 实施计划、specs/ 设计文档）
NOTICE.superpowers.md    # superpowers 衍生内容归属（MIT, Jesse Vincent）
NOTICE.humanizer-zh.md   # humanizer-zh 衍生内容归属（MIT, 歸藏）
NOTICE.mattpocock-skills.md  # mattpocock/skills 衍生内容归属（MIT, Matt Pocock，共 29 个 skill）
package.json             # Node 依赖管理（commonjs，当前无运行时依赖）
```

（※ = 衍生自 mattpocock/skills v1.2.3，全中文重写；mattpocock 系 skill 各含 `agents/openai.yaml` Codex 兼容文件，保持英文原样）

无构建系统、无测试框架、无 lint 工具。项目是纯脚手架。

## 核心架构：插件发现与加载

```text
.claude-plugin/marketplace.json
  -> 声明 marketplace 元数据与插件 source: "./"
  -> .claude-plugin/plugin.json 提供插件身份、安装版本，并以 skills 数组显式列出全部 skill 路径
  -> Claude Code 从 plugin.json 的 skills 数组、output-styles/、hooks/、monitors/ 发现插件能力
```

- `skills/<分组>/<name>/SKILL.md`：skills/ 下按用途分组（git/process/grilling/engineering/productivity/writing/misc/project），frontmatter `name` 必须与最内层文件夹同名。
- skill 路径必须在 `.claude-plugin/plugin.json` 的 `skills` 数组中显式登记（格式 `"./skills/<分组>/<name>"`），否则无法被发现——分组嵌套后不再依赖自动扫描。
- `.claude-plugin/plugin.json` 的 `version` 与 `.claude-plugin/marketplace.json` 的 `metadata.version` 是发布版本事实来源，必须保持一致。
- `package.json` 只记录仓库的 Node 元数据，不控制插件发布版本。

## 可执行验证命令

```bash
# 检查 JSON 清单语法
node -e "const fs=require('fs'); for (const p of ['package.json','.claude-plugin/plugin.json','.claude-plugin/marketplace.json','hooks/hooks.json','monitors/monitors.json']) JSON.parse(fs.readFileSync(p,'utf8'))"

# 检查仓库内 shell 脚本语法
sh -n skills/process/brainstorming/scripts/start-server.sh skills/process/brainstorming/scripts/stop-server.sh skills/process/subagent-driven-development/scripts/review-package skills/process/subagent-driven-development/scripts/sdd-workspace skills/process/subagent-driven-development/scripts/task-brief skills/engineering/diagnosing-bugs/scripts/hitl-loop.template.sh skills/engineering/wizard/template.sh skills/git/git-guardrails-claude-code/scripts/block-dangerous-git.sh

# 检查补丁中的空白错误
git diff --check
```

## 开发规则

- **提交前必须升级版本号**：每次 `git commit` 之前，先升级 `.claude-plugin/plugin.json` 中的 `version`（遵循语义化版本：新功能 minor、修复 patch、破坏性变更 major），并同步升级 `.claude-plugin/marketplace.json` 的 `metadata.version`（两处独立维护，需手动保持一致）。注意 `package.json` 的 `version` 是另一套独立编号，不参与插件发布。
- **Skill 清单必须同步**：新增、删除或重命名 `skills/*/*` 时，同步更新 `.claude-plugin/plugin.json` 的 `skills` 数组、`skills/process/using-tuanzii/SKILL.md` 与本文件；若条目衍生自外部项目，还要同步对应 `NOTICE.<来源>.md`。

## 环境特殊规范

**本机可能残留旧的本地注册状态**。仓库早期的 `setup.sh` / `setup.ps1`（已删除）曾在 `~/.claude/` 下创建符号链接并改写全局配置：

| 历史操作 | 目标 | 后果 |
|------|------|------|
| 创建符号链接 | `~/.claude/plugins/marketplaces/tuanzii` → 本仓库 | 全局 marketplace 列表变化 |
| 改写 JSON | `~/.claude/settings.json`、`~/.claude/plugins/known_marketplaces.json` | 影响所有项目的 Claude Code 会话 |
| 创建缓存符号链接 | `~/.claude/plugins/cache/...` → 本仓库对应版本目录 | skill 编辑免重装 |

如果本机仍通过这些符号链接使用插件，改动 `skills/` 会立即对全局生效、无缓冲。要彻底切到远程 marketplace 方式，需先在 `~/.claude/` 下清理这些残留再重新安装。

## 三层边界模型

### ✅ 必须执行

- `git commit` 前升级 `.claude-plugin/plugin.json` 的 `version`，并同步 `marketplace.json` 的 `metadata.version`（见「开发规则」）
- 新增衍生自外部项目的内容时，创建/更新对应 `NOTICE.<来源>.md` 归属文件（照 `NOTICE.superpowers.md` 格式）
- 修改 superpowers 衍生 skill 时，注解统一用 `【老王注】` 前缀（md 用 `> ` 引用块、脚本用对应注释语法），保持 `grep '【老王注】'` 可速览、`grep -v '【老王注】'` 可还原
- skill 的 frontmatter `name:` 必须与所在文件夹同名（如 `skills/process/using-tuanzii/` 对应 `name: using-tuanzii`），否则 Claude Code 无法发现

### ⚠️ 需先询问

- 清理 `~/.claude/` 下旧的本地注册残留（符号链接、全局 JSON 配置，见上节）
- 删除 `skills/` 或 `output-styles/` 下的整个条目（若本机仍走旧缓存符号链接，删除立即对全局生效，无缓冲）

### ❌ 禁止操作

- 用户未主动要求时，执行 `git commit` / 建分支 / `git push` 等 git 写操作
- 改动 superpowers 衍生 skill 的英文原文——只能在旁边加 `【老王注】` 注解（归属与可还原性要求）
- 依赖 `npm test` 做验证——`package.json` 里它是 `exit 1` 的占位符

## 测试与验证

无自动化测试框架。验证手段按场景：

- **skill 改动**：在 Claude Code 会话中用 `/tuanzii:<skill>` 触发验证；若本机仍走旧缓存符号链接则改动即时生效，否则需等插件更新
- **插件清单/版本号改动**：push 后在已安装机器上更新 marketplace 并用 `/plugins` 确认

## Skills

在根目录 `skills/` 下按分组子目录组织 skill，每个 skill 是一个文件夹，入口文件为 `SKILL.md`，路径需在 `.claude-plugin/plugin.json` 的 `skills` 数组登记。

### Git 工具（skills/git/）

| Skill | 功能 |
|-------|------|
| `git-commit` | 智能提交：分析改动、自动生成 Conventional Commits 消息、支持 emoji/scope/拆分建议 |
| `git-rollback` | 交互式回滚：列分支→列版本→选模式（reset/revert）→二次确认，默认 dry-run |
| `git-cleanBranches` | 安全清理已合并/过期分支，支持 dry-run、保护分支白名单、远程清理 |
| `git-worktree` | Worktree 管理：智能路径、IDE 集成、内容迁移、环境文件自动复制 |
| `resolving-merge-conflicts` ※ | 五步流程解决进行中的 merge/rebase 冲突 |
| `git-guardrails-claude-code` ※ | 配置 Claude Code PreToolUse 钩子拦截危险 git 命令 |
| `setup-pre-commit` ※ | 配置 Husky + lint-staged + Prettier 预提交钩子，串跑 typecheck 与测试 |

### 工程流程（skills/process/，衍生自 superpowers v6.0.3，MIT，见 NOTICE.superpowers.md）

| Skill | 功能 |
|-------|------|
| `brainstorming` | 需求探索：一次一问澄清意图 → 2-3 方案 → 设计文档落盘，未批准禁动手 |
| `subagent-driven-development` | 每任务派 fresh subagent 实现 + 规格/质量双评审 + 进度账本抗压缩 |
| `finishing-a-development-branch` | 分支收尾：验证测试，给合并/PR/清理选项 |
| `using-git-worktrees` | 开始特性工作前确保隔离工作区 |
| `test-driven-development` | TDD 铁律：无失败测试禁写实现，含反借口表与红旗清单 |
| `systematic-debugging` | 四阶段调试：根因优先禁瞎修；连续 3 次修复失败熔断，转质疑架构 |
| `verification-before-completion` | 完成声明前的证据门禁：按结论选择充分检查，并披露未验证项 |
| `dispatching-parallel-agents` | 2+ 独立问题域并行派 agent，含 prompt 四要素 |
| `using-tuanzii` | Skill 路由元规则：1% 可能适用即调用，process skill 优先 |

注：这组 skill 内部互相以 `tuanzii:<skill>` 引用，已与本插件自洽；`docs/superpowers/` 与 `.superpowers/` 路径沿用原版约定（本仓库已有对应目录）。除 `verification-before-completion` 已按当前工作流精简重写外，其余 Superpowers 衍生内容通过 `【老王注】` 旁注适配，保留上游英文原文；`grep '【老王注】'` 可速览这些旁注。

### 追问与领域建模（skills/grilling/，衍生自 mattpocock/skills ※）

| Skill | 功能 |
|-------|------|
| `grilling` | 连环追问核心引擎：design tree / frontier / 轮次机制，事实 sub-agent 自查、决策归用户（model-invoked） |
| `grill-me` | `/grill-me` 入口：对计划或设计连环追问打磨（user-invoked） |
| `grill-with-docs` | `/grill-with-docs` 入口：追问 + 同步沉淀 `CONTEXT.md` 词汇表与 ADR（user-invoked） |
| `domain-modeling` | 领域建模：挑战术语、场景压力测试、就地维护 `CONTEXT.md` 和 `docs/adr/`（含格式文档） |

### 工程流水线（skills/engineering/，衍生自 mattpocock/skills ※）

| Skill | 功能 |
|-------|------|
| `ask-matt` | 不确定该用哪个 skill/流程时的路由入口 |
| `codebase-design` | 深模块设计共享词汇库：接口设计、加深机会、接缝位置、可测试性 |
| `code-review` | 双轴评审：规范符合度 + spec 符合度，并行 sub-agent 出报告 |
| `diagnosing-bugs` | 疑难 bug / 性能回退的交互式诊断循环（含 HITL 脚本模板） |
| `improve-codebase-architecture` | 扫描架构改进机会 → 可视化 HTML 报告 → 选一个追问打磨 |
| `implement` | 按 spec 或工单集实现一块工作 |
| `prototype` | 一次性原型：验证状态模型/逻辑手感或探索 UI 形态 |
| `research` | 查高信任一手资料，结论落盘为 Markdown（可派后台 agent） |
| `tdd` | 测试驱动开发实践（red-green-refactor，含 mocking/tests 专题文档） |
| `to-spec` | 把当前对话综合成 spec 发布到 issue tracker（纯综合不采访） |
| `to-tickets` | 计划/spec 拆成 tracer-bullet 工单，声明阻塞边并发布 |
| `triage` | issue/外部 PR 状态机分诊：分类→验证→追问→写 agent 可执行简报 |
| `wayfinder` | 超大规模工作规划：issue tracker 上的决策工单地图逐个消解 |
| `wizard` | 生成交互式 bash 向导，引导人完成只有人能做的步骤（配密钥/开基础设施） |
| `setup-matt-pocock-skills` | 工程流水线一次性初始化：issue tracker、分诊标签、文档布局 |

流水线主线：`to-spec` → `to-tickets` → `triage` → `wayfinder` → `implement`，各环节可用 `grilling` 系压力测试，`codebase-design` 提供共享设计语言。首次使用前跑一次 `setup-matt-pocock-skills`。

### E2E 流程管理（skills/engineering/）

| Skill | 功能 |
|-------|------|
| `e2e-flow-extract` | 从源码、路由、已有测试和产品文档抽离或维护端到端业务流程 YAML，并写审计报告 |
| `e2e-flow-center` | 完整校验 `e2e-flows/`，并从临时 localhost 看板查看流程与抽离报告 |
| `e2e-test-gen` | 将已确认的 ready 流程转换为并验证 Playwright 测试；通过后推进为 active |
| `e2e-evidence` | 运行 active 流程，归档截图、视频、Trace、HTML 报告与日志，并基于证据解释失败 |

### 效率（skills/productivity/，衍生自 mattpocock/skills ※）

| Skill | 功能 |
|-------|------|
| `handoff` | 把当前对话压缩成交接文档，让另一个 agent 接手 |
| `teach` | 在工作区内教用户新技能/概念（含词汇表/学习记录等格式文档） |
| `to-questionnaire` | 把答不全的决策变成问卷交给别人填 |
| `wait-what` | 上一条消息没讲清时重新表达 |
| `writing-for-agents` | 写给 agent 看的文档：创建/编辑 skill、AGENTS.md、CLAUDE.md 时用 |

### 写作（skills/writing/，衍生自 op7418/Humanizer-zh，MIT，见 NOTICE.humanizer-zh.md）

| Skill | 功能 |
|-------|------|
| `humanizer-zh` | 去除文本 AI 写作痕迹：24 种模式检测（AI 词汇/三段式/破折号滥用/模糊归因等）+ 改写示例 + 50 分制质量评分 |

### 杂项（skills/misc/，衍生自 mattpocock/skills ※）

| Skill | 功能 |
|-------|------|
| `migrate-to-shoehorn` | 测试里的 `as` 类型断言迁移到 @total-typescript/shoehorn |
| `scaffold-exercises` | 课程练习目录脚手架（章节/题目/解答/讲解） |

### 项目上下文（skills/project/）

| Skill | 功能 |
|-------|------|
| `deepinit` | 深度初始化 CLAUDE.md：替代内置 /init，覆盖架构分层/环境规范/三层边界/测试策略 |

※ = 衍生自 [mattpocock/skills](https://github.com/mattpocock/skills) v1.2.3（MIT，见 NOTICE.mattpocock-skills.md），共 29 个，均已全中文重写；frontmatter `name` 保持英文与文件夹同名，`agents/openai.yaml` 与脚本文件保持原样。功能重叠提示：`process/test-driven-development`（重纪律）与 `engineering/tdd`（重实践）并存；`process/systematic-debugging`（四阶段根因）与 `engineering/diagnosing-bugs`（交互式诊断环）并存。

## 输出风格（Output Styles）

在根目录 `output-styles/` 下以 `.md` 文件添加输出风格规则。每个文件定义一种人格化的代码交互风格。

| Rule | 风格 |
|------|------|
| `engineer-professional` | 专业工程师：严谨技术导向，SOLID/KISS/DRY/YAGNI 原则 |
| `laowang-engineer` | 老王暴躁技术流：骂骂咧咧但代码质量极高 |
| `leibus-engineer` | 雷布斯发布会风格：数字化表达、制造期待感、强调性价比 |
| `nekomata-engineer` | 猫娘工程师幽浮喵：可爱猫娘特质 + 严谨工程素养 |
| `ojousama-engineer` | 傲娇大小姐哈雷酱：高贵优雅 + 完美主义 |
| `rem-engineer` | 蕾姆女仆工程师：温柔奉献 + 冷静果敢执行力 |

---
**版本**: v1.6
**最后更新**: 2026-08-16
