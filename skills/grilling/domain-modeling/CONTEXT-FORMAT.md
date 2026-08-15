# CONTEXT.md 格式

## 结构

```md
# {Context 名称}

{一两句话描述这个 context 是什么、为什么存在。}

## Language

**Order**:
{一两句话描述这个术语}
_Avoid_: Purchase, transaction

**Invoice**:
交付后发给客户的付款请求。
_Avoid_: Bill, payment request

**Customer**:
下单的个人或组织。
_Avoid_: Client, buyer, account
```

## 规则

- **要有主见。** 同一个概念存在多个叫法时，选最好的那个，其余列在 `_Avoid_` 下。
- **定义要紧凑。** 最多一两句话。定义它*是什么*，而不是它*做什么*。
- **只收录本项目 context 特有的术语。** 通用编程概念（timeout、错误类型、工具模式）即使项目大量使用也不收录。添加术语前先问：这是这个 context 独有的概念，还是通用编程概念？只有前者够格。
- **出现自然聚类时用子标题分组。** 如果所有术语都属于同一片内聚的领域，平铺列表即可。

## 单 context 与多 context 仓库

**单 context（大多数仓库）：** 仓库根目录一个 `CONTEXT.md`。

**多 context：** 仓库根目录的 `CONTEXT-MAP.md` 列出所有 context、它们的位置以及相互关系：

```md
# Context Map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — 接收并跟踪客户订单
- [Billing](./src/billing/CONTEXT.md) — 生成发票并处理支付
- [Fulfillment](./src/fulfillment/CONTEXT.md) — 管理仓库拣货与发货

## Relationships

- **Ordering → Fulfillment**: Ordering 发出 `OrderPlaced` 事件；Fulfillment 消费它开始拣货
- **Fulfillment → Billing**: Fulfillment 发出 `ShipmentDispatched` 事件；Billing 消费它生成发票
- **Ordering ↔ Billing**: 共享 `CustomerId` 和 `Money` 类型
```

skill 按以下规则推断适用哪种结构：

- 存在 `CONTEXT-MAP.md` 时，读它来定位各 context
- 只有根目录 `CONTEXT.md` 时，为单 context
- 两者都不存在时，在第一个术语敲定时懒创建根目录 `CONTEXT.md`

存在多个 context 时，推断当前话题与哪个相关。不清楚就问。
