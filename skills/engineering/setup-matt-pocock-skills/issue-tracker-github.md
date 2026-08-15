# Issue tracker：GitHub

本仓库的 issue 和 spec 以 GitHub issue 的形式存在。所有操作使用 `gh` CLI。

## 约定

- **创建 issue**：`gh issue create --title "..." --body "..."`。多行正文用 heredoc。
- **读取 issue**：`gh issue view <number> --comments`，用 `jq` 过滤评论，同时获取 label。
- **列出 issue**：`gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`，按需加 `--label` 和 `--state` 过滤。
- **评论 issue**：`gh issue comment <number> --body "..."`
- **添加 / 移除 label**：`gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **关闭**：`gh issue close <number> --comment "..."`

从 `git remote -v` 推断仓库——在 clone 内运行时 `gh` 会自动完成。

## PR 作为 triage 来源

**PR 作为需求来源：否。** _（如果本仓库把外部 PR 当作 feature request 处理，改为 `yes`；`tuanzii:triage` 会读取这个开关。）_

设为 `yes` 时，PR 与 issue 走相同的 label 和状态，使用对应的 `gh pr` 命令：

- **读取 PR**：`gh pr view <number> --comments`，diff 用 `gh pr diff <number>`。
- **列出待 triage 的外部 PR**：`gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments`，然后只保留 `authorAssociation` 为 `CONTRIBUTOR`、`FIRST_TIME_CONTRIBUTOR` 或 `NONE` 的（丢弃 `OWNER`/`MEMBER`/`COLLABORATOR`）。
- **评论 / 打 label / 关闭**：`gh pr comment`、`gh pr edit --add-label`/`--remove-label`、`gh pr close`。

GitHub 的 issue 和 PR 共用一个编号空间，所以裸的 `#42` 可能是任意一种——先用 `gh pr view 42` 解析，失败后回退到 `gh issue view 42`。

## 当 skill 说"发布到 issue tracker"

创建一个 GitHub issue。

## 当 skill 说"获取相关 ticket"

运行 `gh issue view <number> --comments`。

## Wayfinding 操作

供 `tuanzii:wayfinder` 使用。**map** 是一个单独的 issue，**child** issue 即 ticket。

- **Map**：一个带 `wayfinder:map` label 的 issue，正文承载 Notes / Decisions-so-far / Fog。`gh issue create --label wayfinder:map`。
- **Child ticket**：作为 GitHub sub-issue 关联到 map 的 issue（通过 sub-issues 端点的 `gh api`）。sub-issue 不可用时，把 child 加入 map 正文中的 task list，并在 child 正文顶部写 `Part of #<map>`。Label：`wayfinder:<type>`（`research`/`prototype`/`grilling`/`task`）。认领后，ticket 指派给推进的开发者。
- **阻塞关系**：GitHub 的**原生 issue 依赖**——权威的、UI 可见的表示。添加边：`gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`，其中 `<blocker-db-id>` 是阻塞方的数字 **database id**（`gh api repos/<owner>/<repo>/issues/<n> --jq .id`，_不是_ `#number` 或 `node_id`）。GitHub 在 `issue_dependencies_summary.blocked_by` 中报告（仅未关闭的阻塞方——这是实时门禁）。依赖功能不可用时，回退为在 child 正文顶部写一行 `Blocked by: #<n>, #<n>`。所有阻塞方都关闭后，ticket 解除阻塞。
- **Frontier 查询**：列出 map 的未关闭 child（`gh issue list --state open`，限定在 map 的 sub-issue / task list 范围内），丢弃有未关闭阻塞方（`issue_dependencies_summary.blocked_by > 0`，或 `Blocked by` 行中存在未关闭 issue）或已有 assignee 的；map 顺序中排第一的胜出。
- **认领**：`gh issue edit <n> --add-assignee @me`——会话的第一次写入。
- **解决**：`gh issue comment <n> --body "<answer>"`，然后 `gh issue close <n>`，再向 map 的 Decisions-so-far 追加一条上下文指针（gist + 链接）。
