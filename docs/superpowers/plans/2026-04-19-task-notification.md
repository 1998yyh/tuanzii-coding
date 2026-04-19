# 任务完成通知 Hook 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 Claude Code Stop 事件的系统通知钩子，任务完成时弹出包含摘要的桌面通知，支持用户开关控制。

**Architecture:** 通过 `hooks/hooks.json` 注册 Stop 钩子，调用 `scripts/notify.js` 脚本。脚本从 stdin 读取 Claude 最后回复，用 `node-notifier` 发送跨平台（Windows/macOS）系统通知。开关通过 `plugin.json` 的 `userConfig` 控制。

**Tech Stack:** Node.js, node-notifier

---

### Task 1: 初始化 package.json 并安装 node-notifier

**Files:**
- Create: `package.json`

- [ ] **Step 1: 创建 package.json**

```bash
cd C:/Users/53243/Desktop/tuanzii-coding
npm init -y
```

- [ ] **Step 2: 安装 node-notifier**

```bash
npm install node-notifier
```

Expected: `node_modules/` 目录生成，`package.json` 中出现 `node-notifier` 依赖。

- [ ] **Step 3: 验证安装成功**

```bash
node -e "const notifier = require('node-notifier'); console.log(typeof notifier.notify);"
```

Expected: 输出 `function`

- [ ] **Step 4: 提交**

```bash
git add package.json package-lock.json
git commit -m "chore: 初始化 npm 项目并安装 node-notifier"
```

---

### Task 2: 编写通知脚本 scripts/notify.js

**Files:**
- Create: `scripts/notify.js`

- [ ] **Step 1: 创建 scripts/notify.js**

```javascript
#!/usr/bin/env node

const notifier = require('node-notifier');
const path = require('path');

// 读取 stdin JSON
let input = '';

process.stdin.on('data', (chunk) => {
  input += chunk;
});

process.stdin.on('end', () => {
  try {
    // 检查开关：Claude Code 将 userConfig 注入为环境变量 TUAZII_NOTIFY_ENABLED
    const enabled = process.env.TUAZII_NOTIFY_ENABLED;
    if (enabled === 'false' || enabled === '0') {
      process.exit(0);
    }

    // 解析 stdin JSON
    let lastMessage = '';
    if (input.trim()) {
      const data = JSON.parse(input);
      lastMessage = data.last_assistant_message || '';
    }

    // 生成通知正文：截取前 100 字符
    const title = 'tuanzii';
    let body = lastMessage.trim()
      ? lastMessage.trim().slice(0, 100) + (lastMessage.trim().length > 100 ? '...' : '')
      : 'Claude 任务已完成';

    // 发送系统通知
    notifier.notify({
      title: title,
      message: body,
      sound: true,
    });

    process.exit(0);
  } catch {
    // 任何错误静默退出，不阻塞 Claude
    process.exit(0);
  }
});
```

- [ ] **Step 2: 手动测试脚本**

模拟 Stop 钩子发送 JSON 数据：

```bash
echo '{"last_assistant_message":"已完成代码重构，新增了3个测试用例。","hook_event_name":"Stop"}' | node C:/Users/53243/Desktop/tuanzii-coding/scripts/notify.js
```

Expected: 弹出系统通知，标题「tuanzii」，正文「已完成代码重构，新增了3个测试用例。」

- [ ] **Step 3: 测试开关关闭时不发送通知**

```bash
TUAZII_NOTIFY_ENABLED=false echo '{"last_assistant_message":"测试消息"}' | node C:/Users/53243/Desktop/tuanzii-coding/scripts/notify.js
```

Expected: 无通知弹出，脚本静默退出。

- [ ] **Step 4: 测试空 stdin 的兜底行为**

```bash
echo '' | node C:/Users/53243/Desktop/tuanzii-coding/scripts/notify.js
```

Expected: 弹出系统通知，正文为「Claude 任务已完成」。

- [ ] **Step 5: 提交**

```bash
git add scripts/notify.js
git commit -m "feat: 添加任务完成通知脚本"
```

---

### Task 3: 配置 hooks.json 注册 Stop 钩子

**Files:**
- Modify: `hooks/hooks.json`

- [ ] **Step 1: 更新 hooks/hooks.json**

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

- [ ] **Step 2: 验证 JSON 格式正确**

```bash
node -e "JSON.parse(require('fs').readFileSync('C:/Users/53243/Desktop/tuanzii-coding/hooks/hooks.json','utf8')); console.log('JSON valid')"
```

Expected: 输出 `JSON valid`

- [ ] **Step 3: 提交**

```bash
git add hooks/hooks.json
git commit -m "feat: 注册 Stop 钩子调用通知脚本"
```

---

### Task 4: 更新 plugin.json 添加 userConfig 开关

**Files:**
- Modify: `.claude-plugin/plugin.json`

- [ ] **Step 1: 更新 .claude-plugin/plugin.json**

当前内容：
```json
{
  "name": "tuanzii",
  "description": "tuanzii Claude Code Marketplace plugin",
  "version": "1.0.0",
  "author": {
    "name": "hao.yang"
  }
}
```

改为：
```json
{
  "name": "tuanzii",
  "description": "tuanzii Claude Code Marketplace plugin",
  "version": "1.1.0",
  "author": {
    "name": "hao.yang"
  },
  "userConfig": {
    "notify_enabled": {
      "description": "任务完成时是否发送系统通知（true/false）",
      "sensitive": false
    }
  }
}
```

- [ ] **Step 2: 验证 JSON 格式正确**

```bash
node -e "JSON.parse(require('fs').readFileSync('C:/Users/53243/Desktop/tuanzii-coding/.claude-plugin/plugin.json','utf8')); console.log('JSON valid')"
```

Expected: 输出 `JSON valid`

- [ ] **Step 3: 提交**

```bash
git add .claude-plugin/plugin.json
git commit -m "feat: 添加通知开关 userConfig 配置项"
```

---

### Task 5: 端到端验证

- [ ] **Step 1: 确认完整项目结构**

```bash
ls -la C:/Users/53243/Desktop/tuanzii-coding/
ls -la C:/Users/53243/Desktop/tuanzii-coding/scripts/
ls -la C:/Users/53243/Desktop/tuanzii-coding/hooks/
```

Expected 目录结构：
```
tuanzii-coding/
├── .claude-plugin/plugin.json   ← 含 userConfig
├── hooks/hooks.json             ← Stop 钩子已注册
├── scripts/notify.js            ← 通知脚本
├── package.json                 ← node-notifier 依赖
├── package-lock.json
├── node_modules/
└── ...
```

- [ ] **Step 2: 再次运行完整模拟测试**

```bash
echo '{"last_assistant_message":"所有文件已创建，测试通过。"}' | node C:/Users/53243/Desktop/tuanzii-coding/scripts/notify.js
```

Expected: 弹出系统通知，标题「tuanzii」，正文「所有文件已创建，测试通过。」

- [ ] **Step 3: 最终提交（如有未提交的更改）**

```bash
git status
git add -A
git commit -m "feat: 任务完成通知 hook 全部就绪"
```
