# CONTEXT.md 格式

## 结构

```md
# {上下文名称}

{一两句话说明这个上下文是什么、为什么存在。}

## 语言

**Order（订单）**:
{一两句话的术语描述}
_避免使用_: 采购单、交易

**Invoice（发票）**:
发货后发给客户的付款请求。
_避免使用_: 账单、付款单

**Customer（客户）**:
下单的个人或组织。
_避免使用_: 委托方、买家、账户
```

## 规则

- **要有主见。** 同一个概念存在多个说法时，挑最好的那个，其余的列到 `_避免使用_` 下。
- **定义要紧凑。** 最多一两句话。定义它**是什么**，而不是它做什么。
- **只收录本项目上下文特有的术语。** 通用编程概念（超时、错误类型、工具模式）即使项目里大量使用也不收录。加词条之前先问自己：这是本上下文独有的概念，还是通用编程概念？只有前者配得上。
- **出现自然聚类时用子标题分组。** 如果所有术语都属于同一个内聚领域，平铺列表即可。

## 单上下文 vs 多上下文仓库

**单上下文（大多数仓库）：** 仓库根目录放一个 `CONTEXT.md`。

**多上下文：** 仓库根目录放一个 `CONTEXT-MAP.md`，列出各上下文、它们的位置以及相互关系：

```md
# 上下文地图

## 上下文

- [Ordering](./src/ordering/CONTEXT.md) — 接收并跟踪客户订单
- [Billing](./src/billing/CONTEXT.md) — 生成发票并处理付款
- [Fulfillment](./src/fulfillment/CONTEXT.md) — 管理仓库拣货与发货

## 关系

- **Ordering → Fulfillment**: Ordering 发出 `OrderPlaced` 事件；Fulfillment 消费它来开始拣货
- **Fulfillment → Billing**: Fulfillment 发出 `ShipmentDispatched` 事件；Billing 消费它来生成发票
- **Ordering ↔ Billing**: 共享 `CustomerId` 和 `Money` 类型
```

技能按以下规则推断适用哪种结构：

- 存在 `CONTEXT-MAP.md` → 读它来定位各上下文
- 只有根目录 `CONTEXT.md` → 单上下文
- 两者都没有 → 第一个术语敲定时再懒惰地创建根目录 `CONTEXT.md`

存在多个上下文时，推断当前话题属于哪一个。判断不了就问。
