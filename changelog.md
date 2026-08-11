# Changelog

本文件记录 tuanzii Claude Code 插件的重要变更。插件版本以 `.claude-plugin/plugin.json` 和 `.claude-plugin/marketplace.json` 为准。

## [3.1.0] - 2026-08-11

### 流程精简

- 移除 `writing-plans` skill；`brainstorming` 完成并获得用户确认后，改由主会话直接产出细粒度实施计划。
- 移除 `writing-skills` skill 及其配套参考资料、示例和渲染脚本。

### 变更

- 更新 `brainstorming`、`subagent-driven-development` 和 `using-tuanzii`，使流程不再依赖已移除的 planning/skill-authoring skill。
- 将 `verification-before-completion` 从重复的强制规则精简为证据门禁：按结论选择充分检查，报告最新证据，并披露未验证项和剩余风险。
- 将 Superpowers 衍生 skill 清单从 11 项调整为 9 项，并同步更新归属说明。

### 文档

- 通过 `deepinit` 增量刷新 `CLAUDE.md`，补充插件发现链路、可执行验证命令和 skill 清单同步规则。
- 更新工程流程索引及当前项目上下文版本。
- 忽略 `.reasonix/` 生成的本地会话元数据，避免进入版本控制。
