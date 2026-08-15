# Out-of-Scope 知识库

仓库中的 `.out-of-scope/` 目录用于持久记录被拒绝的功能请求。它有两个用途：

1. **组织记忆** —— 记录一个功能为什么被拒绝，让推理过程不随 issue 关闭而丢失
2. **去重** —— 当新 issue 与历史拒绝匹配时，skill 可以浮现之前的决定，而不是重新争论一遍

## 目录结构

```
.out-of-scope/
├── dark-mode.md
├── plugin-system.md
└── graphql-api.md
```

每个 **概念** 一个文件，不是每个 issue 一个文件。多个请求同一件事的 issue 归到同一个文件下。

## 文件格式

文件应以轻松、可读的风格书写 —— 更像一篇短设计文档，而不是数据库条目。使用段落、代码示例和例子，让第一次读到它的人也能清楚理解推理过程。

```markdown
# Dark Mode

This project does not support dark mode or user-facing theming.

## Why this is out of scope

The rendering pipeline assumes a single color palette defined in
`ThemeConfig`. Supporting multiple themes would require:

- A theme context provider wrapping the entire component tree
- Per-component theme-aware style resolution
- A persistence layer for user theme preferences

This is a significant architectural change that doesn't align with the
project's focus on content authoring. Theming is a concern for downstream
consumers who embed or redistribute the output.

```ts
// The current ThemeConfig interface is not designed for runtime switching:
interface ThemeConfig {
  colors: ColorPalette; // single palette, resolved at build time
  fonts: FontStack;
}
```

## Prior requests

- #42 — "Add dark mode support"
- #87 — "Night theme for accessibility"
- #134 — "Dark theme option"
```

### 命名文件

用简短、描述性的 kebab-case 概念名：`dark-mode.md`、`plugin-system.md`、`graphql-api.md`。名字应当让人浏览目录时不打开文件也能明白被拒绝的是什么。

### 撰写理由

理由必须有实质内容 —— 不是"我们不想要这个"，而是为什么。好的理由会引用：

- 项目范围或理念（"本项目专注于 X；主题化是下游消费方的事"）
- 技术约束（"支持它需要 Y，这与我们的 Z 架构冲突"）
- 战略决策（"我们选择 A 而不是 B，因为……"）

理由应当耐久。避免引用临时性情况（"我们现在太忙了"）—— 那不是真正的拒绝，只是推迟。

## 何时检查 `.out-of-scope/`

triage 期间（第 1 步：收集上下文），读 `.out-of-scope/` 下的所有文件。评估新 issue 时：

- 检查请求是否匹配已有的 out-of-scope 概念
- 匹配按概念相似度，不按关键词 —— "night theme" 匹配 `dark-mode.md`
- 如果有匹配，浮现给维护者："这与 `.out-of-scope/dark-mode.md` 相似 —— 我们之前因为 [理由] 拒绝过。你仍然这么认为吗？"

维护者可以：

- **确认** —— 新 issue 追加到已有文件的 "Prior requests" 列表，然后关闭
- **重新考虑** —— 删除或更新该 out-of-scope 文件，issue 走正常 triage 流程
- **不同意** —— 两者相关但不同，走正常 triage 流程

## 何时写入 `.out-of-scope/`

仅当一个 **enhancement**（不是 bug）被拒绝为 `wontfix` 时。enhancement PR 与 issue 完全同规则 —— 被拒绝的 PR 记录在这里，同一个请求才不会以新代码的形式卷土重来。

当某件事因为 **已实现** 而被关闭为 `wontfix` 时，**不要** 写在这里。那是已建成的功能，不是被拒绝的；记录它会用假拒绝污染去重检查。这种情况的关闭评论应指向该功能已经存在的位置。

流程：

1. 维护者判定某功能请求超出范围
2. 检查是否已有匹配的 `.out-of-scope/` 文件
3. 有：把新 issue 追加到 "Prior requests" 列表
4. 没有：新建文件，包含概念名、决定、理由和第一条历史请求
5. 在 issue 上发评论解释决定并提及该 `.out-of-scope/` 文件
6. 以 `wontfix` 标签关闭 issue

## 更新或删除 out-of-scope 文件

如果维护者对之前拒绝过的概念改变主意：

- 删除对应的 `.out-of-scope/` 文件
- skill 不需要重开旧 issue —— 它们是历史记录
- 触发这次重新考虑的新 issue 走正常 triage 流程
