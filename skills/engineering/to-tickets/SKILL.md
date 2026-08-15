---
name: to-tickets
description: 把计划、spec 或当前对话拆成一组 tracer-bullet ticket，每张 ticket 声明自己的阻塞边并发布到配置好的 tracker —— 本地时每张 ticket 一个文件、以文字声明阻塞边，真实 tracker 上使用原生阻塞链接。当用户说"拆 ticket"、"拆分任务"、"to-tickets"时触发。
disable-model-invocation: true
---

# To Tickets

把计划、spec 或对话拆成一组 **ticket** —— tracer-bullet 式的垂直切片，每张声明哪些 ticket **阻塞** 它。

issue tracker 和 triage label 词汇表应该已经提供给你了 —— 如果没有，先运行 `tuanzii:setup-matt-pocock-skills`。

## 流程

### 1. 收集上下文

基于对话上下文中已有的内容工作。如果用户传了引用（spec 路径、issue 编号或 URL）作为参数，先获取它并读完正文和评论。

### 2. 探索代码库（可选）

如果还没探索过代码库，先探索以了解代码现状。ticket 的标题和描述应使用项目领域词汇表中的术语，并尊重你所触及领域的 ADR。

留意可以 prefactor（预重构）的机会，让后续实现更容易。"先让改动变得容易，再做那个容易的改动。"

### 3. 起草垂直切片

把工作拆成 **tracer bullet** ticket。

<vertical-slice-rules>

- 每个切片要穿过所有层（schema、API、UI、测试），窄但完整 —— 是垂直切片，不是某一层的水平切片
- 一个完成的切片可以独立演示或验证
- 每个切片的大小要能放进一个全新的上下文窗口
- 所有 prefactoring 都应先做

</vertical-slice-rules>

给每张 ticket 标注它的 **阻塞边** —— 必须先完成的其他 ticket。没有阻塞者的 ticket 可以立即开始。

**宽重构（wide refactor）是垂直切片的例外。** 宽重构指一次机械性改动 —— 改列名、改共享符号的类型 —— 其 **爆炸半径（blast radius）** 波及整个代码库，单次编辑会同时破坏成千上万个调用点，任何垂直切片都无法保持绿灯落地。不要硬塞进 tracer bullet；改用 **expand–contract**（先扩后收）排序。先 expand：新旧形态并存添加，什么都不破坏。然后按爆炸半径分批迁移调用点（按包、按目录），每批一张 ticket、都被 expand 阻塞，批与批之间保持 CI 绿灯，因为旧形态还在。最后 contract：确认没有调用方残留后删除旧形态，这张 ticket 被所有迁移批次阻塞。如果连分批都无法各自保持绿灯，顺序不变，但让它们共享一个集成分支，共同阻塞一张最终的"集成并验证"ticket —— 绿灯只在那里承诺。

### 4. 向用户提问确认

把提议的拆分方案以编号列表呈现。每张 ticket 展示：

- **标题**：简短的描述性名称
- **Blocked by**：必须先完成的其他 ticket（如有）
- **交付内容**：这张 ticket 打通的端到端行为

问用户：

- 粒度合适吗？（太粗 / 太细）
- 阻塞边对吗 —— 每张 ticket 是否只依赖真正卡住它的 ticket？
- 有没有 ticket 需要合并或进一步拆分？

迭代直到用户批准拆分方案。

### 5. 把 ticket 发布到配置好的 tracker

发布批准后的 ticket。**怎么发**取决于 `tuanzii:setup-matt-pocock-skills` 配置的 tracker —— ticket 内容不变，只是阻塞边的形态不同：

- **本地文件** → 在 `.scratch/<feature-slug>/issues/<NN>-<slug>.md` 下每张 ticket 写一个文件，从 `01` 开始按依赖顺序编号（阻塞者在前）。每个文件的 "Blocked by" 列出它依赖的编号/标题。使用下面的单 ticket 文件模板 —— 一张 ticket 一个文件，绝不合并成一个文件。
- **真实 issue tracker（GitHub、Linear 等）** → 按依赖顺序（阻塞者在前）每张 ticket 发一个 issue，让阻塞边能引用真实标识符。平台有原生阻塞 / 子 issue 关系就用原生的；否则在每张 ticket 的 "Blocked by" 里填阻塞它的 issue。除非另有指示，打上 `ready-for-agent` triage 标签 —— 这些 ticket 按构造就是 agent 可直接认领的。

从 **frontier（前沿）** 开始干活：所有阻塞者都已完成的 ticket。对于纯线性链条，就是从头到尾。

不要关闭或修改任何父 issue。

<local-ticket-template>

# <NN> — <Ticket 标题>

**要构建什么：** 这张 ticket 打通的端到端行为，从用户视角描述 —— 不是逐层的实现清单。

**Blocked by：** 卡住这张 ticket 的编号/标题，或"无 —— 可以立即开始"。

**Status:** ready-for-agent

- [ ] 验收标准 1
- [ ] 验收标准 2

</local-ticket-template>

<issue-template>

## 父 issue

指向 tracker 上父 issue 的引用（如果来源是已有 issue，否则省略本节）。

## 要构建什么

这张 ticket 打通的端到端行为，从用户视角描述 —— 不是逐层实现。

## 验收标准

- [ ] 标准 1
- [ ] 标准 2

## Blocked by

- 指向每张阻塞 ticket 的引用，或"无 —— 可以立即开始"。

</issue-template>

两种形态下都避免具体文件路径或代码片段 —— 它们很快就会过时。例外：如果 prototype 产出的某个片段比散文更能精确地表达一个决策（状态机、reducer、schema、类型形状），可以内联并简短注明它来自 prototype。只保留承载决策的关键部分 —— 不是可运行的 demo，只要要点。
