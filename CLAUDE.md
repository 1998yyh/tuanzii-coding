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
  plugin.json            # 插件清单（name: tuanzii）
  marketplace.json       # 本地 marketplace 清单（新版 Claude Code 市场规范要求，含独立 metadata.version）
skills/                  # Skills 目录，每个 skill 一个文件夹，入口为 SKILL.md
  git-commit/            # 智能 Git 提交
  git-rollback/          # 交互式回滚
  git-cleanBranches/     # 分支清理
  git-worktree/          # Worktree 管理
  deepinit/              # 深度初始化 CLAUDE.md（替代内置 /init，含 references/）
  # ── 以下 11 个衍生自 obra/superpowers v6.0.3（MIT），见 NOTICE.superpowers.md ──
  brainstorming/         # 需求探索 → 设计文档
  writing-plans/         # 设计文档 → 细粒度实施计划
  subagent-driven-development/  # subagent 逐任务实现 + 评审（含 scripts/、prompt 模板）
  finishing-a-development-branch/  # 分支收尾
  using-git-worktrees/   # 隔离工作区
  test-driven-development/  # TDD 铁律
  systematic-debugging/  # 四阶段根因调试（含辅助脚本/技术文档）
  verification-before-completion/  # 完成前强制验证
  dispatching-parallel-agents/  # 并行派 agent
  using-tuanzii/         # Skill 路由元规则（含各平台 references/）
  writing-skills/        # 用 TDD 方式编写 skill（含测试方法论文档）
  # ── 以下衍生自 op7418/Humanizer-zh（MIT），见 NOTICE.humanizer-zh.md ──
  humanizer-zh/          # 去除文本 AI 写作痕迹（24 种模式检测 + 质量评分）
  # ── 以下衍生自 mattpocock/skills（MIT），见 NOTICE.mattpocock-skills.md ──
  grilling/              # 连环追问循环（打磨计划/决策的核心引擎）
  grill-me/              # /grill-me 入口：追问打磨计划（user-invoked）
  grill-with-docs/       # /grill-with-docs 入口：追问 + 沉淀文档（user-invoked）
  domain-modeling/       # 领域建模：维护 CONTEXT.md 词汇表与 ADR（含格式文档）
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
NOTICE.mattpocock-skills.md  # grilling/domain-modeling 衍生内容归属（MIT, Matt Pocock）
package.json             # Node 依赖管理（commonjs，当前无运行时依赖）
```

无构建系统、无测试框架、无 lint 工具。项目是纯脚手架。

## 开发规则

- **提交前必须升级版本号**：每次 `git commit` 之前，先升级 `.claude-plugin/plugin.json` 中的 `version`（遵循语义化版本：新功能 minor、修复 patch、破坏性变更 major），并同步升级 `.claude-plugin/marketplace.json` 的 `metadata.version`（两处独立维护，需手动保持一致）。注意 `package.json` 的 `version` 是另一套独立编号，不参与插件发布。

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
- skill 的 frontmatter `name:` 必须与所在文件夹同名（如 `skills/using-tuanzii/` 对应 `name: using-tuanzii`），否则 Claude Code 无法发现

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

在根目录 `skills/` 下添加 skill，每个 skill 是一个文件夹，入口文件为 `SKILL.md`。

### Git 工具（Skills）

| Skill | 功能 |
|-------|------|
| `git-commit` | 智能提交：分析改动、自动生成 Conventional Commits 消息、支持 emoji/scope/拆分建议 |
| `git-rollback` | 交互式回滚：列分支→列版本→选模式（reset/revert）→二次确认，默认 dry-run |
| `git-cleanBranches` | 安全清理已合并/过期分支，支持 dry-run、保护分支白名单、远程清理 |
| `git-worktree` | Worktree 管理：智能路径、IDE 集成、内容迁移、环境文件自动复制 |

### 项目上下文（Skills）

| Skill | 功能 |
|-------|------|
| `deepinit` | 深度初始化 CLAUDE.md：替代内置 /init，覆盖架构分层/环境规范/三层边界/测试策略（自 tuanzi 项目迁入） |

### 工程流程（Skills，衍生自 superpowers v6.0.3，MIT，见 NOTICE.superpowers.md）

| Skill | 功能 |
|-------|------|
| `brainstorming` | 需求探索：一次一问澄清意图 → 2-3 方案 → 设计文档落盘，未批准禁动手 |
| `writing-plans` | 把设计拆成细粒度计划：每步含完整代码/命令/预期输出，禁占位符 |
| `subagent-driven-development` | 每任务派 fresh subagent 实现 + 规格/质量双评审 + 进度账本抗压缩 |
| `finishing-a-development-branch` | 分支收尾：验证测试，给合并/PR/清理选项 |
| `using-git-worktrees` | 开始特性工作前确保隔离工作区 |
| `test-driven-development` | TDD 铁律：无失败测试禁写实现，含反借口表与红旗清单 |
| `systematic-debugging` | 四阶段调试：根因优先禁瞎修；连续 3 次修复失败熔断，转质疑架构 |
| `verification-before-completion` | 未跑验证命令禁声称完成：证据先于断言 |
| `dispatching-parallel-agents` | 2+ 独立问题域并行派 agent，含 prompt 四要素 |
| `using-tuanzii` | Skill 路由元规则：1% 可能适用即调用，process skill 优先 |
| `writing-skills` | 用 TDD 方式写 skill：压力场景先行，反合理化加固，SDO 发现优化 |

注：这组 skill 内部互相以 `tuanzii:<skill>` 引用，已与本插件自洽；`docs/superpowers/` 与 `.superpowers/` 路径沿用原版约定（本仓库已有对应目录）。全部 47 个文件含行内中文注解（统一 `【老王注】` 前缀，md 用 `> `、脚本用对应注释语法），英文原文一字未动；`grep '【老王注】'` 可速览全部注解，`grep -v '【老王注】'` 即还原原版。

### 写作辅助（Skills，衍生自 op7418/Humanizer-zh，MIT，见 NOTICE.humanizer-zh.md）

| Skill | 功能 |
|-------|------|
| `humanizer-zh` | 去除文本 AI 写作痕迹：24 种模式检测（AI 词汇/三段式/破折号滥用/模糊归因等）+ 改写示例 + 50 分制质量评分 |

### 追问与领域建模（Skills，衍生自 mattpocock/skills，MIT，见 NOTICE.mattpocock-skills.md）

| Skill | 功能 |
|-------|------|
| `grilling` | 连环追问循环：一次一问打磨计划/决策，事实自查、决策归用户（model-invoked 核心引擎） |
| `grill-me` | `/grill-me` 入口：对计划或设计进行刨根问底的追问（user-invoked） |
| `grill-with-docs` | `/grill-with-docs` 入口：追问 + 同步沉淀 `CONTEXT.md` 词汇表与 ADR（user-invoked） |
| `domain-modeling` | 领域建模：挑战术语、场景压力测试、就地维护 `CONTEXT.md` 和 `docs/adr/`（含格式文档） |

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
**版本**: v1.1
**最后更新**: 2026-07-19
