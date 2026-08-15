---
name: setup-matt-pocock-skills
description: 为当前仓库配置本插件的工程 skills 所需的运行环境——设置 issue tracker、triage label 词汇表和领域文档布局。首次使用其他工程 skills 前运行一次。当用户说"初始化工程配置"、"配置 issue tracker"、"setup skills"时触发。
disable-model-invocation: true
---

# 初始化工程 Skills 配置

为当前仓库生成工程 skills 所依赖的配置：

- **Issue tracker** —— issue 存放在哪里（默认 GitHub；也内置支持本地 markdown）
- **Triage labels** —— 五个标准 triage 角色对应的 label 字符串
- **领域文档** —— `CONTEXT.md` 与 ADR 的存放位置，以及读取它们的消费方规则

本 skill 是对话驱动的流程，不是确定性脚本。先探索、再汇报发现、与用户确认、最后写入。

## 流程

### 1. 探索

查看当前仓库的初始状态。有什么读什么，不要臆测：

- `git remote -v` 和 `.git/config` —— 这是 GitHub 仓库吗？是哪一个？
- 仓库根目录的 `AGENTS.md` 和 `CLAUDE.md` —— 是否存在？其中是否已有 `## Agent skills` 小节？
- 仓库根目录的 `CONTEXT.md` 和 `CONTEXT-MAP.md`
- `docs/adr/` 以及任何 `src/*/docs/adr/` 目录
- `docs/agents/` —— 本 skill 之前的产出是否已存在？
- `.scratch/` —— 存在则说明已在用本地 markdown 作为 issue tracker
- 是否安装了 `triage` skill？（与本 skill 同级的 `triage` 目录，或可用 skills 列表中的 `triage`。）这决定 Section B 是否需要执行。
- monorepo 信号 —— `pnpm-workspace.yaml`、`package.json` 中的 `workspaces` 字段、或带有独立 `src/` 的 `packages/*`。只在真正大型的多包仓库中才会出现；没有这些信号即为单上下文布局，绝大多数仓库属于此类。

### 2. 汇报发现并提问

总结哪些已存在、哪些缺失。然后按顺序逐个处理各小节——一个小节、一个答案、再进行下一个。

每个小节先给出推荐答案，让用户一个字就能确认。只在选择真正产生分支时给一行解释；探索已经定论的小节直接跳过（`triage` 未安装时跳过 Section B，非 monorepo 时跳过 Section C）。

**Section A —— Issue tracker。**

> 解释：issue tracker 是本仓库 issue 的存放地。`tuanzii:to-tickets`、`tuanzii:triage`、`tuanzii:to-spec` 等 skill 需要读写它——它们必须知道该调用 `gh issue create`、在 `.scratch/` 下写 markdown 文件，还是遵循你描述的其他工作流。选你实际用来跟踪工作的那个。

默认立场：这套 skills 是为 GitHub 设计的。如果 `git remote` 指向 GitHub，推荐 GitHub；指向 GitLab（`gitlab.com` 或自托管），推荐 GitLab。其他情况（或用户另有偏好）提供以下选项：

- **GitHub** —— issue 存放在仓库的 GitHub Issues（使用 `gh` CLI）
- **GitLab** —— issue 存放在仓库的 GitLab Issues（使用 [`glab`](https://gitlab.com/gitlab-org/cli) CLI）
- **本地 markdown** —— issue 以文件形式存放在本仓库 `.scratch/<feature>/` 下（适合个人项目或无远程仓库的场景）
- **其他**（Jira、Linear 等）—— 请用户用一段话描述工作流；本 skill 会以自由文本形式记录

把选择记录到 `docs/agents/issue-tracker.md`。GitHub 和 GitLab 模板带有一个"PR 作为需求来源"开关，默认**关闭**——保持关闭，不要主动提起；想让外部 PR 进入 triage 队列的用户可以日后自行在文件中打开。

**Section B —— Triage label 词汇表。** 如果 `triage` skill 未安装（探索阶段已确认），整节跳过——未安装的 skill 不需要 label。

如果已安装，只问一个问题：

> 是否保留默认的 triage label？（推荐：**是**）

默认值是五个标准角色，label 字符串与角色名相同：`needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix`。回答**是**就原样写入。仅当用户回答否——通常因为他们的 tracker 已经在用别的名字（如用 `bug:triage` 代替 `needs-triage`）——才收集覆盖项，让 `triage` 复用现有 label 而不是创建重复项。

**Section C —— 领域文档。** 默认采用**单上下文**——仓库根目录一个 `CONTEXT.md` + `docs/adr/`。这适合几乎所有仓库，直接写入，不用问。

仅当探索发现 monorepo 信号时才提供**多上下文**选项——根目录一个 `CONTEXT-MAP.md`，指向各上下文自己的 `CONTEXT.md`。此时与用户确认要哪种布局。

### 3. 确认并修改

向用户展示以下草稿：

- 要加入 `CLAUDE.md` / `AGENTS.md` 的 `## Agent skills` 区块（编辑哪个文件的选择规则见第 4 步）
- `docs/agents/issue-tracker.md`、`docs/agents/domain.md`、`docs/agents/triage-labels.md` 的内容（最后一个仅在 `triage` 已安装时生成）

写入前让用户修改。

### 4. 写入

**选择要编辑的文件：**

- 如果 `CLAUDE.md` 存在，编辑它。
- 否则如果 `AGENTS.md` 存在，编辑它。
- 如果都不存在，问用户要创建哪一个——不要替用户决定。

`CLAUDE.md` 已存在时绝不创建 `AGENTS.md`（反之亦然）——永远编辑已存在的那个。

如果所选文件中已有 `## Agent skills` 区块，就地更新其内容，不要追加重复区块。不要覆盖用户对周边段落的修改。

区块内容：

```markdown
## Agent skills

### Issue tracker

[一句话说明 issue 跟踪在哪里]。见 `docs/agents/issue-tracker.md`。

### Triage labels

[一句话说明 label 词汇表]。见 `docs/agents/triage-labels.md`。

### Domain docs

[一句话说明布局——"单上下文"或"多上下文"]。见 `docs/agents/domain.md`。
```

仅当 `triage` 已安装且 Section B 执行过，才包含 `### Triage labels` 子区块并写入 `docs/agents/triage-labels.md`；否则两者都省略。

然后以本 skill 目录下的种子模板为起点写入各文档文件：

- [issue-tracker-github.md](./issue-tracker-github.md) —— GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md) —— GitLab issue tracker
- [issue-tracker-local.md](./issue-tracker-local.md) —— 本地 markdown issue tracker
- [triage-labels.md](./triage-labels.md) —— label 映射（仅在 `triage` 已安装时）
- [domain.md](./domain.md) —— 领域文档消费方规则 + 布局

对于"其他"类 issue tracker，根据用户的描述从零撰写 `docs/agents/issue-tracker.md`。

### 5. 完成

告知用户配置已完成，以及哪些工程 skills 将读取这些文件。提醒用户之后可以直接编辑 `docs/agents/*.md`——只有想更换 issue tracker 或推倒重来时才需要重新运行本 skill。
