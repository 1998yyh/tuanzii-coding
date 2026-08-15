---
name: domain-modeling
description: 构建并打磨项目的领域模型。当讨论代码库术语、编写或编辑 CONTEXT.md、记录或编辑 ADR 时使用。
---

# 领域建模（Domain Modeling）

在设计过程中主动构建并打磨项目的领域模型。这是一项*主动*的纪律——挑战术语、编造边界场景、在词汇表和决策成形的瞬间把它们写下来。（仅仅*阅读* `CONTEXT.md` 查词汇不算使用本 skill——那只是任何 skill 都该有的一行习惯。本 skill 用于你在*改动*模型时，而不是仅仅消费它时。）

## 文件结构

大多数仓库只有一个 context：

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

如果根目录存在 `CONTEXT-MAP.md`，说明仓库有多个 context。map 会指出每个 context 的位置：

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                          ← 系统级决策
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/                 ← 单个 context 的决策
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

文件按需懒创建——有东西可写时才建。如果没有 `CONTEXT.md`，在第一个术语被敲定时创建；如果没有 `docs/adr/`，在需要第一条 ADR 时创建。

## 会话期间

### 对照词汇表发起挑战

当用户使用的术语与 `CONTEXT.md` 中已有的语言冲突时，立即指出。"词汇表里 'cancellation' 定义为 X，但你的意思似乎是 Y——到底是哪个？"

### 打磨模糊用语

当用户使用含糊或多义的词时，提出一个精确的规范术语。"你说的是 'account'——指的是 Customer 还是 User？这是两个不同的东西。"

### 讨论具体场景

讨论领域关系时，用具体场景做压力测试。编造能探测边界的场景，逼用户把概念之间的界线说清楚。

### 与代码交叉验证

当用户陈述某事物如何工作时，检查代码是否与此一致。发现矛盾就摆出来："你的代码会取消整个 Order，但你刚才说可以部分取消——哪个是对的？"

### 就地更新 CONTEXT.md

术语一旦敲定，当场更新 `CONTEXT.md`。不要攒批——一边发生一边记录。格式见 [CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md)。

`CONTEXT.md` 必须完全不包含实现细节。不要把它当成规格说明、草稿纸或实现决策的仓库。它只是一本词汇表，别无他物。

### 有节制地提议 ADR

只有同时满足以下三条时，才提议创建 ADR：

1. **难以逆转**——日后改主意的代价是实打实的
2. **没有上下文会显得反常**——未来的读者会纳闷"当初为什么这么做？"
3. **源自真实的取舍**——确实存在过备选方案，你基于具体理由选了其一

缺任何一条，就跳过 ADR。格式见 [ADR-FORMAT.md](./ADR-FORMAT.md)。
