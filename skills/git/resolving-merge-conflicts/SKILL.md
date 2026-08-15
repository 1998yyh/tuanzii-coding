---
name: resolving-merge-conflicts
description: "当需要解决进行中的 git merge / rebase 合并冲突时使用。触发词：解决冲突、合并冲突、resolve conflict。"
---

1. **看清当前状态**：确认 merge / rebase 进行到哪一步，查看 git 历史与所有冲突文件。

2. **追溯每处冲突的源头**：深入理解每一侧改动为什么存在、原始意图是什么。读 commit message、查对应 PR、查原始 issue / ticket。

3. **逐块解决冲突**：尽可能同时保留两侧意图；确实互斥时，选择符合本次 merge 既定目标的一侧，并注明取舍。**不要**凭空发明新行为。始终完成解决，绝不 `--abort`。

4. 找到项目的**自动化检查**并运行——通常是先 typecheck，再测试，再 format。修掉 merge 引入的一切问题。

5. **完成 merge / rebase**：暂存全部改动并提交。如果是 rebase，持续 `git rebase --continue` 直到所有 commit 重放完毕。
