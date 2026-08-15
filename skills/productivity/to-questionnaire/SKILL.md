---
name: to-questionnaire
description: 把一个你独自无法回答的决策变成一份问卷，交给掌握信息的对方填写。当用户说"问卷"、"帮我列问题"、"to-questionnaire"时触发。
disable-model-invocation: true
---

把用户独自回答不了的东西变成一份**问卷（questionnaire）**——一份 Markdown 文档，用户可以把它交给某一个人异步填写，或约一次会议一起填完。接收方掌握用户缺少的信息，问卷负责把这些信息从他们身上取出来。

**追问的是"寄送"，不是"主题"。** 只就_寄送_本身访谈用户——这是用户永远答得上来的：问卷发给谁、需要对方回答什么。文档里的问题则瞄准**缺口**：接收方知道的与用户需要的之间的差。

1. **发给谁？** 用一轮问答弄清接收方的角色、专长，以及与用户的关系。这决定问卷的语气和需要携带多少背景。完成标准：你知道接收方是谁，以及他们知道什么用户不知道的东西。

2. **需要拿回什么？** 用一轮问答弄清用户独自无法解决、需要从这个人这里获得的具体决策或事实。完成标准：你拿到一份具体清单——用户填完问卷后必须能做什么、或能决定什么。

3. **写问卷。** 针对第 1–2 步确定的缺口起草问题，遵循下面的文档结构。写到当前目录下的 `to-questionnaire-<slug>.md`（slug 取自主题），并报告文件路径。完成标准：文件已存在，且第 2 步中用户列出的每一项都有对应的问题覆盖。

## 文档结构

把文档定位为一份**情况摸底问卷（discovery questionnaire）**：用户缺少上下文，接收方握有上下文。问题按重要性从高到低排列——异步填写可能只有一次机会——问题超过一小把之后按主题用 `##` 标题分组。按下面的模板来写。

<questionnaire-template>

# <问卷标题>

**Purpose:** 这份问卷为什么存在，以及押在它上面的决策是什么。

**From:** <用户> — **To:** <接收方> — **How your answers will be used:** <答案的去向>

## Context

一段话，帮一个不在用户脑子里的接收方进入状态。够答好问题即可，不要写成一页纸。

## How to answer

截止时间和大致工作量。部分回答和"我不知道"同样有用——拿不准的地方请标出来，不要跳过。

## <主题标题>

每个主题一个 `## 小节`。小节内的问题按重要性从高到低排列。每个问题只问一件事——绝不复合提问——问题正下方留出作答占位，仅在问题可能被误读或容易招来敷衍回答时加一行 _why this matters_。

<question-example>
### What load is the system expected to handle at launch?

_Why this matters: it decides whether we provision for burst traffic now or defer it._

>
</question-example>

## Anything else?

收尾的兜底问题：还有什么我们没问、但我们应该知道的？

</questionnaire-template>
