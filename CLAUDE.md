# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**tuanzii** 是一个 Claude Code 本地 Marketplace 插件项目。它将自身注册为本地插件市场，使自定义 Skills 可通过 Claude Code 的 `/plugins` 命令被发现和安装。同时提供 Stop 钩子通知等增强功能。

## 安装

```bash
# macOS / Linux
./setup.sh

# Windows (PowerShell，需管理员权限或开启开发者模式)
.\setup.ps1
```

前置依赖：Node.js、已安装的 Claude Code（需要 `~/.claude` 目录）。

安装后需运行 `npm install` 安装 Node 依赖（`node-notifier`）。

安装脚本执行 4 步：创建 marketplace 符号链接 → 注册到 `settings.json` → 注册到 `known_marketplaces.json` → 创建插件缓存符号链接（使 skill 编辑免重装）。

## 架构

```
.claude-plugin/
  plugin.json            # 插件清单（name: tuanzii, version: 1.1.0）
skills/                  # Skills 目录，每个 skill 一个文件夹，入口为 SKILL.md
  git-commit/            # 智能 Git 提交
  git-rollback/          # 交互式回滚
  git-cleanBranches/     # 分支清理
  git-worktree/          # Worktree 管理
output-styles/           # 输出风格规则，每个风格一个 .md 文件
  engineer-professional.md   # 专业工程师
  laowang-engineer.md        # 老王暴躁技术流
  leibus-engineer.md         # 雷布斯发布会风格
  nekomata-engineer.md       # 猫娘工程师
  ojousama-engineer.md       # 傲娇大小姐
  rem-engineer.md            # 蕾姆女仆工程师
hooks/
  hooks.json             # Claude Code 钩子声明（Stop 事件触发通知）
monitors/
  monitors.json          # 监控配置（当前为空数组）
scripts/
  notify.js              # Stop 钩子脚本：读取 stdin JSON，发送系统通知
setup.sh                 # macOS/Linux 注册脚本
setup.ps1                # Windows PowerShell 注册脚本
package.json             # Node 依赖管理（commonjs，依赖 node-notifier）
```

无构建系统、无测试框架、无 lint 工具。项目是纯脚手架 + 钩子脚本。

## 关键机制

### 通知系统

`hooks/hooks.json` 注册了 Stop 事件钩子，当 Claude Code 会话结束时执行 `scripts/notify.js`：
- 从 stdin 读取 JSON（含 `last_assistant_message`）
- 通过 `node-notifier` 发送桌面系统通知
- 受 `userConfig.notify_enabled` 控制（环境变量 `TUANZII_NOTIFY_ENABLED`），设为 `false` 或 `0` 可关闭
- 5 秒超时保护，防止进程卡死阻塞 Claude 退出
- 任何错误静默退出，不阻塞 Claude

### 插件配置项

`plugin.json` 中的 `userConfig` 定义了用户可配置项：
- `notify_enabled` — 控制任务完成通知开关

## Skills

在根目录 `skills/` 下添加 skill，每个 skill 是一个文件夹，入口文件为 `SKILL.md`。缓存符号链接直接指向源目录，新增或修改 skill 后无需重新安装插件。

### Git 工具（Skills）

| Skill | 功能 |
|-------|------|
| `git-commit` | 智能提交：分析改动、自动生成 Conventional Commits 消息、支持 emoji/scope/拆分建议 |
| `git-rollback` | 交互式回滚：列分支→列版本→选模式（reset/revert）→二次确认，默认 dry-run |
| `git-cleanBranches` | 安全清理已合并/过期分支，支持 dry-run、保护分支白名单、远程清理 |
| `git-worktree` | Worktree 管理：智能路径、IDE 集成、内容迁移、环境文件自动复制 |

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
