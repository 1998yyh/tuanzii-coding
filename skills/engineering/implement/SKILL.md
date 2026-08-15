---
name: implement
description: "根据 spec 或一组 tickets 实现一项工作。当用户说“实现”、“按 spec 开发”、“implement”时触发。"
disable-model-invocation: true
---

实现用户在 spec 或 tickets 中描述的工作。

在预先约定好的 seam 处，尽可能使用 tuanzii:tdd。

定期运行 typecheck 和单个测试文件；完整测试套件只在最后跑一次。

完成后，使用 tuanzii:code-review 评审本次工作。

把工作成果提交到当前分支。
