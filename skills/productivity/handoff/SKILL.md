---
name: handoff
description: 把当前会话压缩成一份交接文档，供另一个 agent 接手继续工作。当用户说"交接"、"生成交接文档"、"handoff"时触发。
argument-hint: "下一个会话要用来做什么？"
disable-model-invocation: true
---

写一份交接文档，总结当前会话，让一个全新的 agent 能接手继续工作。保存到用户操作系统的临时目录——不要保存到当前工作区。

文档中需包含"建议使用的 skills"一节，列出接手 agent 应该调用的 skill（本插件内 skill 以 `tuanzii:<skill>` 形式引用）。

不要重复其他产物（spec、plan、ADR、issue、commit、diff）已经记录的内容，用路径或 URL 引用即可。

脱敏所有敏感信息，如 API key、密码或个人身份信息。

如果用户传了参数，把它当作下一个会话的工作重点，并据此调整文档内容。
