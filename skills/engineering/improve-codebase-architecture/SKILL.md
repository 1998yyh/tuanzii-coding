---
name: improve-codebase-architecture
description: 扫描代码库寻找深化（deepening）机会，以可视化 HTML 报告呈现候选方案，然后针对你选中的方案进行连环追问。当用户说“改进架构”、“架构评审”、“improve architecture”时触发。
disable-model-invocation: true
---

# 改进代码库架构

暴露架构上的摩擦点，提出**深化机会（deepening opportunities）**——把 shallow module 变成 deep module 的重构。目标是可测试性与 AI 可导航性。

本命令以项目的领域模型为依据，并建立在一套共享的设计词汇之上：

- 运行 `tuanzii:codebase-design` skill 获取架构词汇（**module**、**interface**、**depth**、**seam**、**adapter**、**leverage**、**locality**）及其原则（deletion test、“interface 即测试面”、“一个 adapter = 假想 seam，两个 = 真实 seam”）。在每条建议中严格使用这些术语——不要滑向 “component”、“service”、“API”、“boundary” 这类说法。
- `CONTEXT.md` 中的领域语言为好的 seam 提供了名字；`docs/adr/` 中的 ADR 记录了本命令不应重新争论的决策。

## 流程

### 1. 探索

**先圈定范围再扫描——YAGNI。** 深化一个 module 的回报在于让未来对它的改动更容易，所以要把额外权重放在近期频繁变动的代码区域。先看哪里，再决定怎么看：

- 如果用户指明了方向——某个 module、子系统或痛点——直接采用，跳过下面的推断。
- 否则，回溯一段足够长的提交历史（`git log --oneline`），找出代码库的热点——反复出现的文件和区域——让这些路径优先牵引你的注意力。如果改动很分散、没有明显热点，就扩大搜索面。

先读项目的领域词汇表（`CONTEXT.md`）和你要触碰区域内的所有 ADR。

然后派一个 sub-agent 走查代码库。不要机械套用固定启发式——自然地探索，记下你感到摩擦的地方：

- 哪里理解一个概念需要在许多小 module 之间来回跳转？
- 哪些 module 是 **shallow** 的——interface 几乎和实现一样复杂？
- 哪里为了可测试性抽出了纯函数，但真正的 bug 藏在它们的调用方式里（没有 **locality**）？
- 哪些紧耦合的 module 在跨越各自的 seam 泄漏？
- 代码库哪些部分没有测试，或者难以通过现有 interface 测试？

对任何你怀疑 shallow 的东西应用 **deletion test**：删掉它会让复杂度集中，还是仅仅挪了个位置？“是的，会集中”才是你要的信号。

### 2. 以 HTML 报告呈现候选方案

写一个自包含的 HTML 文件到操作系统临时目录，保证不往仓库里落任何东西。从 `$TMPDIR` 解析临时目录，回退到 `/tmp`（Windows 上是 `%TEMP%`），写到 `<tmpdir>/architecture-review-<timestamp>.html`，让每次运行都得到一个新文件。为用户打开它——Linux 上用 `xdg-open <path>`，macOS 上用 `open <path>`，Windows 上用 `start <path>`——并告知绝对路径。

报告使用 **CDN 引入的 Tailwind** 做布局与样式，在图/流程/时序能可靠表达结构的地方使用 **CDN 引入的 Mermaid**。把 Mermaid 与手工制作的 CSS/SVG 图示混用——当关系是图状结构（调用图、依赖、时序）时用 Mermaid；当你想要更偏编辑排版的东西（体量图、剖面图、塌缩动画）时用手工 div/SVG。每个候选方案都要有一个**前后对比可视化**。要视觉化。

每个候选方案渲染为一张卡片，包含：

- **Files**——涉及哪些文件/module
- **Problem**——为什么当前架构造成摩擦
- **Solution**——用平实语言描述会改变什么
- **Benefits**——用 locality 和 leverage 来解释，并说明测试会如何改善
- **Before / After 图**——并排、定制绘制，展示 shallowness 与深化后的样子
- **推荐强度**——`Strong`、`Worth exploring`、`Speculative` 之一，渲染为徽章

报告末尾放一个 **Top recommendation** 区块：你会先动手做哪个候选，以及为什么。

**领域用词取自 CONTEXT.md，架构用词取自 `tuanzii:codebase-design` 词汇表。** 如果 `CONTEXT.md` 定义了 “Order”，就说 “Order 接入 module”——而不是 “FooBarHandler”，也不是 “Order service”。

**ADR 冲突**：如果某个候选与现有 ADR 矛盾，只有当摩擦真实到值得重开这条 ADR 时才提出。在卡片里明确标注（例如一个警告 callout：_“与 ADR-0007 矛盾——但值得重开，因为……”_）。不要罗列 ADR 禁止的所有理论上的重构。

完整的 HTML 骨架、图示模式与样式指引见 [HTML-REPORT.md](HTML-REPORT.md)。

此时**不要**提出 interface 设计。文件写完后，问用户：“你想深入探索哪一个？”

### 3. 追问循环

用户选定候选后，运行 `tuanzii:grilling` skill，陪用户走完决策树——约束、依赖、深化后 module 的形状、seam 背后放什么、哪些测试得以保留。

副作用随决策成形就地发生——运行 `tuanzii:domain-modeling` skill，随时保持领域模型最新：

- **用 `CONTEXT.md` 里还没有的概念给深化后的 module 命名？** 把该术语加入 `CONTEXT.md`。文件不存在就顺手创建。
- **对话中把某个模糊术语打磨清楚了？** 当场更新 `CONTEXT.md`。
- **用户以一个承重的理由否决了候选？** 提议记录一条 ADR，话术如：_“要不要我把这个决定记成 ADR，免得以后的架构评审再次提出它？”_ 只有当理由真的会被未来的探索者用来避免重复建议时才提议——跳过临时性理由（“现在不值得做”）和不言自明的理由。
- **想为深化后的 module 探索备选 interface？** 运行 `tuanzii:codebase-design` skill，使用它的 design-it-twice 并行 sub-agent 模式。
