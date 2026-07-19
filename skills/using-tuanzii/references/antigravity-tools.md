# Antigravity CLI (`agy`) Tool Mapping

Skills speak in actions ("dispatch a subagent", "create a todo", "read a file"). On the Antigravity CLI (`agy`) these resolve to the tools below.
> 【老王注】给 Antigravity(agy) 用户查的映射表；这个平台差异最大，下面"调 skill""派 subagent""任务追踪"三节都是独特机制，别跳过。

| Action skills request | Antigravity CLI equivalent |
|----------------------|----------------------|
| Read a file | `view_file` |
| Create a new file | `write_to_file` |
| Edit a file | `replace_file_content` |
| Edit a file in several places at once | `multi_replace_file_content` |
| Run a shell command | `run_command` |
| Search file contents | `grep_search` |
| Find files by name / list a directory | `list_dir` (no dedicated glob tool — combine `list_dir` with `grep_search`) |
| Fetch a URL | `read_url_content` |
| Search the web | `search_web` |
| Pose a structured question to your human partner | `ask_question` |
| Dispatch a subagent (`Subagent (general-purpose):` template) | `invoke_subagent` with a built-in `TypeName` — `self` for full-capability work, `research` for read-only (see [Subagent support](#subagent-support)) |
| Multiple parallel dispatches | Multiple entries in one `invoke_subagent` call's `Subagents` array |
| Task tracking ("create a todo", "mark complete") | a **task artifact** — `write_to_file` with `IsArtifact: true` and `ArtifactType: "task"` (see [Task tracking](#task-tracking)). **Not** `manage_task`, which manages background processes. |

## Invoking a skill — read its `SKILL.md`
> 【老王注】关键差异：agy 没有 Skill 工具，正规加载方式就是用 view_file 读 SKILL.md 并带 IsSkillFile: true——在这里"手动读文件"恰恰是官方机制，不算违规。

Antigravity surfaces every installed skill's `name` + `description` to you at the
start of each session, but it has **no `Skill`/`activate_skill` tool**. To load a
skill, **read its `SKILL.md` with `view_file`, setting `IsSkillFile: true`** when
the skill applies — e.g. `view_file` on
`.../plugins/superpowers/skills/<skill-name>/SKILL.md` with `IsSkillFile: true`.
(`IsSkillFile` is agy's own signal that you're reading a file to *execute its
instructions*, not to edit or preview it — set it whenever you load a skill.)

This is the blessed skill-loading mechanism on this harness. The general rule
"never read skill files manually" means "don't bypass your platform's
skill-loading mechanism" — and on Antigravity, reading `SKILL.md` *is* that
mechanism. Reading it honors the rule rather than breaking it.

You already know which skills exist and what they're for: their names and
descriptions are in front of you at session start. When a description matches
what you're about to do, read that skill's `SKILL.md` before acting.

## Subagent support
> 【老王注】派 subagent 默认用内置 self（全能力，能写文件跑命令），只读审查用 research；需要自定义提示词时才 define_subagent。

Antigravity dispatches subagents with `invoke_subagent`, passing each one a
`TypeName` in the `Subagents` array. Two `TypeName`s are **built in** — use them
directly, no `define_subagent` needed:

- **`self`** — a full clone of you, with every tool you have (including
  `write_to_file`/`replace_file_content`/`run_command`). The safe default for
  general-purpose work: implementing, fixing, anything that edits files or runs
  commands.
- **`research`** — read-only (file reading, `grep_search`, web/URL fetch; no write
  or command access). Use it when you specifically want a subagent that can't make
  changes — investigation and read-only review.

Call `define_subagent` only for a custom system prompt or capability mix: set
`enable_write_tools: true` to grant file edits **and** `run_command`,
`enable_subagent_tools` for nested dispatch, `enable_mcp_tools` for MCP. Then
invoke it by the name you gave it. (`manage_subagents` lists/kills running
subagents.)

Skills dispatch with `Subagent (general-purpose):` and either reference a
prompt-template file (e.g. `tuanzii:subagent-driven-development`'s
`./implementer-prompt.md`) or supply an inline prompt. On Antigravity:

| Skill dispatch form | Antigravity equivalent |
|---------------------|----------------------|
| An implementer-style `*-prompt.md` template (writes code, runs tests) | Fill the template, then `invoke_subagent` with `TypeName: "self"` and the filled prompt |
| A read-only reviewer template (`tuanzii:subagent-driven-development`'s `./task-reviewer-prompt.md`) | `invoke_subagent` with `TypeName: "research"` and the filled review template |
| Inline prompt (no template referenced) | `invoke_subagent` with `TypeName: "self"` (or `"research"` if the task only reads) and your inline prompt |

### Prompt filling

Skills provide prompt templates with placeholders like `{WHAT_WAS_IMPLEMENTED}` or
`[FULL TEXT of task]`. Fill all placeholders before passing the complete prompt to
`invoke_subagent`. The prompt template itself contains the agent's role, review
criteria, and expected output format — the subagent will follow it.

### Parallel dispatch

Put multiple entries in a single `invoke_subagent` call's `Subagents` array to run
independent subagent work in parallel. Keep dependent tasks sequential, but do not
serialize independent subagent tasks just to preserve a simpler history.

## Task tracking
> 【老王注】agy 没有 todo 工具：任务清单要落成 task artifact（markdown checklist 文件），manage_task 是管后台进程的，别搞混。

Antigravity has **no todo / `TodoWrite` tool** (`manage_task` manages background
processes — `list`/`kill`/`status`/`send_input` — it is *not* a checklist). When a
skill says to create a todo list or track tasks, maintain a **task artifact**: a
markdown checklist saved with `write_to_file` (`IsArtifact: true`,
`ArtifactMetadata.ArtifactType: "task"`), edited with `replace_file_content` /
`multi_replace_file_content` as you go.

At the start of any multi-step task, create the task artifact listing every step of
your plan. As you complete each step, edit the artifact to mark it done (`- [x]`).
If the plan changes, update the checklist. Keep it current — it is your source of
truth for what remains; once the conversation gets long, re-read it before starting
each step.
