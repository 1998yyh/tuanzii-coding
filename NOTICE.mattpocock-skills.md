# Attribution: mattpocock/skills

本仓库共 34 个 skill 衍生自 [mattpocock/skills](https://github.com/mattpocock/skills)（均已翻译为中文）。下面原有 29 个以 v1.2.3 为迁移基线；2026-09-12 选择性同步主分支修复，并从同一固定提交另迁入 5 个实验版 skill。没有将原有技能整体覆盖为上游最新版。

本轮固定来源：[3cca18b368ae95cdbdebbff572ccafa662551015](https://github.com/mattpocock/skills/tree/3cca18b368ae95cdbdebbff572ccafa662551015)（2026-09-04）。

## 原有技能（29 个）

**`skills/grilling/`（追问与领域建模，4 个）**

- `grilling/` —— 连环追问核心引擎（design tree / frontier 机制）
- `grill-me/` —— `/grill-me` 追问入口（对应原仓库 `skills/productivity/grill-me/`）
- `grill-with-docs/` —— 追问 + 领域建模文档入口
- `domain-modeling/` —— 领域建模：维护 `CONTEXT.md` 词汇表与 ADR（含 `CONTEXT-FORMAT.md`、`ADR-FORMAT.md`）

**`skills/engineering/`（工程流水线，15 个，均对应原仓库 `skills/engineering/`）**

- `ask-matt/` —— skill 路由入口
- `codebase-design/` —— 深模块设计共享词汇库
- `code-review/` —— 双轴评审（规范 + spec）
- `diagnosing-bugs/` —— 疑难 bug / 性能回退诊断循环
- `improve-codebase-architecture/` —— 架构改进机会扫描 + HTML 报告
- `implement/` —— 按 spec / 工单实现
- `prototype/` —— 一次性原型验证设计问题
- `research/` —— 高信任一手资料调研并落盘
- `tdd/` —— 测试驱动开发
- `to-spec/` —— 对话综合为 spec 发布到 issue tracker
- `to-tickets/` —— 计划/spec 拆分为 tracer-bullet 工单
- `triage/` —— issue / PR 状态机分诊
- `wayfinder/` —— 超大规模工作的决策工单地图
- `wizard/` —— 生成交互式 bash 向导引导人工操作
- `setup-matt-pocock-skills/` —— 一次性初始化 issue tracker / 标签 / 文档布局

**`skills/productivity/`（效率，5 个，均对应原仓库 `skills/productivity/`）**

- `handoff/` —— 对话压缩为交接文档
- `teach/` —— 在工作区内教学新技能/概念
- `to-questionnaire/` —— 决策转为问卷
- `wait-what/` —— 重新表达未讲清的上一条消息
- `writing-for-agents/` —— 写给 agent 的文档（skill、AGENTS.md、CLAUDE.md）

**`skills/git/`（Git 补充，3 个）**

- `resolving-merge-conflicts/` —— 解决 merge/rebase 冲突（原仓库 `skills/engineering/`）
- `git-guardrails-claude-code/` —— Claude Code 钩子拦截危险 git 命令（原仓库 `skills/misc/`）
- `setup-pre-commit/` —— Husky + lint-staged 预提交钩子（原仓库 `skills/misc/`）

**`skills/misc/`（杂项，2 个，均对应原仓库 `skills/misc/`）**

- `migrate-to-shoehorn/` —— 测试 `as` 断言迁移到 @total-typescript/shoehorn
- `scaffold-exercises/` —— 课程练习目录脚手架

## 实验版迁入（5 个，2026-09-12）

均来自上游 `skills/in-progress/`，上游尚未纳入正式插件；本仓库保留实验状态与仅限用户显式调用的设置。

| 本地路径 | 上游路径 | 用途 |
|---|---|---|
| `skills/engineering/implement-spec/` | `skills/in-progress/implement-spec/` | 按工单依赖并行实现整份 spec，汇总为一个 PR |
| `skills/engineering/setup-ts-deep-modules/` | `skills/in-progress/setup-ts-deep-modules/` | TypeScript 包入口与模块边界检查 |
| `skills/writing/writing-fragments/` | `skills/in-progress/writing-fragments/` | 采访并收集文章素材 |
| `skills/writing/writing-shape/` | `skills/in-progress/writing-shape/` | 将素材逐段组织为文章 |
| `skills/writing/writing-beats/` | `skills/in-progress/writing-beats/` | 按叙事节拍逐步写作 |

翻译正文、描述、参数提示与文档示例；英文技能名和技术标识保留。`agents/openai.yaml` 及 `dependency-cruiser.config.cjs` 保持上游原样。`implement-spec` 适配本项目的 Git/PR 授权、串行汇总与失败处理规则；`setup-ts-deep-modules` 补齐实际配置的 5 条规则说明、应用扫描范围、解析器兼容性与非空扫描校验、现有文件保护。

## 原有技能的选择性同步

- 修复 5 个工程技能自动调用仅限用户触发的 setup 的说明；调试后的架构改进保留为用户可选建议。
- `wait-what` 支持 `CONTEXT-MAP.md` 路由；多个追问入口明确分别加载依赖 skill；`grilling` 同轮问题增加分隔线。
- 保留中文改写和 `wayfinder` 的一次一问定制。`domain-modeling` 现有触发条件已覆盖上游修订，不重复改写；英文 em-dash 清理不机械迁入。
- `retro` 在上游仍标记为 STUB，`loop-me` 与 `claude-handoff` 本轮暂缓，三者均未迁入或注册。

详细对比见 [2026-09-12 调研记录](docs/research/2026-09-12-matt-skills-upstream.md)。

## 许可

原项目以 MIT License 发布，原作者为 Matt Pocock。许可原文如下：

---

MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
