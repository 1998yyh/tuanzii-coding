# Attribution: mattpocock/skills

本仓库以下 29 个 skill 衍生自 [mattpocock/skills](https://github.com/mattpocock/skills) v1.2.3（均已翻译为中文）：

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
