---
name: ask-matt
description: 不确定当前场景该用哪个 skill 或哪条流程时问它。本插件所有 skill 的路由器。当用户问"该用哪个 skill"、"流程怎么走"、"帮我路由"时触发。
disable-model-invocation: true
---

# Ask Matt

你记不住所有 skill，那就问。

一条**流程（flow）**是穿过若干 skill 的路径。大多数路径都跑在一条**主流程**上，另有两条**入口支线**汇入它。其余的 skill 要么独立使用，要么是运行在底层的词汇表。

## 主流程：想法 → 交付

大多数工作走的路线：你有一个想法，想把它做出来。

1. **tuanzii:grill-with-docs** — 用访谈把想法打磨清晰。只要你**在一个工作目录里干活**就从这里开始：它是有状态的，会把学到的东西留在 `CONTEXT.md` 和 ADR 里。（不在工作目录？用 tuanzii:grill-me —— 见「独立 skill」。两者跑的都是同一个 tuanzii:grilling 原语；grill-with-docs 是会留下书面记录的那个，只要有仓库可写，它就是两者中更好的选择。）
2. **分支 —— 所有问题都能在对话里敲定吗？** 如果某个问题需要一个能跑起来的答案（状态、业务逻辑、必须亲眼看到的 UI），就绕道做一个 prototype，两个方向都用 **tuanzii:handoff** 衔接（prototype 生活在独立目录里，这正是 handoff 的用途 —— 见「阶段边界」）：
   - 用 **tuanzii:handoff** 交出去，然后针对该文件开一个全新会话，
   - 用 **tuanzii:prototype** 写一次性代码回答这个问题，
   - 再用 **tuanzii:handoff** 把结论带回来，并在原想法的主线里引用它。
3. **分支 —— 这是一个跨会话的大型构建吗？**
   - **是** → **tuanzii:to-spec**（把对话整理成 spec），然后 **tuanzii:to-tickets** 把它拆成 tracer-bullet 式的 ticket，每张 ticket 声明自己的**阻塞边（blocking edges）**。本地 tracker 下就是 `.scratch/<feature>/issues/` 目录里一 ticket 一文件、手工按阻塞优先推进；真实 tracker 下阻塞边会变成原生 blocking 链接，任何阻塞已清的 ticket 都可以直接领走 —— 每张 ticket 各起一个 **tuanzii:implement**，两张之间 `/clear` 上下文。每张 ticket 都是自包含的，上一张的上下文用完即弃。
   - **否** → 就在当前上下文窗口里直接 **tuanzii:implement**。

   无论走哪条，**tuanzii:implement** 都会在内部驱动 **tuanzii:tdd** 来构建每个 issue —— 一次一个 red-green 切片 —— 提交前再跑 **tuanzii:code-review** 收尾，对 diff 做双轴评审（Standards + Spec）。只想对某个具体行为做测试先行、不需要完整 spec 时，单独使用 **tuanzii:tdd**；想对照某个固定点评审一个分支或 PR 时，单独使用 **tuanzii:code-review**。

### 上下文卫生

第 1–3 步保持在**同一个不中断的上下文窗口**里 —— 在 tuanzii:to-tickets 之前不要 compact 也不要 clear —— 这样追问、spec、ticket 全部建立在同一套思考之上。之后每个 tuanzii:implement 都全新启动，只从 ticket 出发。

这条规则的上限是 **smart zone**：模型仍能保持清晰推理的上下文窗口（当前顶级模型约 150k token）。如果会话在到达 tuanzii:to-tickets 之前就逼近这个上限，不要带着退化的上下文硬撑 —— 在最近的阶段边界处 `/compact`，然后继续（见「阶段边界」）。

## 入口支线

一种会产生工作的起始局面，随后汇入主流程。

- **bug 和需求堆积如山** → **tuanzii:triage**。它让 issue 经过分诊角色流转，产出 agent 可直接执行的 issue，之后由 **tuanzii:implement** 领走。

  分诊只适用于**不是你创建的** issue —— bug 报告、外部进来的需求、任何原始抵达的东西。tuanzii:to-tickets 产出的 ticket 已经是 agent-ready 的，**不要对它们做分诊**。

- **有东西坏了** → **tuanzii:diagnosing-bugs**。专治硬骨头：第一眼看不穿的 bug、时有时无的 flake、在两个已知良好状态之间潜入的回归。在拿到**紧凑反馈回路**（一条已经能因*这个* bug 变红的命令）之前，它拒绝做任何理论推测；修复时附带回归测试。当事后复盘的真正结论是"没有好的 seam 可以锁住这个 bug"时，它会交接给 **tuanzii:improve-codebase-architecture**。

- **庞大而模糊的工作 —— 全新项目或超大特性，一个会话装不下** → **tuanzii:wayfinder**，这里认知负荷最高的一条流程。当从这里到目的地的路还看不见时，它在 issue tracker 上绘制一张由**决策 ticket** 组成的**共享地图**，然后逐个解决 —— 产出的是**决策，不是交付物** —— 直到迷雾被推开、道路清晰。tuanzii:grill-with-docs 打磨的是一个会话能装下的想法，wayfinder 对付的是装不下的 —— 它更慢、更重，所以只留给这种场景，界限清晰的特性永远不要用它。

  地图清晰后，**它交接，而不是直接开建**：在 **tuanzii:to-spec** 处汇入主流程，由它把地图上互链的决策收敛成可构建的计划，然后照常走 tuanzii:to-tickets 和 tuanzii:implement。把地图直接接进 tuanzii:implement 会跳过这个收敛、丢掉互链的细节 —— 只有当工作量最后证明确实很小时，才直接进 tuanzii:implement。

## 代码库健康

不是特性开发 —— 是保养。

- **tuanzii:improve-codebase-architecture** —— 一有空就跑，让代码库始终适合 agent 在其中工作。它浮现**深化机会（deepening opportunities）**；选中一个就会*产生一个想法*，你可以带着它从 tuanzii:grill-with-docs 进入主流程。它是负责普查、找出候选的那个；**tuanzii:codebase-design**（见下）是你对中选者做设计的工作台。

## 底层词汇表

两个 model-invoked 的参考 skill，运行在其他 skill *之下* —— 各自是其词汇的唯一事实来源。当问题出在**词语**而非流程上时直接使用它们；否则让上面的 skill 自行引入。

- **tuanzii:domain-modeling** —— 打磨项目的*领域*语言：挑战模糊术语、消解一词多义（"account" 干着三份活）、把难以逆转的决策记成 ADR。tuanzii:grill-with-docs 正是靠它让 `CONTEXT.md` 保持为一份干净的词汇表。
- **tuanzii:codebase-design** —— deep module 词汇表（module、interface、depth、seam、adapter、leverage、locality），用于设计模块的*形状*：小接口、大量行为、干净的 seam。tuanzii:tdd 和 tuanzii:improve-codebase-architecture 都说这套语言。

## 阶段边界

一个**阶段（phase）**是会话内的一段工作 —— 追问、实现、QA。在两个阶段之间的**边界**上，你有五个选项，而如何取舍是整张地图里最模糊的决策：

- **继续（Continue）** —— 留在原地。零成本，零损失。
- **`/clear`** —— 清空窗口，当这里的一切对下一步都无关紧要时。
- **tuanzii:handoff** —— 写一份可携带的 markdown 文件。用途很窄：只在**换 harness**、**换目录**、**交给同事**，或在**阶段中途**分叉出一个支线任务时用。它买到的是可携带性。
- **Subagent** —— 把一个范围收紧的任务派到独立窗口，拿回一份报告。
- **`/compact`** —— 压缩当前上下文，用它来启动新会话。是**默认项**，位于决策树底部，而不是第一选择。

阅读 [PHASE-BOUNDARIES.md](PHASE-BOUNDARIES.md) 查看有序决策树 —— 五个问题、每个分支背后的推理，以及为什么 primary source 的代价让**继续**成为第一个要排除的选项。决策要**在**边界上做；阶段中途，要么继续，要么把剩余工作拆给 subagent。

## 独立 skill

完全不在主流程上。

- **tuanzii:grill-me** —— 与 tuanzii:grill-with-docs 相同的连环追问访谈，但**无状态**：本地不保存任何东西，也不构建 `CONTEXT.md`。当你**不在工作目录里**时使用 —— 打磨计划、设计、文稿，任何底下没有仓库的东西。如果你在工作目录里，改用 tuanzii:grill-with-docs：同样的访谈，还会留下书面记录，严格更优。
- **tuanzii:grilling** —— 访谈原语本身：轮次、知识边界（frontier）、事实是 agent 的活、决策是你的。tuanzii:grill-me 和 tuanzii:grill-with-docs 是两个命名入口，tuanzii:triage、tuanzii:wayfinder 和 tuanzii:improve-codebase-architecture 也都在内部运行它。只有当你想要不带任何外壳的裸访谈时才直接使用。
- **tuanzii:resolving-merge-conflicts** —— 逐 hunk 处理进行中的 merge 或 rebase 冲突，按**意图**（追溯到每一侧的 primary source）而不是按选行来解决，然后完成这次操作。它永不执行 `--abort`。独立、不属于任何流程：已经身在冲突中时再用它。
- **tuanzii:prototype** —— 一个回答单一设计问题的一次性小程序：这个状态模型手感对吗，这个 UI 该长什么样。"一次性"约束的是代码的写法，不是必须销毁的承诺：结论折叠进正式代码，prototype 本身作为 **primary source** 保留在 main 之外的 `prototype/<name>` 分支上，并在实现 issue 中指向它。它是主流程第 2 步的绕道，但任何时候遇到纸面上难以敲定的设计问题都可以用它。
- **tuanzii:research** —— 把阅读跑腿活委托给**后台 agent**：它对照 **primary source** 调查一个问题，然后在仓库里留下一份带引用的 Markdown 文件。它读它的，你继续干你的。产出的文件是带进主流程 tuanzii:grill-with-docs 的素材 —— 研究喂养思考，不替代思考。
- **tuanzii:to-questionnaire** —— 当阻塞你的东西既不在你脑里也不在代码库里、而在**别人脑里**时，它替你写一份问卷发给对方填。它是 tuanzii:grill-me 的反面：不是围绕主题访谈你，而是围绕**这次发送**访谈你 —— 发给谁、你需要拿回什么 —— 并让问题瞄准缺口。收回来的东西是 tuanzii:grill-with-docs 或 tuanzii:to-spec 的素材。
- **tuanzii:wizard** —— 处理只有**人类**才能做的步骤：开通基础设施、配置凭据或 CI secret、在不熟悉的第三方后台里点来点去、跑一次性的迁移或切换。它生成一个交互式 bash 脚本，逐个打开 URL、捕获每个值、写入 `.env` 和 GitHub secrets —— 让这类流程不再是每次都要重新向 agent 解释一遍的东西。model-invoked，agent 一撞到只有你能通过的墙就会找到它。如果 agent 自己能做，就让它自己做；这个 skill 只留给真正需要人类在环的场景。
- **tuanzii:wait-what** —— 针对"刚才那条消息没看懂"的纠正器。在任何其他 skill 的会话中途使用，agent 会用平实的语言、带上你缺的背景、`CONTEXT.md` 的词汇，把刚才说的东西重新讲一遍。它是事后补救；tuanzii:grill-with-docs 是事前预防，因为早早达成共同语言才能从源头挡住黑话。
- **tuanzii:teach** —— 跨多个会话学习一个概念，把当前目录当作有状态的工作区。
- **tuanzii:writing-for-agents** —— 编写面向 agent 的文档（skill、AGENTS.md、被引用的文档）时的参考。

## 前置条件

**tuanzii:setup-matt-pocock-skills** —— 在第一次跑工程流程之前运行，配置其他 skill 所假设的 issue tracker、分诊标签和文档布局。自定义 issue tracker 同样支持。
