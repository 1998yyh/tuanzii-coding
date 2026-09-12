---
name: grill-with-docs
description: 对计划或设计进行刨根问底的连环追问，并在追问过程中同步沉淀文档（ADR 与词汇表）。当用户说"追问并记录"、"grill"且需要落文档时使用。
disable-model-invocation: true
---

通过宿主的技能加载机制分别调用 `tuanzii:grilling` 与 `tuanzii:domain-modeling`，每个 skill 单独加载。按前者运行追问会话，按后者同步维护领域词汇与 ADR。
