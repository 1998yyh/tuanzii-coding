---
name: migrate-to-shoehorn
description: 将测试文件中的 `as` 类型断言迁移到 @total-typescript/shoehorn。当用户提到 shoehorn 迁移、想替换测试中的 `as` 断言、类型断言、或需要部分测试数据（partial test data）时使用。
---

# 迁移到 Shoehorn

## 为什么用 shoehorn？

`shoehorn` 允许在测试中传入部分数据，同时让 TypeScript 保持类型安全。它用类型安全的替代方案取代 `as` 断言。

**仅限测试代码。** 永远不要在生产代码中使用 shoehorn。

测试中使用 `as` 的问题：

- 违背"不要用 `as`"的训练直觉
- 必须手动指定目标类型
- 故意传错误数据时需要双重断言（`as unknown as Type`）

## 安装

```bash
npm i @total-typescript/shoehorn
```

## 迁移模式

### 大对象只关心少数字段

迁移前：

```ts
type Request = {
  body: { id: string };
  headers: Record<string, string>;
  cookies: Record<string, string>;
  // ...20 more properties
};

it("gets user by id", () => {
  // Only care about body.id but must fake entire Request
  getUser({
    body: { id: "123" },
    headers: {},
    cookies: {},
    // ...fake all 20 properties
  });
});
```

迁移后：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

it("gets user by id", () => {
  getUser(
    fromPartial({
      body: { id: "123" },
    }),
  );
});
```

### `as Type` → `fromPartial()`

迁移前：

```ts
getUser({ body: { id: "123" } } as Request);
```

迁移后：

```ts
import { fromPartial } from "@total-typescript/shoehorn";

getUser(fromPartial({ body: { id: "123" } }));
```

### `as unknown as Type` → `fromAny()`

迁移前：

```ts
getUser({ body: { id: 123 } } as unknown as Request); // wrong type on purpose
```

迁移后：

```ts
import { fromAny } from "@total-typescript/shoehorn";

getUser(fromAny({ body: { id: 123 } }));
```

## 各函数适用场景

| 函数            | 适用场景                                     |
| --------------- | -------------------------------------------- |
| `fromPartial()` | 传入仍能通过类型检查的部分数据               |
| `fromAny()`     | 故意传入错误数据（保留自动补全）             |
| `fromExact()`   | 强制完整对象（之后可与 fromPartial 互换）    |

## 工作流程

1. **收集需求** —— 询问用户：
   - 哪些测试文件中的 `as` 断言造成了问题？
   - 是否涉及大对象但只有部分字段重要的场景？
   - 是否需要故意传入错误数据做错误路径测试？

2. **安装并迁移**：
   - [ ] 安装：`npm i @total-typescript/shoehorn`
   - [ ] 找出含 `as` 断言的测试文件：`grep -r " as [A-Z]" --include="*.test.ts" --include="*.spec.ts"`
   - [ ] 将 `as Type` 替换为 `fromPartial()`
   - [ ] 将 `as unknown as Type` 替换为 `fromAny()`
   - [ ] 添加 `@total-typescript/shoehorn` 的 import
   - [ ] 运行类型检查验证
