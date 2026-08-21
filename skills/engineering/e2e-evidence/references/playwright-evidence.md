# Playwright 证据规则

仅在④配置、运行或解释 E2E 证据时阅读本文件。优先保留目标项目的 Playwright 配置与输出约定；不要把这里的示例整体覆盖进配置文件。

## 最小证据集

每次运行（无论成败）都应保留截图；对失败流程，还应能定位以下相对路径：

| 证据 | 用途 | 常见策略 |
|---|---|---|
| 截图 | 查看每步与失败时的可见 UI | `on` 兜底 + 每个 `test.step` 末尾全页截图（按 YAML 步骤 id 命名，见「步骤级截图」） |
| 视频 | 复现动作顺序 | `retain-on-failure` |
| Trace | 时间线、网络与 DOM 诊断 | `retain-on-failure` 或项目既有重试策略 |
| HTML 报告 | 聚合测试与附件入口 | 保留项目既有 reporter 并写入本次结果目录 |
| 日志 | 命令、退出码、服务/测试摘要 | 脱敏文本摘要 |

不要把 Trace 策略当作截图或视频策略的替代物。配置合并时保留既有 `use`、reporter、projects、webServer 与 baseURL；只加入缺失字段或在项目原有机制中配置等价输出。

## 步骤级截图

`screenshot: on` 只产出每条测试结束态一张图；跨页跳转的流程（如确认页 → 签约页）早期业务步骤没有任何视觉证据，结束图甚至可能落在流程边界之外。③应在每个 `test.step` 的断言之后补一张全页截图（具体模式见③的 Playwright 模式文档），④归档时按 `results/<run-id>/evidence/<flow-id>/<step-id>.png` 归位，并在结果清单中按步骤 id 登记相对路径。评审业务证据时以步骤截图为主、`test-finished-*.png` 兜底图为辅。

## 配置合并陷阱

`projects[].use` 会覆盖顶层 `use` 的同名字段。在 project 里展开 `devices['Desktop Chrome']` 等桌面设备描述符，会静默覆盖顶层已设的移动端 `viewport` / `isMobile` / `hasTouch`——测试照样全绿，但证据全部变成桌面视口。修改配置后核对**最终生效值**（如用 `npx playwright test --list` 或打印 `use` 合并结果），不要只看顶层声明。

## 视口保真校验

运行结束后机械核对截图尺寸与配置 viewport 一致（macOS 用 `sips -g pixelWidth -g pixelHeight`，或 ImageMagick `identify`）。尺寸不符说明视口配置被覆盖，按上节排查；不要把桌面视口证据当作移动端流程的验收依据。

## 结果清单

每次正式运行写入 `results/<run-id>.json`，附件位于 `results/<run-id>/evidence/<flow-id>/`。清单只保存项目相对路径和脱敏摘要：

```json
{
  "schemaVersion": 1,
  "id": "run-20260814T090000Z-a1b2c3",
  "createdAt": "2026-08-14T09:00:00Z",
  "status": "passed",
  "flows": [
    {
      "flowId": "user-login",
      "spec": "tests/e2e/user-login.spec.ts",
      "status": "passed",
      "stepIds": ["open-login", "submit-credentials", "verify-dashboard"],
      "artifacts": {
        "htmlReport": "results/run-20260814T090000Z-a1b2c3/html-report/index.html",
        "log": "results/run-20260814T090000Z-a1b2c3/evidence/user-login/run.log"
      }
    }
  ],
  "command": "npx playwright test tests/e2e/user-login.spec.ts"
}
```

- `status` 为 `passed`、`failed`、`blocked` 或 `cancelled`。
- 失败项在 `artifacts` 中尽量列出 screenshot、video、trace、htmlReport 和 log；未产生的项目省略并在摘要说明原因。
- `stepIds` 只写实际执行到的 YAML step id，不写测试数据或用户输入。
- `command` 不含环境变量赋值、token、Cookie、绝对路径或未经脱敏的用户输入。
- 历史清单和附件不可覆盖；同一次失败的原始产物不得为节省空间而删除。
- Playwright 每次运行前都会清空 `--output` 目录：已归档目录不得复用为后续运行（含③的单 spec 验证）的 outputDir，补跑一律用全新目录，否则同 run 其他流程的产物被静默清空。

## 证据支持的结论

将结论限制在产物所能支持的范围：

- Trace/截图显示页面与 YAML 预期不同：说明观察到的差异，交①判断业务契约。
- Trace 显示 locator 找不到但页面目标仍存在：交③修正 selector。
- 日志显示服务未启动、认证数据缺失或网络不可用：报告环境前置条件，不归因为产品缺陷。
- 没有截图、Trace 或日志：报告证据链不完整；不要根据退出码猜测根因。

## 临时失败验证

只在配置/修复证据获授权时创建。临时测试必须固定在本次可识别的临时文件名、只包含无敏感数据的断言，并在收集后立即删除。删除前确认路径属于本次临时文件；如果无法安全删除，保留文件并明确报告，不能删除任何未知 spec。
