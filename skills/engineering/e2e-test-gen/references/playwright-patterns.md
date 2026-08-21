# Playwright 测试模式

仅在创建或维护③的 spec 时阅读本文件。优先遵循目标项目已有的 Playwright、fixture、登录和断言约定；本文件只给出不能省略的互操作规则。

## 步骤映射

每个流程步骤都映射到一个带步骤 id 的 `test.step`，但不把 YAML 机械翻译成 CSS 操作：

```ts
test("已注册用户登录后看到工作台", async ({ page }) => {
  await test.step("open-login：打开登录页", async () => {
    await page.goto("/login");
    await expect(page.getByRole("button", { name: "登录" })).toBeVisible();
  });

  await test.step("submit-credentials：填入测试账号并提交", async () => {
    // 使用项目 fixture 或已登记的环境变量；不要写入真实值。
  });

  await test.step("verify-dashboard：确认已进入工作台", async () => {
    await expect(page.getByTestId("current-user")).toBeVisible();
  });
});
```

- 每个 `test.step` 至少覆盖该 YAML 步骤的动作和可观察结果；允许一段连贯表单填写留在同一 step。
- 将 flow id 放入测试标题、describe 或文件名，确保④能稳定关联 `flowId → spec → step id`。
- 使用 `expect` 的自动等待；不要用任意固定 sleep 掩盖页面未就绪。

## 步骤证据截图

每个 `test.step` 末尾（该步骤全部断言通过之后）留一张全页截图，按 YAML 步骤 id 命名，供④归档到 `results/<run-id>/evidence/<flow-id>/`：

```ts
test("已注册用户登录后看到工作台", async ({ page }, testInfo) => {
  await test.step("verify-dashboard：确认已进入工作台", async () => {
    await expect(page.getByTestId("current-user")).toBeVisible();
    await page.screenshot({
      path: testInfo.outputPath("verify-dashboard.png"),
      fullPage: true,
      animations: "disabled",
    });
  });
});
```

- `animations: "disabled"` 把 CSS 动画/过渡快进到结束态：弹窗滑入等场景不会截到半态，也就不用为动画加固定 sleep（上节的禁令仍然有效）。
- 截图是证据不是断言：不断言截图内容，也不用截图替代 `expect`。
- 签名注入 `testInfo` 才能用 `testInfo.outputPath`；`test-finished-*.png` 兜底图由 config 的 `screenshot: "on"` 自动产出，与步骤截图不冲突。

## 选择器与断言

优先顺序：`getByRole`（带可访问名称）→ `getByLabel` → `getByTestId` → 稳定用户文本。只有源码无更稳定线索时才使用项目既有 selector；记录它需要复核，而不是编造新 CSS 结构。

成功断言验证用户看到的页面、文本、路由或状态。请求响应、localStorage、store 和内部函数只能辅助等待或准备数据，不能成为唯一成功断言。

## 安全数据与隔离

- 仅通过 `steps[].data` 中已校验的 `fixtures.env.<别名>` 引用读取 YAML `fixtures.env` 登记的环境变量；读取后先检查是否缺失，但不打印值，也不接受 YAML 中的任何字面量数据。
- 复用项目已有 seed、API helper 或 fixture。没有安全数据源时停下并报告需求。
- 每个测试自包含清理或使用隔离数据；不要依赖上一个测试留下的用户、订单或浏览器状态。
- 不在 spec、快照、截图名称、错误消息或生成报告中回显秘密值。

## 测试落点同步

只有 `test.spec` 通过完整路径校验（位于顶层 `e2e/`、`playwright/` 或 `test(s)/e2e/`、`test(s)/playwright/` 下，为 `*.e2e.*` 或 `*.spec.*`，且路径不含符号链接）后，③才可创建或修改它。创建后重新确认该项目相对文件存在，并只将对应 YAML 的 `test.source` 从 `external` 设为 `existing`。测试随后失败也不把已存在的文件重新标为待创建；流程状态仍保持 `ready`，直到单文件实跑全绿。

## 失败处理

先区分 locator/时序问题、测试数据问题、环境问题和业务契约漂移。③可修前两类测试实现；业务语义、入口或成功结果冲突时移交①。不要降低断言、跳过测试或修改产品实现来换取绿灯。
