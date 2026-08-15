---
name: using-git-worktrees
description: 开始需要与当前工作区隔离的功能工作，或执行实施计划之前使用；通过原生工具或 Git worktree 回退方案确保存在隔离工作区。
---

# 使用 Git Worktree

## Overview
> 【老王注】这节定调子：开工先进隔离环境，优先级是「检测已有隔离 > 平台原生工具 > 手动 git worktree」，别跟 harness 对着干。
> 【老王注】本质一句话：worktree 是手段不是目的——能复用就别新建，套娃 worktree 是最常见的翻车点。

Ensure work happens in an isolated workspace. Prefer your platform's native worktree tools. Fall back to manual git worktrees only when no native tool is available.

**Core principle:** Detect existing isolation first. Then use native tools. Then fall back to git. Never fight the harness.

**Announce at start:** "I'm using the using-git-worktrees skill to set up an isolated workspace."

## Step 0: Detect Existing Isolation
> 【老王注】铁律：先检测再动手。不看 GIT_DIR 就建 worktree，等于在 worktree 里又生一个 worktree。
> 【老王注】坑点：submodule 也会让 GIT_DIR != GIT_COMMON，别误判成「已在 worktree 里」——先跑 superproject 检查排除掉。

**Before creating anything, check if you are already in an isolated workspace.**

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**Submodule guard:** `GIT_DIR != GIT_COMMON` is also true inside git submodules. Before concluding "already in a worktree," verify you are not in a submodule:

```bash
# If this returns a path, you're in a submodule, not a worktree — treat as normal repo
git rev-parse --show-superproject-working-tree 2>/dev/null
```

**If `GIT_DIR != GIT_COMMON` (and not a submodule):** You are already in a linked worktree. Skip to Step 2 (Project Setup). Do NOT create another worktree.

Report with branch state:
- On a branch: "Already in isolated workspace at `<path>` on branch `<name>`."
- Detached HEAD: "Already in isolated workspace at `<path>` (detached HEAD, externally managed). Branch creation needed at finish time."

**If `GIT_DIR == GIT_COMMON` (or in a submodule):** You are in a normal repo checkout.

Has the user already indicated their worktree preference in your instructions? If not, ask for consent before creating a worktree:

> "Would you like me to set up an isolated worktree? It protects your current branch from changes."

Honor any existing declared preference without asking. If the user declines consent, work in place and skip to Step 2.

## Step 1: Create Isolated Workspace
> 【老王注】顺序是硬规定：有原生工具就别碰 git 命令——徒手建的 worktree 平台看不见、管不了、也清不掉。

**You have two mechanisms. Try them in this order.**

### 1a. Native Worktree Tools (preferred)
> 【老王注】比如 Claude Code 的 EnterWorktree：目录、分支、清理全自动。你手动 git worktree add 出来的就是「幽灵状态」，harness 感知不到。

The user has asked for an isolated workspace (Step 0 consent). Do you already have a way to create a worktree? It might be a tool with a name like `EnterWorktree`, `WorktreeCreate`, a `/worktree` command, or a `--worktree` flag. If you do, use it and skip to Step 2.

Native tools handle directory placement, branch creation, and cleanup automatically. Using `git worktree add` when you have a native tool creates phantom state your harness can't see or manage.

Only proceed to Step 1b if you have no native worktree tool available.

### 1b. Git Worktree Fallback
> 【老王注】只有确定没有原生工具时才走这条后路——它是 fallback，不是默认路径。

**Only use this if Step 1a does not apply** — you have no native worktree tool available. Create a worktree manually using git.

#### Directory Selection
> 【老王注】选目录优先级：用户明说 > 项目已有目录 > 默认 .worktrees/。别自作主张换地方，一致性比聪明重要。

Follow this priority order. Explicit user preference always beats observed filesystem state.

1. **Check your instructions for a declared worktree directory preference.** If the user has already specified one, use it without asking.

2. **Check for an existing project-local worktree directory:**
   ```bash
   ls -d .worktrees 2>/dev/null     # Preferred (hidden)
   ls -d worktrees 2>/dev/null      # Alternative
   ```
   If found, use it. If both exist, `.worktrees` wins.

3. **If there is no other guidance available**, default to `.worktrees/` at the project root.

#### Safety Verification (project-local directories only)
> 【老王注】铁律：建之前先确认目录已被 gitignore。漏了这步，worktree 内容会被 git 跟踪，污染主仓库的 status，哭都来不及。

**MUST verify directory is ignored before creating worktree:**

```bash
git check-ignore -q .worktrees 2>/dev/null || git check-ignore -q worktrees 2>/dev/null
```

**If NOT ignored:** Add to .gitignore, commit the change, then proceed.

**Why critical:** Prevents accidentally committing worktree contents to repository.

#### Create the Worktree
> 【老王注】沙箱拦了别硬刚，跟用户说清楚然后在原目录干活——透明比失败强。

```bash
# Determine path based on chosen location
path="$LOCATION/$BRANCH_NAME"

git worktree add "$path" -b "$BRANCH_NAME"
cd "$path"
```

**Sandbox fallback:** If `git worktree add` fails with a permission error (sandbox denial), tell the user the sandbox blocked worktree creation and you're working in the current directory instead. Then run setup and baseline tests in place.

## Step 2: Project Setup
> 【老王注】worktree 是全新检出，依赖目录是空的——装依赖这步不能省，省了后面测试全红还找不到原因。

Auto-detect and run appropriate setup:

```bash
# Node.js
if [ -f package.json ]; then npm install; fi

# Rust
if [ -f Cargo.toml ]; then cargo build; fi

# Python
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f pyproject.toml ]; then poetry install; fi

# Go
if [ -f go.mod ]; then go mod download; fi
```

## Step 3: Verify Clean Baseline
> 【老王注】先跑一遍测试拿「干净基线」：不然开发中测试红了，你分不清是自己写坏的还是本来就坏的。
> 【老王注】基线就红？报告并问用户，别默默带病开工。

Run tests to ensure workspace starts clean:

```bash
# Use project-appropriate command
npm test / cargo test / pytest / go test ./...
```

**If tests fail:** Report failures, ask whether to proceed or investigate.

**If tests pass:** Report ready.

### Report
> 【老王注】报告固定三行：路径、测试结果、就绪状态——下游拿到就能直接开工。

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## Quick Reference
> 【老王注】速查表：遇到状况先查这张表，比回头翻步骤快。

| Situation | Action |
|-----------|--------|
| Already in linked worktree | Skip creation (Step 0) |
| In a submodule | Treat as normal repo (Step 0 guard) |
| Native worktree tool available | Use it (Step 1a) |
| No native tool | Git worktree fallback (Step 1b) |
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check instruction file, then default `.worktrees/` |
| Directory not ignored | Add to .gitignore + commit |
| Permission error on create | Sandbox fallback, work in place |
| Tests fail during baseline | Report failures + ask |
| No package.json/Cargo.toml | Skip dependency install |

## Common Mistakes
> 【老王注】五个高频翻车点，根因都一样：跳步、自作主张、不验证。

### Fighting the harness
> 【老王注】最大的坑：平台已经给了隔离，你还徒手 git——两边状态对不上，收尾时必乱。

- **Problem:** Using `git worktree add` when the platform already provides isolation
- **Fix:** Step 0 detects existing isolation. Step 1a defers to native tools.

### Skipping detection
> 【老王注】套娃 worktree 就是这么来的——Step 0 一次检测就能避免。

- **Problem:** Creating a nested worktree inside an existing one
- **Fix:** Always run Step 0 before creating anything

### Skipping ignore verification
> 【老王注】一条 git check-ignore 的事，别省。

- **Problem:** Worktree contents get tracked, pollute git status
- **Fix:** Always use `git check-ignore` before creating project-local worktree

### Assuming directory location
> 【老王注】按优先级走，别把 worktree 随手塞——项目约定大于个人习惯。

- **Problem:** Creates inconsistency, violates project conventions
- **Fix:** Follow priority: explicit instructions > existing project-local directory > default

### Proceeding with failing tests
> 【老王注】带病基线上做开发，等于在流沙上盖楼。

- **Problem:** Can't distinguish new bugs from pre-existing issues
- **Fix:** Report failures, get explicit permission to proceed

## Red Flags
> 【老王注】Never 清单背下来，尤其前两条——九成的 worktree 事故都是「重复创建」和「绕过原生工具」这两类。

**Never:**
- Create a worktree when Step 0 detects existing isolation
- Use `git worktree add` when you have a native worktree tool (e.g., `EnterWorktree`). This is the #1 mistake — if you have it, use it.
- Skip Step 1a by jumping straight to Step 1b's git commands
- Create worktree without verifying it's ignored (project-local)
- Skip baseline test verification
- Proceed with failing tests without asking

**Always:**
- Run Step 0 detection first
- Prefer native tools over git fallback
- Follow directory priority: explicit instructions > existing project-local directory > default
- Verify directory is ignored for project-local
- Auto-detect and run project setup
- Verify clean test baseline
