# Issue tracker：本地 Markdown

本仓库的 issue 和 spec 以 markdown 文件的形式存放在 `.scratch/` 下。

## 约定

- 一个 feature 一个目录：`.scratch/<feature-slug>/`
- spec 是 `.scratch/<feature-slug>/spec.md`
- 实现 issue 一个 ticket 一个文件，放在 `.scratch/<feature-slug>/issues/<NN>-<slug>.md`，从 `01` 开始编号——绝不使用单个合并的 tickets 文件
- Triage 状态记录为每个 issue 文件顶部附近的一行 `Status:`（角色字符串见 `triage-labels.md`）
- 评论和对话历史追加到文件底部的 `## Comments` 标题下

## 当 skill 说"发布到 issue tracker"

在 `.scratch/<feature-slug>/` 下创建新文件（需要时先创建目录）。

## 当 skill 说"获取相关 ticket"

读取所引用路径下的文件。用户通常会直接传入路径或 issue 编号。

## Wayfinding 操作

供 `tuanzii:wayfinder` 使用。**map** 是一个文件，每个 ticket 一个 **child** 文件。

- **Map**：`.scratch/<effort>/map.md`——承载 Notes / Decisions-so-far / Fog 的正文。
- **Child ticket**：`.scratch/<effort>/issues/NN-<slug>.md`，从 `01` 开始编号，问题写在正文中。一行 `Type:` 记录 ticket 类型（`research`/`prototype`/`grilling`/`task`）；一行 `Status:` 记录 `claimed`/`resolved`。
- **阻塞关系**：顶部附近一行 `Blocked by: NN, NN`。所列文件全部为 `resolved` 后，ticket 解除阻塞。
- **Frontier**：扫描 `.scratch/<effort>/issues/`，找出未解决、未阻塞、未认领的文件；编号最小的胜出。
- **认领**：设为 `Status: claimed` 并保存，然后再开始任何工作。
- **解决**：在 `## Answer` 标题下追加答案，设为 `Status: resolved`，然后向 `map.md` 中 map 的 Decisions-so-far 追加一条上下文指针（gist + 链接）。
