#!/usr/bin/env node

const notifier = require('node-notifier');

// 5 seconds timeout to prevent blocking Claude exit
setTimeout(() => process.exit(0), 5000);

// 读取 stdin JSON
let input = '';

process.stdin.on('data', (chunk) => {
  input += chunk;
});

process.stdin.on('end', () => {
  try {
    // 检查开关：Claude Code 将 userConfig 注入为环境变量 TUANZII_NOTIFY_ENABLED
    const enabled = process.env.TUANZII_NOTIFY_ENABLED;
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
