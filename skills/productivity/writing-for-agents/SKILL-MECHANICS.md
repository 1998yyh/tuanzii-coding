# Skill 机制

本文档是 [`tuanzii:writing-for-agents`](SKILL.md) 的 skill 专属分支：当文档是一个 skill 时有哪些不同——frontmatter、调用方式的选择，以及路由 skill（router skill）。写法的其他部分见 `SKILL.md` 里的通用参考。

## 调用方式（Invocation）

两种选择，在两种负载之间做取舍：

- **model-invoked** skill 保留 `description`，agent 可以自主触发它——其他 skill 也能触达它。你仍然可以手敲它的名字：model-invocation 永远_包含_用户的触达；description 只会增加 agent 的发现能力，从不会移除人的。description 是这个 skill 的顶层上下文指针，被迫常驻加载——用永久的上下文负载换可发现性。一个内容全是参考的 model-invoked skill 也是共享参考的一个家：别的 skill 可以调用它，多个 skill 都需要的参考就有了单一存放处。机制：不要设置 `disable-model-invocation`，并写一个面向模型的 description，携带各触发分支（`SKILL.md` 里的指针写作规则全部适用）。
- **user-invoked** skill 把 description 移出 agent 的触达范围：只有人敲它的名字才能调用，其他 skill 都不行。上下文负载为零，但花认知负载——你自己就是那个必须记住它存在的索引。机制：设置 `disable-model-invocation: true`；此时 `description` 变成面向人的——一行摘要，触发词列表全部去掉。

只在 agent 必须自主触达这个 skill、或其他 skill 必须触达它时，才选 model-invocation。如果它永远只被手动触发，就做成 user-invoked，不付任何上下文负载。

两个 user-invoked skill 都需要的共享参考，放不进任何一个里——没有 description，彼此都无法触发对方。把它推到 skill 系统之外的普通文件里：任何 skill 都能指向的外部参考。

## 按调用拆分

拆分中的"按调用"这一刀（"按顺序"那一刀在 `SKILL.md` 里）：当你有一个应当独立触发它的引导词——一个你在 prompt 里真正会用的触发词——或另一个 skill 必须触达它时，拆出一个 model-invoked skill。你要为新的常驻 description 支付上下文负载，所以这份独立触达必须值回票价。

## 路由 skill（Router skills）

当 user-invoked skill 多到你记不住时，堆积起来的认知负载可以用一个**路由 skill** 来治：一个 user-invoked skill，点名其他 skill 以及何时该用哪一个，让人只需要记住一个 skill 而不是许多个。它只能提示，永远不能触发它们：user-invoked skill 没有 description，除了人之外没有任何东西能触达它们。
