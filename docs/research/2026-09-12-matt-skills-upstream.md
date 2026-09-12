# Matt Pocock skills 上游检查（2026-09-12）

## 检查范围与版本

本次读取 GitHub 仓库、远程 refs、GitHub Releases API，并临时 clone 完整历史，对比本地声明基线 `v1.2.3` 与检查时的 `main`。仓库没有现存同类研究笔记，结果放在 `docs/research/`。本次只新增调查笔记，不迁移 skill，也不改插件清单或版本。

| 项目 | 核实结果 | 来源 |
|---|---|---|
| 本地 Matt 归属基线 | v1.2.3，29 个已迁入 skill | [本地归属说明](../../NOTICE.mattpocock-skills.md) |
| 最新 tag / release | v1.2.3；2026-08-06 14:05:28 UTC 发布；没有更高版本的已发布 release | [Release](https://github.com/mattpocock/skills/releases/tag/v1.2.3)、[Releases API](https://api.github.com/repos/mattpocock/skills/releases) |
| 基线 commit | `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e` | [固定 commit](https://github.com/mattpocock/skills/commit/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e) |
| 最新 main | `3cca18b368ae95cdbdebbff572ccafa662551015`；2026-09-04 08:43:27 UTC | [固定 commit](https://github.com/mattpocock/skills/commit/3cca18b368ae95cdbdebbff572ccafa662551015) |
| 基线之后 | 41 个 commit（包含 merge commit），skill 数量从 35 增至 37；新增 2、改名 0、删除 0 | [固定范围对比](https://github.com/mattpocock/skills/compare/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e...3cca18b368ae95cdbdebbff572ccafa662551015) |
| main 插件版本与正式清单 | 仍为 1.2.3，登记 25 个 skill；不包含 in-progress 与 misc | [固定插件清单](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/.claude-plugin/plugin.json) |

因此“有更新”指 main 已前进，不能表述为发布了比 v1.2.3 更新的稳定版本。这里的最新只涵盖已合入 main 的内容；未合入分支/PR 不算可迁移的现有 skill。

## 真正新增的两个 skill

二者都在 `skills/in-progress/`。上游明确将该目录定义为 beta，不随正式插件发布，可随时修改或消失。[固定目录说明](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/README.md)

| Skill | 新增日期 | 能力与迁移判断 | 一手来源 |
|---|---|---|---|
| `implement-spec` | 2026-08-21 | 把 spec 的 tickets 当作依赖图；就绪工单由不同 worktree/branch 的 implementer 并行执行，merger 合入一个 PR 分支，最后评审、标记 ready、清理 worktree。比本地 `implement` 的单块实现明显更广，适合整份 spec 的多 agent 交付；建议作为下一项实验性迁移。需适配 Git 写操作授权与平台可用工具。 | [新增 commit](https://github.com/mattpocock/skills/commit/84b5ee5afd738b6a3484e62509b84b3b573c5be3)、[当前固定 SKILL](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/implement-spec/SKILL.md)、[本地 implement](../../skills/engineering/implement/SKILL.md) |
| `retro` | 2026-08-24 | 复盘指定或当前会话，按导航、自动检查、编码标准、全局 AGENTS、工具开销、无效指令、信息可达性给出环境改进候选。能补本地会话复盘缺口，但目录 README 仍标注 **STUB：设计笔记，尚未可用**，不应当作成熟功能原样迁入。与本地 `deepinit` 的完整 CLAUDE 文档策略需要协调。 | [新增 commit](https://github.com/mattpocock/skills/commit/8fa188659c5f102894807854bed9d2eee4a711f4)、[信息访问补充](https://github.com/mattpocock/skills/commit/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76)、[当前固定 SKILL](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/retro/SKILL.md)、[本地 deepinit](../../skills/project/deepinit/SKILL.md) |

以上能力是上游文本描述，未实跑验证。`implement-spec` 的自动创建分支、draft PR、合并、ready 操作，以及 `retro` 的日志访问和文档建议，都要按宿主环境与用户授权做适配。仓库自己的 [CLAUDE.md](../../CLAUDE.md) 明确禁止在用户未主动要求时执行 Git 写操作。

## 本地尚未迁入的六个旧实验技能

以下六个在 v1.2.3 已经存在，不能算本轮新发布。此结论由两个固定树中的 `SKILL.md` 名称集合差分得到：[基线 in-progress](https://github.com/mattpocock/skills/tree/6acc160e4e0cd062dbbbd7a1b26ae92855edf07e/skills/in-progress)、[当前 in-progress](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress)。推荐等级是本次结合本地 skill 职责作出的判断。

| Skill | 用途与本地重叠 | 判断与固定来源 |
|---|---|---|
| `setup-ts-deep-modules` | 用 dependency-cruiser 检查 TypeScript 包入口和模块可见边界，给 `codebase-design` 理念增加可执行约束。 | TypeScript 项目有需求时优先选；[SKILL](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/setup-ts-deep-modules/SKILL.md) |
| `loop-me` | 跨会话追问并生成可实现的工作流 spec；与本地 grilling、to-spec 和 E2E 流程抽离部分重叠。 | 先明确增量再迁；[SKILL](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/loop-me/SKILL.md) |
| `claude-handoff` | 用 `claude --bg` 把当前工作交给新后台 agent；本地 handoff 已能生成交接文档。 | Claude 专用、重叠较高，低优先；[SKILL](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/claude-handoff/SKILL.md) |
| `writing-fragments` | 采访用户并收集文章原材料；与 humanizer 的成文润色职责不同。 | 有文章写作需求再迁；[SKILL](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/writing-fragments/SKILL.md) |
| `writing-shape` | 将原材料逐段整理为文章，讨论每段表达形式。 | 与 fragments 配套按需迁；[SKILL](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/writing-shape/SKILL.md) |
| `writing-beats` | 以叙事节拍推进文章，每次写一个节拍后决定下一步。 | 写作场景按需迁；[SKILL](https://github.com/mattpocock/skills/blob/3cca18b368ae95cdbdebbff572ccafa662551015/skills/in-progress/writing-beats/SKILL.md) |

## 已迁入 skill 值得同步的变化

不要把所有文本差异当成功能升级：2026-08-19 的全仓 em-dash 清理导致许多文件逐行变化，本地已中文重写，应按语义挑选补丁。[全仓文案清理 commit](https://github.com/mattpocock/skills/commit/321658273cb1d20b76026717d027d505790106d4)

| 变化 | 影响与建议 | 固定来源 |
|---|---|---|
| 修复对 user-invoked skill 的自动调用 | `code-review`、`to-spec`、`to-tickets`、`triage`、`wayfinder` 缺 setup 配置时，改为提示用户运行 setup。建议优先同步调用契约，避免把不可自动触发的 skill 当作可调用依赖。 | [修复 commit](https://github.com/mattpocock/skills/commit/1dab98299c3b81f560026c01b7ebf55ed5d91373) |
| `diagnosing-bugs` 删除自动架构复盘转交 | Phase 6 只做 Cleanup，去掉自动转交 user-invoked `improve-codebase-architecture` 的段落。若本地想保留复盘，可改成提出建议，由用户决定是否启动。 | [同一修复 commit](https://github.com/mattpocock/skills/commit/1dab98299c3b81f560026c01b7ebf55ed5d91373) |
| 显式跨 skill 调用，多个依赖分别调用 | `grill-with-docs` 等不再笼统说“用 skill”，而明确要求调用加载工具；两个 skill 对应两次调用。迁移时使用当前宿主的技能加载机制，不能硬编码一个不存在的 Skill 工具。 | [调用标准化](https://github.com/mattpocock/skills/commit/d28dfdc39beadc3142a33359b5cfa4765dcbd0bc)、[多依赖澄清](https://github.com/mattpocock/skills/commit/447ca70872026d5b79d6073a546dac082117fed7) |
| `domain-modeling` 扩清触发条件 | 显式覆盖讨论代码术语、编写/编辑 CONTEXT.md、记录/编辑 ADR。本地若已同义表达则无需机械更新。 | [触发更新](https://github.com/mattpocock/skills/commit/bd8e81baafe43e3e4a3e06f0d256da595edcdeca)、[最终清理](https://github.com/mattpocock/skills/commit/54bc6b604075c18293d38e9e294a2c96f365f104) |
| `wait-what` 支持多个 context | 按 `CONTEXT-MAP.md` 找到正确 `CONTEXT.md`，再使用其词汇重新解释。本地缺少这条，值得补齐。 | [修复 commit](https://github.com/mattpocock/skills/commit/d6cd26f7f245e67ea7d0554a2fe468cd9def6e6f)、[本地 SKILL](../../skills/productivity/wait-what/SKILL.md) |
| `grilling` 同轮问题间加分隔线 | 只是展示改进，整轮 frontier 提问机制不变。迁移不能覆盖本地 `wayfinder` 后加的“一次一问”。 | [格式 commit](https://github.com/mattpocock/skills/commit/85f83d3fde1d3a90d5c9a657f6998c79a6c37308)、[本地 wayfinder](../../skills/engineering/wayfinder/SKILL.md) |
| YAML frontmatter 描述引用 | 给包含英文冒号的 description 加引号，涉及 code-review、setup、to-spec、wait-what 与两个实验写作 skill。中文重写后是否仍受影响，应解析当前文件判断。 | [修复 commit](https://github.com/mattpocock/skills/commit/5c89081d4bbeb3d039a42093653f90bb698d780e) |

2026-09-04 最新合并只改变上游 `scripts/link-skills.sh`：不再将 misc 链到作者的本地 skill 目录；misc 四个 skill 本身没有删除，也不意味着本地应删掉这四项。[固定脚本修改](https://github.com/mattpocock/skills/commit/8666e05d641f6922993616e92c0cf54a85080bd7)

## 建议顺序

1. 先补现有 skill 的调用契约与 `wait-what` 修复；保留本地中文改写和 wayfinder 一次一问定制。
2. 需要完整 spec 并行落地时，适配并迁入 `implement-spec`，明确其 beta 状态。
3. 将 `retro` 留作实验设计候选，完善执行边界和验证后再发布；不要隐去上游 STUB 标识。
4. `setup-ts-deep-modules` 与三个写作 skill 按实际项目需求选择；其余旧实验项优先级较低。

## 验证记录

- `git ls-remote --tags --heads` 核实 main 和 tags；GitHub Releases API 核实 release 日期。
- 临时 clone 用 `git rev-list --count v1.2.3..HEAD`、`git diff --name-status` 和两版 `git ls-tree` 比较提交与 skill 名称集合。
- 阅读新增 skill、in-progress README、插件清单和重点行为变更 commit；候选技能未安装、未实跑。
- 上游事实以本笔记固定的 commit 为准，后续 main 或 release 可能变化。
