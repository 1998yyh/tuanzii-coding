# Issue tracker：GitLab

本仓库的 issue 和 spec 以 GitLab issue 的形式存在。所有操作使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI。

## 约定

- **创建 issue**：`glab issue create --title "..." --description "..."`。多行描述用 heredoc。传 `--description -` 打开编辑器。
- **读取 issue**：`glab issue view <number> --comments`。需要机器可读输出时用 `-F json`。
- **列出 issue**：`glab issue list -F json`，按需加 `--label` 过滤。
- **评论 issue**：`glab issue note <number> --message "..."`。GitLab 把评论称为 "note"。
- **添加 / 移除 label**：`glab issue update <number> --label "..."` / `--unlabel "..."`。多个 label 可用逗号分隔或重复该 flag。
- **关闭**：`glab issue close <number>`。`glab issue close` 不接受关闭评论，所以先用 `glab issue note <number> --message "..."` 发出说明，再关闭。
- **Merge request**：GitLab 把 PR 称为 "merge request"。使用 `glab mr create`、`glab mr view`、`glab mr note` 等——与 `gh pr ...` 形状相同，只是用 `mr` 替换 `pr`，用 `note`/`--message` 替换 `comment`/`--body`。

从 `git remote -v` 推断仓库——在 clone 内运行时 `glab` 会自动完成。

## Merge request 作为 triage 来源

**MR 作为需求来源：否。** _（如果本仓库把外部 merge request 当作 feature request 处理，改为 `yes`；`tuanzii:triage` 会读取这个开关。）_

设为 `yes` 时，MR 与 issue 走相同的 label 和状态，使用对应的 `glab mr` 命令：

- **读取 MR**：`glab mr view <number> --comments`，diff 用 `glab mr diff <number>`。
- **列出待 triage 的外部 MR**：`glab mr list -F json`，然后只保留作者不是项目 member/owner 的 MR（贡献者的 MR，而不是维护者进行中的工作）。
- **评论 / 打 label / 关闭**：`glab mr note`、`glab mr update --label`/`--unlabel`、`glab mr close`。

与 GitHub 不同，GitLab 的 issue 和 MR 编号相互独立，所以只要知道维护者指的是哪个来源，`#42` 就没有歧义。

## 当 skill 说"发布到 issue tracker"

创建一个 GitLab issue。

## 当 skill 说"获取相关 ticket"

运行 `glab issue view <number> --comments`。

## Wayfinding 操作

供 `tuanzii:wayfinder` 使用。**map** 是一个单独的 issue，**child** issue 即 ticket。

- **Map**：一个带 `wayfinder:map` label 的 issue，正文承载 Notes / Decisions-so-far / Fog。`glab issue create --label wayfinder:map`。（在支持原生 epic 的 GitLab 套餐上，也可以用 epic 承载 map；带 label 的 issue 在所有套餐都可用。）
- **Child ticket**：描述顶部带 `Part of #<map>`、label 为 `wayfinder:<type>`（`research`/`prototype`/`grilling`/`task`）的 issue。认领后，ticket 指派给推进的开发者。
- **阻塞关系**：GitLab 的**原生 blocking 链接**——权威的、UI 可见的表示。用 `/blocked_by #<n>` quick action 添加，以 note 形式发出（`glab issue note <child> --message "/blocked_by #<blocker>"`）。原生 blocking 链接是 Premium/Ultimate 功能；在免费套餐（或不可用时）回退为在描述顶部写一行 `Blocked by: #<n>, #<n>`。所有阻塞方都关闭后，ticket 解除阻塞。
- **Frontier 查询**：`glab issue list -F json` 限定在 map 的 child 范围内，丢弃有未关闭阻塞方——指向未关闭 issue 的原生 `blocked_by` 链接（`glab api projects/:id/issues/:iid/links`），或 `Blocked by` 行中存在未关闭 issue——或已有 assignee 的；map 顺序中排第一的胜出。
- **认领**：`glab issue update <n> --assignee @me`——会话的第一次写入。
- **解决**：`glab issue note <n> --message "<answer>"`，然后 `glab issue close <n>`，再向 map 的 Decisions-so-far 追加一条上下文指针（gist + 链接）。
