# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

这是一个 **Claude Code 本地 Marketplace 插件**项目（"tuanzii"）。它将自身注册为本地插件市场，使得自定义 Skills 可以通过 Claude Code 中的 `/plugins` 命令被发现和安装。

## 安装

```bash
./setup.sh
```

前置依赖：Node.js（脚本中用于 JSON 操作）和已安装的 Claude Code（需要 `~/.claude` 目录）。脚本执行以下步骤：

1. 在 `~/.claude/plugins/marketplaces/tuanzii` 创建指向项目目录的符号链接
2. 在 `~/.claude/settings.json` 的 `extraKnownMarketplaces` 中注册 marketplace
3. 在 `~/.claude/plugins/known_marketplaces.json` 中注册
4. 在 `~/.claude/plugins/cache/tuanzii/<name>/<version>` 创建缓存符号链接，使 skill 编辑无需重新安装即可生效

## 架构

项目仅包含两个文件：
- **`setup.sh`** — Bash 注册/安装脚本，执行所有 marketplace 注册步骤
- **`.claude-plugin/plugin.json`** — 插件清单，声明名称（`tuanzii`）、版本（`1.0.0`）和作者

项目无构建系统、测试框架或代码检查工具，是用于分发 Claude Code Skills 的脚手架。

## 添加 Skills

在 `.claude-plugin/skills/` 目录下以 Markdown 文件添加 Skills，遵循 Claude Code skill 格式。由于缓存符号链接直接指向源目录，新增或修改 skill 后无需重新安装插件。
