# 领域文档

工程 skills 在探索代码库时，应如何消费本仓库的领域文档。

## 探索之前，先读这些

- 仓库根目录的 **`CONTEXT.md`**，或者
- 如果根目录存在 **`CONTEXT-MAP.md`**——它指向每个上下文各自的 `CONTEXT.md`，读取与当前主题相关的那些。
- **`docs/adr/`** —— 阅读与你即将改动的区域相关的 ADR。多上下文仓库中，还要查看 `src/<context>/docs/adr/` 里上下文级别的决策。

如果上述文件不存在，**静默继续**。不要指出它们缺失，也不要建议预先创建。`tuanzii:domain-modeling` skill（可通过 `tuanzii:grill-with-docs` 和 `tuanzii:improve-codebase-architecture` 触达）会在术语或决策真正敲定时惰性创建它们。

## 文件结构

单上下文仓库（绝大多数仓库）：

```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

多上下文仓库（根目录存在 `CONTEXT-MAP.md`）：

```
/
├── CONTEXT-MAP.md
├── docs/adr/                          ← 系统级决策
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/                  ← 上下文级决策
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

## 使用词汇表中的术语

当你的输出命名一个领域概念时（在 issue 标题、重构提案、假设、测试名中），使用 `CONTEXT.md` 中定义的术语。不要漂移为词汇表明确避用的同义词。

如果你需要的概念还不在词汇表里，这是一个信号——要么你在发明项目并不使用的语言（重新考虑），要么确实存在空白（记下来交给 `tuanzii:domain-modeling`）。

## 标出 ADR 冲突

如果你的输出与某条现有 ADR 相矛盾，显式指出，不要静默覆盖：

> _与 ADR-0007（event-sourced orders）矛盾——但值得重新讨论，因为……_
