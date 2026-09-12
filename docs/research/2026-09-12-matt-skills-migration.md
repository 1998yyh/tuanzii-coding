# Matt skills 中文迁移记录（2026-09-12）

## 交付范围

插件版本更新为 4.6.0。提交前同步远端 `e7de244`，保留其 4.5.0 E2E 更新；此前尚未发布的技术配图与本轮 5 个 Matt 技能统一记入 4.6.0。相对远端 41 项，最终技能清单增至 47 项，Matt 来源从 29 项增至 34 项。

新增 `implement-spec`、`setup-ts-deep-modules`、`writing-fragments`、`writing-shape`、`writing-beats`，全部保留实验版及仅限用户显式调用的设置。正文、描述、示例中文化，英文名称与技术标识保留；`agents/openai.yaml` 和 dependency-cruiser 配置模板与固定上游逐字节一致。

同步已有技能的 setup 调用契约、调试后的可选架构建议、wait-what 多 context 路由、追问依赖的分别加载与同轮分隔线。wayfinder 的“一次一问”小节与修改前逐字一致。domain-modeling 现有触发已覆盖上游修改，无需重写。

`retro` 仍属上游 STUB，`loop-me` 和 `claude-handoff` 本轮暂缓，三者未注册。固定来源及迁移取舍见 [调研报告](2026-09-12-matt-skills-upstream.md) 和 [NOTICE](../../NOTICE.mattpocock-skills.md)。

## 验证

- 47 个实际技能目录与清单精确对应，无重复注册；全部 SKILL frontmatter 能被 YAML 解析，名称与目录一致。
- 两份发布清单版本均为 4.6.0；新增项均在 CLAUDE.md、NOTICE 和 ask-matt 中登记。
- 新增 5 项通过 skill-creator 基础验证。该验证器不支持 Claude 的 `disable-model-invocation` 字段，因此先在原文件上检查 Claude 调用字段，再对临时副本移除该字段后运行基础验证；没有删改交付文件的调用设置。
- dependency-cruiser 模板通过 `node --check`，并在仓库之外的临时 TypeScript 项目中实跑。未给本仓库安装依赖。
- implement-spec 以 A→B、A→C、B+C→D 的任务图做独立文本场景评审，覆盖两个 worker、B 失败、用户未提交改动、无 Git 写和 PR 权限。评审发现的本地实现缺口与失败集成状态已修复并复核。

## 边界检查实跑

环境：Node v22.22.0、dependency-cruiser 18.2.0、TypeScript 6.0.3。扫描覆盖全部 7 个 TypeScript 模块与实际依赖边。以下退出码来自 `err` 报告模式，JSON 模式用于检查扫描覆盖和规则明细，不能单靠 JSON 命令退出码判断违规。

| 场景 | 退出码 | 触发规则 |
|---|---|---|
| 合法公共入口、本包实现和测试夹具 | 0 | 无 |
| 应用深导入 | 1 | entrypoint-boundary-from-app |
| 恢复应用导入 | 0 | 无 |
| 跨包深导入 | 1 | entrypoint-boundary-across-packages |
| 恢复跨包导入 | 0 | 无 |
| 测试深导入实现 | 1 | tests-through-entrypoints |
| 恢复测试导入 | 0 | 无 |
| 生产代码导入测试夹具 | 1 | tests-folder-is-private |
| 恢复夹具导入 | 0 | 无 |
| 依赖环 | 1 | no-circular |
| 恢复无环状态 | 0 | 无 |

首次安装 TypeScript 7.0.2 时，dependency-cruiser 18.2.0 的 JSON 报告显示 TypeScript 解析器不可用、模块扫描数为 0，但命令退出码为 0。诊断后仅在临时项目切换到兼容的 TypeScript 6.0.3 完成验证；迁移技能已要求检查解析器可用性、实际模块和依赖边，遇到不兼容不能擅自修改目标项目的 TypeScript 版本，也不能宣称完成。规则格式参考 [dependency-cruiser 官方文档](https://github.com/sverweij/dependency-cruiser/blob/main/doc/rules-reference.md)。

## 验证边界

未在已安装的 Claude Code 插件中执行这 5 个入口，未实跑多 agent 整份 spec 交付或真实写作会话。模板行为与静态注册通过不等同于已完成宿主端到端验证。本次没有执行 Git 提交、推送或全局插件安装。

提交前同步核验：保留远端 E2E 代码和入口，合并清单、路由与日志的重叠改动；发布版本仍为 4.6.0。
提交前验证通过：47 个技能与清单一致、4.6.0 版本一致；E2E 契约测试 29 项与 runtime 测试 4 项全部通过。
