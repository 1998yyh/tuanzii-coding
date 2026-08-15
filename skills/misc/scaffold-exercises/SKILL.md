---
name: scaffold-exercises
description: 创建包含 section、problem、solution、explainer 且能通过 lint 校验的练习目录结构。当用户想做练习脚手架、创建练习占位（exercise stubs）、搭建课程练习或新增课程章节时使用。
---

# 练习脚手架

创建能通过 `pnpm ai-hero-cli internal lint` 校验的练习目录结构，然后用 `git commit` 提交。

## 目录命名

- **章节（Section）**：`exercises/` 下的 `XX-section-name/`（如 `01-retrieval-skill-building`）
- **练习（Exercise）**：章节内的 `XX.YY-exercise-name/`（如 `01.03-retrieval-with-bm25`）
- 章节号为 `XX`，练习号为 `XX.YY`
- 名称一律使用 dash-case（小写加连字符）

## 练习变体

每个练习至少包含以下子目录之一：

- `problem/` —— 学员工作区，含 TODO
- `solution/` —— 参考实现
- `explainer/` —— 概念讲解材料，无 TODO

搭占位（stub）时，除非计划中另有说明，默认使用 `explainer/`。

## 必需文件

每个子目录（`problem/`、`solution/`、`explainer/`）都需要一个 `readme.md`，要求：

- **不能为空**（必须有实际内容，哪怕只有一行标题）
- 不能有失效链接

搭占位时，创建一个只含标题和描述的最小 readme：

```md
# Exercise Title

Description here
```

如果子目录包含代码，还需要一个 `main.ts`（超过 1 行）。但纯占位的练习只有 readme 即可。

## 工作流程

1. **解析计划** —— 提取章节名、练习名和变体类型
2. **创建目录** —— 对每个路径执行 `mkdir -p`
3. **创建占位 readme** —— 每个变体目录一个 `readme.md`，带上标题
4. **运行 lint** —— 用 `pnpm ai-hero-cli internal lint` 校验
5. **修复报错** —— 迭代直到 lint 通过

## lint 规则摘要

linter（`pnpm ai-hero-cli internal lint`）检查以下内容：

- 每个练习都有子目录（`problem/`、`solution/`、`explainer/`）
- `problem/`、`explainer/` 或 `explainer.1/` 至少存在一个
- 主要子目录中 `readme.md` 存在且非空
- 不允许 `.gitkeep` 文件
- 不允许 `speaker-notes.md` 文件
- readme 中不能有失效链接
- readme 中不能出现 `pnpm run exercise` 命令
- 每个子目录都需要 `main.ts`，除非它是纯 readme 形式

## 移动/重命名练习

重新编号或移动练习时：

1. 使用 `git mv`（而非 `mv`）重命名目录 —— 保留 git 历史
2. 更新数字前缀以保持顺序
3. 移动后重新运行 lint

示例：

```bash
git mv exercises/01-retrieval/01.03-embeddings exercises/01-retrieval/01.04-embeddings
```

## 示例：根据计划搭占位

给定如下计划：

```
Section 05: Memory Skill Building
- 05.01 Introduction to Memory
- 05.02 Short-term Memory (explainer + problem + solution)
- 05.03 Long-term Memory
```

创建：

```bash
mkdir -p exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer
mkdir -p exercises/05-memory-skill-building/05.02-short-term-memory/{explainer,problem,solution}
mkdir -p exercises/05-memory-skill-building/05.03-long-term-memory/explainer
```

然后创建占位 readme：

```
exercises/05-memory-skill-building/05.01-introduction-to-memory/explainer/readme.md -> "# Introduction to Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/explainer/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/problem/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.02-short-term-memory/solution/readme.md -> "# Short-term Memory"
exercises/05-memory-skill-building/05.03-long-term-memory/explainer/readme.md -> "# Long-term Memory"
```
