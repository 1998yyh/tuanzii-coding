---
name: codebase-design
description: 设计 deep module 的共享词汇表。当用户想设计或改进模块接口、寻找深化（deepening）机会、决定 seam 放在哪、让代码更可测或更适合 AI 浏览时，或其他 skill 需要 deep module 词汇表时使用。
---

# Codebase Design

设计 **deep module**：小接口背后藏着大量行为，落在干净的 seam 上，并且可以通过该接口测试。在任何设计或重构代码的地方使用这套语言和这些原则。目标：给调用方 leverage，给维护者 locality，给所有人可测性。

## 词汇表

严格使用这些术语 —— 不要用 "component"、"service"、"API" 或 "boundary" 替代。语言一致本身就是目的。

**Module（模块）** —— 任何有接口和实现的东西。刻意做到与规模无关：一个函数、一个类、一个包、或跨层的切片都算。_避免用_：unit、component、service。

**Interface（接口）** —— 调用方要正确使用模块所必须知道的一切：类型签名，还有不变量、顺序约束、错误模式、所需配置和性能特征。_避免用_：API、signature（太窄 —— 它们只指类型层面的表面）。

**Implementation（实现）** —— 模块内部的东西，它的代码本体。与 **Adapter** 区分开：一个东西可以是小 adapter 大实现（一个 Postgres 仓库），也可以是大 adapter 小实现（一个内存 fake）。话题在 seam 上时用 "adapter"，否则用 "implementation"。

**Depth（深度）** —— 接口处的 leverage：调用方（或测试）每学习一单位接口，能驱动多少行为。大量行为藏在小接口后面，模块就是**深（deep）**的；接口几乎和实现一样复杂，就是**浅（shallow）**的。

**Seam** _（Michael Feathers）_ —— 一个不改该处代码就能改变行为的位置；模块接口所在的*位置*。seam 放在哪里是一个独立的设计决策，与 seam 后面放什么无关。_避免用_：boundary（与 DDD 的 bounded context 撞车）。

**Adapter（适配器）** —— 在 seam 处满足接口的具体东西。它描述的是*角色*（填哪个槽位），不是*实质*（里面装了什么）。

**Leverage（杠杆）** —— 调用方从深度中得到的东西：每学习一单位接口，获得更多能力。一份实现，回报给 N 个调用点和 M 个测试。

**Locality（局部性）** —— 维护者从深度中得到的东西：变更、bug、知识和验证集中在一处，而不是散布到各调用方。修一次，处处修好。

## 深 vs 浅

**Deep module** = 小接口 + 大量实现：

```
┌─────────────────────┐
│   Small Interface   │  ← Few methods, simple params
├─────────────────────┤
│                     │
│  Deep Implementation│  ← Complex logic hidden
│                     │
└─────────────────────┘
```

**Shallow module** = 大接口 + 单薄实现（要避免）：

```
┌─────────────────────────────────┐
│       Large Interface           │  ← Many methods, complex params
├─────────────────────────────────┤
│  Thin Implementation            │  ← Just passes through
└─────────────────────────────────┘
```

设计接口时问：

- 方法数量还能减吗？
- 参数还能简化吗？
- 还能把更多复杂度藏进内部吗？

## 原则

- **深度是接口的属性，不是实现的属性。** 一个 deep module 内部可以由小的、可 mock、可替换的部件组合而成 —— 只是它们不属于接口。一个模块除了在接口处的**外部 seam**，还可以有**内部 seam**（实现私有，供自己的测试用）。
- **删除测试（deletion test）。** 想象删掉这个模块。如果复杂度随之消失，它只是个透传层。如果复杂度在 N 个调用方身上重新冒出来，它就是在挣钱养家。
- **接口就是测试面。** 调用方和测试跨过同一个 seam。如果你想测到接口*之外*的东西，模块的形状多半是错的。
- **一个 adapter 意味着假想的 seam，两个 adapter 才意味着真实的 seam。** 除非确有东西在这个 seam 上变化，否则不要引入它。

## 为可测性而设计

好接口让测试自然发生：

1. **接受依赖，而不是创建依赖。**

   ```typescript
   // Testable
   function processOrder(order, paymentGateway) {}

   // Hard to test
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **返回结果，而不是制造副作用。**

   ```typescript
   // Testable
   function calculateDiscount(cart): Discount {}

   // Hard to test
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **小表面积。** 方法越少 = 需要的测试越少。参数越少 = 测试准备越简单。

## 概念间关系

- 一个 **Module** 恰有一个 **Interface**（它呈现给调用方和测试的表面）。
- **Depth** 是 **Module** 的属性，相对其 **Interface** 度量。
- **Seam** 是 **Module** 的 **Interface** 所在的位置。
- **Adapter** 位于 **Seam** 处，满足 **Interface**。
- **Depth** 为调用方产出 **Leverage**，为维护者产出 **Locality**。

## 已被否决的框架

- **把深度定义为实现行数与接口行数之比**（Ousterhout）：这会奖励往实现里灌水。我们改用"深度即 leverage"。
- **把 "interface" 当成 TypeScript 的 `interface` 关键字或类的公有方法**：太窄 —— 这里的接口包含调用方必须知道的每一个事实。
- **"Boundary"**：与 DDD 的 bounded context 撞车。说 **seam** 或 **interface**。

## 深入阅读

- **在给定依赖的情况下深化一个模块簇** —— 见 [DEEPENING.md](DEEPENING.md)：依赖分类、seam 纪律、"替换而非叠加"的测试策略。
- **探索备选接口** —— 见 [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md)：并行派多个 subagent，用几种截然不同的方式设计接口，再从深度、局部性和 seam 位置上对比。
