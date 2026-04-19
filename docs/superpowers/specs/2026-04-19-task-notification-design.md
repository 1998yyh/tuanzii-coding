# 任务完成通知 Hook 设计

## 概述

当 Claude Code 停止响应时，通过系统通知提醒用户任务已完成，通知内容包含 Claude 最后回复的动态摘要。用户可通过插件配置开关控制是否启用通知。兼容 Windows 和 macOS。

## 方案选择

**Node.js + node-notifier**（已选定）

- 使用 `node-notifier` 发送跨平台系统通知（Windows / macOS）
- 无需系统级依赖，npm install 即可
- Windows：使用 Windows Toast 通知
- macOS：使用 `terminal-notifier`（推荐）或原生 `osascript` 作为 fallback
- 通知样式支持标题、正文、图标

## 架构

```
Claude Stop 事件
    ↓
hooks/hooks.json → Stop 钩子配置
    ↓
scripts/notify.js ← stdin: { last_assistant_message, ... }
    ↓
检查 userConfig 开关（环境变量）
    ↓ 已启用
node-notifier → 系统通知（Windows / macOS）
```

## 文件清单

| 文件 | 作用 |
|---|---|
| `scripts/notify.js` | 通知脚本：读 stdin、提取摘要、发送通知 |
| `hooks/hooks.json` | 注册 Stop 钩子 |
| `package.json` | 声明 node-notifier 依赖 |
| `.claude-plugin/plugin.json` | 添加 userConfig.notify_enabled |

## 详细设计

### 1. hooks/hooks.json

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "node ${CLAUDE_PLUGIN_ROOT}/scripts/notify.js"
          }
        ]
      }
    ]
  }
}
```

### 2. scripts/notify.js

- 从 stdin 读取 JSON
- 提取 `last_assistant_message` 字段
- 检查环境变量 `TUAZII_NOTIFY_ENABLED`（由 Claude Code 从 userConfig 注入），若为 `"false"` 则退出
- 截取前 100 字符作为通知正文
- 空消息时显示「Claude 任务已完成」
- 使用 `node-notifier` 发送系统通知，标题「tuanzii」，正文为摘要
- node-notifier 会自动根据操作系统选择通知方式：
  - Windows：Windows Toast / Balloon
  - macOS：`terminal-notifier`（如果已安装）或 `osascript`（系统自带）

### 3. .claude-plugin/plugin.json

在 `userConfig` 中添加：

```json
"userConfig": {
  "notify_enabled": {
    "description": "任务完成时是否发送系统通知",
    "sensitive": false
  }
}
```

默认值为 true（启用）。

### 4. package.json

声明 `node-notifier` 为 dependencies。

## 环境变量

| 变量 | 来源 | 用途 |
|---|---|---|
| `CLAUDE_PLUGIN_ROOT` | Claude Code 自动注入 | 定位插件目录 |
| `TUAZII_NOTIFY_ENABLED` | userConfig 注入 | 控制通知开关 |

## 错误处理

- node-notifier 不可用时静默失败（exit 0），不阻塞 Claude
- macOS 未安装 terminal-notifier 时，node-notifier 自动 fallback 到 osascript
- JSON 解析失败时使用默认消息
- stdin 为空时使用默认消息
