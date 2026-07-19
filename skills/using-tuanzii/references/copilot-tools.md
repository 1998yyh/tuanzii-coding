# Copilot CLI Tool Mapping

Skills speak in actions ("dispatch a subagent", "create a todo", "read a file"). On Copilot CLI these resolve to the tools below.
> 【老王注】给 Copilot CLI 用户查：没有独立 create/edit 工具，写文件全靠 apply_patch；没有 plan mode，留在主会话里做。

| Action skills request | Copilot CLI equivalent |
|----------------------|----------------------|
| Read a file | `view` |
| Create / edit / delete a file | `apply_patch` (Copilot CLI has no separate create/edit/write tools) |
| Run a shell command | `bash` |
| Search file contents | `rg` (ripgrep; Copilot CLI does not expose a `grep` tool) |
| Find files by name | `glob` |
| Fetch a URL | `web_fetch` |
| Search the web | `web_search` |
| Invoke a skill | `skill` |
| Dispatch a subagent (`Subagent (general-purpose):` template) | `task` with `agent_type: "general-purpose"` (other accepted types: `explore`, `task`, `code-review`, `research`, `configure-copilot`) |
| Multiple parallel dispatches | Multiple `task` calls in one response |
| Subagent status/output/control | `read_agent`, `list_agents`, `write_agent` |
| Task tracking ("create a todo", "mark complete") | `update_todo` |
| Enter / exit plan mode | No equivalent — stay in the main session |

## Instructions file

When a skill mentions "your instructions file", on Copilot CLI this is **`AGENTS.md`** at the repository root. If both `AGENTS.md` and `.github/copilot-instructions.md` are present, Copilot reads both.

## Personal skills directory
> 【老王注】个人 skill 放 ~/.copilot/skills/；跨运行时别名 ~/.agents/skills/ 也认，与 Codex、Gemini 共享。

User-level skills live at **`~/.copilot/skills/`**. Copilot CLI also recognizes the cross-runtime alias **`~/.agents/skills/`**, which is shared with Codex and Gemini CLI. Each skill is a subdirectory containing a `SKILL.md` (with `name` and `description` frontmatter).

## Async shell sessions
> 【老王注】异步 shell 是 Copilot 特色：长命令挂后台拿 shellId，随时读输出/喂输入，适合跑服务、watch 类任务。

Copilot CLI supports persistent async shell sessions:

| Tool | Purpose |
|------|---------|
| `bash` with `mode: "async"` (and optionally `detach: true`) | Start a long-running command in the background; returns a `shellId` |
| `write_bash` | Send input to a running async session |
| `read_bash` | Read output from an async session |
| `stop_bash` | Terminate an async session |
| `list_bash` | List all active shell sessions |

## Additional Copilot CLI tools

| Tool | Purpose |
|------|---------|
| `store_memory` | Persist facts about the codebase for future sessions |
| `report_intent` | Update the UI status line with current intent |
| `sql` | Query the session's SQLite database (todos, metadata) |
| `fetch_copilot_cli_documentation` | Look up Copilot CLI documentation |
| GitHub MCP tools (`github-mcp-server-*`) | Native GitHub API access (issues, PRs, code search) |
