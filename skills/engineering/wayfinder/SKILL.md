---
name: wayfinder
description: 规划一大块超出单个 agent 会话容量的工作 —— 在 issue tracker 上以"决策 ticket 共享地图"的形式组织，然后逐张消解，直到通往目标的路径清晰。当用户说"wayfinder"、"绘制地图"、"规划大型工作"时触发。
disable-model-invocation: true
---

一个模糊的想法出现了 —— 大到单个 agent 会话装不下，而且笼罩在迷雾中：从这里到 **终点（destination）** 的路还看不见。Wayfinding 的目的是找到那条路，而不是直接向终点冲锋。本 skill 把这条路绘制成仓库 issue tracker 上的一张 **共享地图**，然后逐张处理它的 **决策 ticket** —— 消解结果为"一个决定"的问题，而不是要执行的构建切片 —— 直到路线清晰。

终点因任务而异，命名终点是绘图的第一个动作 —— 它塑造每张 ticket。终点可能是要交付并迭代的 spec、规划开始前要锁定的决定，或就地完成的改动（比如数据结构迁移）。地图是领域无关的 —— 工程工作、课程内容，任何符合这个形状的东西都行。

## 规划，而非执行

Wayfinder 默认是 **规划**：每张 ticket 消解一个决定，当道路清晰时地图就完成了 —— 在有人去真正执行之前，没有剩下要决定的事。"干脆直接把活干了"的冲动通常就是信号：你已经到达地图边缘，该交棒了。任务可以在自己的 **Notes** 里推翻这一点 —— 把执行纳入地图本身 —— 但没有这种声明时，产出决定，不产出交付物。

## 以名字引用

每张地图和 ticket 都是一个 issue，所以它有一个 **名字** —— 它的标题。在一切给人看的输出中 —— 叙述、地图的 Decisions-so-far —— 用名字引用它，绝不用裸 id、编号或 slug。一面 `#42, #43, #44` 的墙根本没法读；名字一目了然。id 和 URL 不会消失 —— 名字包裹链接 —— 但它们藏在名字 _里面_，绝不取而代之。

## 地图

地图是仓库 issue tracker 上的单个 issue，标签为 `wayfinder:map` —— 它是权威产物。它的 ticket 是地图的子 issue。

地图是 **索引**，不是仓库。它列出已做的决定并指向持有细节的 ticket；一个决定只存在于一个地方 —— 它的 ticket —— 所以地图从不复述，只做一行摘要并链接。

**地图、子 ticket、阻塞关系和 frontier 查询在物理上放在哪里是 tracker 相关的。** issue tracker 应该已经提供给你了 —— 如果没有，先运行 `tuanzii:setup-matt-pocock-skills`。查 tracker 文档的 "Wayfinding operations" 一节，了解 _本_ 仓库如何表达这些概念。如果没有提供 tracker，默认使用本地 markdown tracker。

### 地图正文

整张地图的低分辨率视图，每个会话加载一次。未完成的 ticket **不** 列在其中 —— 它们是开放的子 issue，通过查询找到。

```markdown
## Destination

<到达这张地图的终点是什么样子 —— 本任务要找到的那份 spec、那个决定或那项改动。一两行；每个会话在选择 ticket 之前先据此定向。>

## Notes

<领域；每个会话都应查阅的 skill；本任务的长期偏好>

## Decisions so far

<!-- 索引 —— 每张已关闭 ticket 一行：足以判断相关性，然后点链接放大查看 ticket 持有的细节 -->

- [<已关闭 ticket 标题>](链接) —— <答案的一行摘要>

## Not yet specified

<!-- 见"战争迷雾"：在范围内但还不能写成 ticket 的迷雾；随 frontier 推进而毕业 -->

## Out of scope

<!-- 见"范围之外"：被判定超出终点的工作；已关闭，永不毕业 -->
```

### Ticket

每张 ticket 是地图的一个 **子 issue**；tracker 的 issue id 就是它的身份。正文是那个问题，大小以一次 100K token 的 agent 会话为限：

```markdown
## Question

<这张 ticket 要消解的决定或调查>
```

每张 ticket 携带一个 `wayfinder:<type>` 标签 —— `research`、`prototype`、`grilling`、`task` 之一（见 [Ticket 类型](#ticket-类型)）。

会话通过把 ticket **指派** 给驱动地图的开发者来 **认领** 它，**最先** 做这件事，早于任何工作，这样并发会话会跳过它。这个 assignee _就是_ 认领：开放的、未指派的 ticket 即未认领。

阻塞使用 tracker 的 **原生** 依赖关系 —— 这很关键，因为它让 frontier 在 tracker 自己的 UI 里 _可视化_ 呈现，人类不用打开地图就能看到什么可以拿。只有缺少原生阻塞能力的 tracker 才退回正文约定。当阻塞一张 ticket 的所有 ticket 都关闭时，它就是 **unblocked**；**frontier** 是开放的、unblocked、未认领的子 ticket —— 已知世界的边缘。

答案不属于正文 —— 它在消解时记录（见 [在地图上推进](#在地图上推进)）。消解 ticket 过程中产生的资产以链接形式挂在 issue 上，不粘贴进去。

## Ticket 类型

每张 ticket 要么是 **HITL** —— human in the loop，与能为自己发言的人类 _一起_ 推进 —— 要么是 **AFK**，由 agent 独自驱动。HITL ticket 只能通过这种实时交流消解；agent 绝不代替人类那一边（自问自答的 grilling agent 就破坏了这一点）。

- **Research**（AFK）：阅读文档、第三方 API 或本地资源（如知识库），挖出一个决定所等待的事实。由 `tuanzii:research` **子 agent** 消解。当需要当前工作目录之外的知识时使用。
- **Prototype**（HITL）：通过做一个便宜、粗糙、具体的可讨论 artifact 来提高讨论的真实度 —— 大纲、粗略初稿、stub，或通过 tuanzii:prototype skill 做的 UI/逻辑代码。把 prototype 作为资产链接上来。当关键问题是"它应该长什么样"或"它应该怎么表现"时使用。
- **Grilling**（HITL）：对话。默认情形。总是调用 `tuanzii:grilling` 和 `tuanzii:domain-modeling` skill。
- **Task**（HITL 或 AFK）：必须先完成、才能做出某个 _决定_ 的手工工作 —— 没什么可决定、可原型、可研究的，但讨论被它卡住。注册某个服务以便评估它的 API、开通访问权限、搬运数据以便看清它的形状。这是唯一 _做事_ 而非 _做决定_ 的类型 —— 它靠解锁一个决定赢得自己的位置，而不是靠交付终点。agent 能做就独自驱动（AFK）；否则给人类一份精确的清单（HITL）。工作完成即消解；答案记录做了什么以及后续 ticket 依赖的事实（凭据位置、新 URL、行数）。

## 战争迷雾

地图是 _刻意_ 不完整的：看不见的东西不要画。在活跃 ticket 之外是 **战争迷雾（fog of war）** —— 你能感觉到会到来、但还无法钉死的决定和调查的模糊景象，因为它们挂在仍未开放的问题上。消解一张 ticket 会清开它前方的迷雾，让现在可以说清的东西毕业成新 ticket —— 一次一张，直到通往终点的路清晰、不再有 ticket 剩余。

地图的 **Not yet specified** 一节就是写下这种模糊景象的地方：疑似的问题、以后要回访的区域。它是 _朝向_ 终点的未探索 frontier —— 这里的一切都在范围内，只是还不够清晰、写不成 ticket。能写多细写多细；它也兼任给协作者看的路标，指示任务的走向。

**迷雾还是 ticket？** 检验标准是你现在能否精确陈述这个问题 —— _不是_ 你现在能否回答它。

- 问题已经清晰时 **写成 ticket** —— 即使它被阻塞、你还不能动手。
- 还无法精确表述时放进 **Not yet specified**。不要预先把迷雾切成 ticket 大小的块：它比 ticket 粗，一片迷雾在 frontier 到达时可能毕业成好几张 ticket，也可能一张都没有。

**Not yet specified** 排除已决定的（Decisions so far）、已是活跃 ticket 的，以及超出范围的（下一节）。

## 范围之外

迷雾只会 _朝向_ 终点聚集。终点固定了范围，所以超出它的工作是 **out of scope** —— 它不是迷雾，也不属于 **Not yet specified**。它在地图上有自己的 **Out of scope** 一节：你有意识地排除出 _本次_ 任务的工作。把它放到这里的是范围，不是清晰度。

Out-of-scope 的工作永不毕业 —— frontier 止于终点 —— 所以它只有在终点被重绘时才会回来，而且那是作为一次新任务，不是恢复旧任务。

把某物判定为超出范围是一个定界动作，不是路线上的一步。当一张已存在的 ticket 被发现位于终点之外 —— 绘图时误圈进来的，或被某次消解暴露的 —— **关闭它**（关闭的 ticket 明确地离开 frontier），并在 **Out of scope** 一节留一行：摘要加为什么超出范围，链接那张已关闭的 ticket。它不进 **Decisions so far** —— 那里记录的是实际走过的路线，范围边界不是路线上的一步。

## 调用方式

两种模式。无论哪种，**每个会话最多消解一张 ticket** —— research ticket 除外。

### 绘制地图

用户带着一个模糊的想法调用。

1. **命名终点。** 运行一轮 `tuanzii:grilling` 和 `tuanzii:domain-modeling` 会话，钉死这张地图要找到什么 —— 那份 spec、那个决定或那项改动。终点固定范围，所以最先定。
2. **测绘 frontier。** 再追问一轮，这次是 **广度优先**：扇形扫过整个空间，而不是在单条线上深挖，浮现开放的决定和现在就能迈出的第一步。**如果这没有浮现任何迷雾** —— 通往终点的路已经清晰，整个旅程小到一次会话装得下 —— 你不需要地图。停下来问用户想怎么进行。
3. **创建地图**（标签 `wayfinder:map`）：填好 Destination 和 Notes，Decisions-so-far 为空，迷雾草写进 **Not yet specified**。
4. **创建现在就能说清的 ticket**，作为地图的子 issue —— 然后在 **第二遍** 中接好阻塞边（issue 需要先有 id 才能互相引用）。接线把它们分成 frontier 和被阻塞两类；一切还说不清的东西留在迷雾里 —— **Not yet specified** 一节。
5. **放出 research 子 agent。** 对刚创建的每张 `research` ticket，启动一个 `tuanzii:research` 子 agent 并行消解它，把发现记录在一次性的 `research/<name>` 分支上，并从 ticket 给出上下文指针。
6. 停下 —— 绘图就是这一个会话的工作；它亲手不消解任何 ticket。

### 在地图上推进

用户带着一张地图（URL 或编号）调用。ticket 是 **可选的** —— 没指定时，由你而不是用户挑下一个决定。

1. 加载 **地图** —— 低分辨率视图，不是每张 ticket 的正文。
2. 选择 ticket。用户点名了就用点名的；否则按顺序取第一张 frontier ticket。**认领它**：在任何工作之前先指派给自己。
3. 消解它 —— **按需放大**：临时拉取任何相关或已关闭 ticket 的完整正文；调用 `## Notes` 块点名的 skill。拿不准时用 `tuanzii:grilling` 和 `tuanzii:domain-modeling`。
4. 记录消解结果：把答案作为 **resolution 评论** 发出，**关闭** issue，并向地图的 Decisions-so-far **追加一条上下文指针**。
5. 添加新浮现的 ticket（先创建、后接线）；把答案已经说清的迷雾毕业，每毕业一片就从 **Not yet specified** 中清除它，让它只以新 ticket 的形式存在。如果答案显示某张 ticket —— 这张或另一张 —— 位于终点之外，**把它判定为超出范围**，而不是在路线上消解它。如果这个决定推翻了地图的其他部分，更新或删除那些 ticket。

用户可能并行推进多张 unblocked ticket，所以预期会有其他会话在并发编辑 tracker。
