---
name: git-guardrails-claude-code
description: 配置 Claude Code 钩子，在危险 git 命令（push、reset --hard、clean、branch -D 等）执行前拦截。当用户想防止破坏性 git 操作、添加 git 安全钩子、在 Claude Code 中禁用 git push/reset 时使用。触发词：git 护栏、危险命令拦截、git 安全钩子。
---

# 配置 Git 护栏

设置一个 PreToolUse 钩子，在 Claude 执行危险 git 命令之前将其拦截。

## 拦截哪些命令

- `git push`（所有变体，包括 `--force`）
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

命令被拦截时，Claude 会收到一条提示，告知其无权执行这些命令。

## 步骤

### 1. 询问生效范围

询问用户：只对**当前项目**生效（`.claude/settings.json`），还是对**所有项目**生效（`~/.claude/settings.json`）？

### 2. 复制钩子脚本

内置脚本位于：[scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh)

根据生效范围复制到目标位置：

- **项目级**：`.claude/hooks/block-dangerous-git.sh`
- **全局级**：`~/.claude/hooks/block-dangerous-git.sh`

复制后执行 `chmod +x` 赋予可执行权限。

### 3. 在 settings 中注册钩子

向对应的 settings 文件添加：

**项目级**（`.claude/settings.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

**全局级**（`~/.claude/settings.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

如果 settings 文件已存在，把钩子合并进现有的 `hooks.PreToolUse` 数组——不要覆盖其他配置。

### 4. 询问是否需要定制

询问用户是否要在拦截列表中增删匹配模式，并相应修改复制后的脚本。

### 5. 验证

快速测试一下：

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
```

预期以退出码 2 退出，并向 stderr 打印 BLOCKED 提示信息。
