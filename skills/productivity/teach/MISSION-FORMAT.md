# MISSION.md 格式

`MISSION.md` 位于工作区根目录。它记录用户学习这个主题的_原因_。每一个教学决策——接下来教什么、推荐哪些资源、设计什么练习——都应该能回溯到这份文档。

## 模板

```md
# Mission: {Topic}

## Why
{1-3 sentences. The concrete real-world goal the user is chasing. What changes in their life or work when they have this skill? Avoid abstract framings like "to understand X" — push for the underlying outcome.}

## Success looks like
- {A specific, observable thing the user will be able to do}
- {Another specific thing}
- {…}

## Constraints
- {Time, budget, prior commitments, learning preferences, anything that bounds the approach}

## Out of scope
- {Adjacent topics the user explicitly does not want to chase right now — protects the zone of proximal development}
```

## 规则

- **一个工作区一个 mission。** 用户想学两件不相关的东西，那就是两个工作区。
- **具体优于抽象。** "十月前跑完半马"好过"变得更健康"。"给团队交付一个 Rust CLI"好过"学 Rust"。
- **对含糊要追问。** 如果用户说不清为什么，先访谈他们再动笔。一个糟糕的 mission 比没有 mission 更糟。
- **现实变了就修订。** mission 会变。用户的目标移动时，更新这份文件——不要留一个过期的 mission 继续指挥后续会话。
- **保持简短。** 如果 `MISSION.md` 超过一屏，它就不再是指南针，而变成了计划。
