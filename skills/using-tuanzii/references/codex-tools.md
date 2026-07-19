# Codex Tool Mapping

Skills speak in actions ("dispatch a subagent", "create a todo", "read a file"). On Codex these resolve to the tools below.
> 【老王注】给 Codex 用户查的映射表：Codex 大量动作走 shell，读写文件靠 apply_patch，跟 Claude Code 的专用工具思路不一样。

| Action skills request | Codex equivalent |
|----------------------|------------------|
| Read a file | `shell` (e.g., `cat`, `head`, `tail`) — Codex reads files via shell |
| Create / edit / delete a file | `apply_patch` (structured diff for create, update, delete) |
| Run a shell command | `shell` |
| Search file contents | `shell` (e.g., `grep`, `rg`) |
| Find files by name | `shell` (e.g., `find`, `ls`) |
| Fetch a URL | `shell` with `curl` / `wget` — Codex has no native fetch tool |
| Search the web | `web_search` (enabled by default; configurable in `config.toml` via the top-level `web_search` setting — `live`, `cached`, or `disabled`) |
| Invoke a skill | Skills load natively — just follow the instructions |
| Dispatch a subagent (`Subagent (general-purpose):` template) | `spawn_agent` (see [Subagent dispatch requires multi-agent support](#subagent-dispatch-requires-multi-agent-support)) |
| Multiple parallel dispatches | Multiple `spawn_agent` calls in one response |
| Wait for subagent result | `wait_agent` |
| Free up subagent slot when done | `close_agent` |
| Task tracking ("create a todo", "mark complete") | `update_plan` |

## Instructions file
> 【老王注】Codex 的指令文件是 AGENTS.md（不是 CLAUDE.md）；AGENTS.override.md 存在时优先。

When a skill mentions "your instructions file", on Codex this is **`AGENTS.md`** at the project root. Codex also reads `~/.codex/AGENTS.md` for global context, and an `AGENTS.override.md` (in the project tree or `~/.codex/`) takes precedence when present. Codex walks from the project root down to the current working directory, concatenating `AGENTS.md` files it finds along the way, up to `project_doc_max_bytes` (32 KiB by default).

## Personal skills directory

User-level skills live at **`$CODEX_HOME/skills/`** (default `~/.codex/skills/`). Codex also reads the cross-runtime path **`~/.agents/skills/`** (shared with Copilot CLI and Gemini CLI). When both directories exist at the same scope, Codex loads them both as separate skill catalogs — Codex's docs don't currently document a precedence between them. Each skill is a subdirectory containing a `SKILL.md` (with `name` and `description` frontmatter).

## Subagent dispatch requires multi-agent support
> 【老王注】想用 dispatching-parallel-agents 这类派子代理的 skill，必须先在 config.toml 开 multi_agent，否则 spawn_agent 根本不存在。

Add to your Codex config (`~/.codex/config.toml`):

```toml
[features]
multi_agent = true
```

This enables `spawn_agent`, `wait_agent`, and `close_agent` for skills like `dispatching-parallel-agents` and `subagent-driven-development`.

Legacy note: Codex builds before `rust-v0.115.0` exposed spawned-agent
waiting as `wait`. Current Codex uses `wait_agent` for spawned agents. The
`wait` name now belongs to code-mode `exec/wait`, which resumes a yielded exec
cell by `cell_id`; it is not the spawned-agent result tool.

## Environment Detection
> 【老王注】Codex 沙箱里常遇到 linked worktree / detached HEAD，建 worktree 或收尾分支前先跑这三条只读 git 命令探环境。

Skills that create worktrees or finish branches should detect their
environment with read-only git commands before proceeding:

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

- `GIT_DIR != GIT_COMMON` → already in a linked worktree (skip creation)
- `BRANCH` empty → detached HEAD (cannot branch/push/PR from sandbox)

See `using-git-worktrees` Step 0 and `finishing-a-development-branch`
Step 1 for how each skill uses these signals.

## Codex App Finishing

When the sandbox blocks branch/push operations (detached HEAD in an
externally managed worktree), the agent commits all work and informs
the user to use the App's native controls:

- **"Create branch"** — names the branch, then commit/push/PR via App UI
- **"Hand off to local"** — transfers work to the user's local checkout

The agent can still run tests, stage files, and output suggested branch
names, commit messages, and PR descriptions for the user to copy.
