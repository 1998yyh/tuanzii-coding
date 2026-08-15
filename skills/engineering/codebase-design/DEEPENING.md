# Deepening（深化）

如何在给定依赖的情况下，安全地深化一簇浅模块。假设你已掌握 [SKILL.md](SKILL.md) 的词汇 —— **module**、**interface**、**seam**、**adapter**。

## 依赖分类

评估一个深化候选时，先给它的依赖分类。类别决定深化后的模块如何跨 seam 测试。

### 1. 进程内（In-process）

纯计算、内存状态、无 I/O。永远可以深化 —— 合并模块，直接通过新接口测试。不需要 adapter。

### 2. 本地可替代（Local-substitutable）

有本地测试替身的依赖（Postgres 对应 PGLite、内存文件系统）。只要替身存在就可以深化。深化后的模块在测试套件里带着替身一起测。seam 是内部的；模块的外部接口上不开 port。

### 3. 远程但自有（Ports & Adapters）

跨网络边界、但属于你自己的服务（微服务、内部 API）。在 seam 处定义一个 **port**（接口）。deep module 持有逻辑；传输层作为 **adapter** 注入。测试用内存 adapter，生产用 HTTP/gRPC/队列 adapter。

建议的表述形状：*"在 seam 处定义一个 port，生产环境实现 HTTP adapter、测试实现内存 adapter，这样逻辑落在一个 deep module 里，尽管部署跨了网络。"*

### 4. 真正的外部依赖（Mock）

你控制不了的第三方服务（Stripe、Twilio 等）。深化后的模块把外部依赖作为注入的 port 接收；测试提供 mock adapter。

## Seam 纪律

- **一个 adapter 意味着假想的 seam，两个 adapter 才意味着真实的 seam。** 除非至少有理由存在两个 adapter（通常是生产 + 测试），否则不要引入 port。单 adapter 的 seam 只是间接层。
- **内部 seam vs 外部 seam。** 一个 deep module 可以有内部 seam（实现私有，供自己的测试用），同时有接口处的外部 seam。不要因为测试用到了内部 seam，就把它从接口上暴露出去。

## 测试策略：替换，而非叠加

- 一旦深化模块的接口上有了测试，浅模块上的旧单元测试就成了废物 —— 删掉它们。
- 在深化模块的接口上写新测试。**接口就是测试面。**
- 测试通过接口断言可观察的结果，而不是内部状态。
- 测试应该扛得住内部重构 —— 它描述行为，不描述实现。如果实现一变测试就得跟着变，说明它测到了接口之外。
