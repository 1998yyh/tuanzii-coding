---
name: writing-plans
description: 已有多步骤任务的规格或需求时，在接触代码之前使用。
---

# 编写计划

## 概述
> 【老王注】写计划时假设实现者对代码库零上下文、品味存疑——文件路径、代码、命令全部写死，别指望他自己去查、去判断。

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. TDD. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

**开始时声明：**“我正在使用 `writing-plans` 技能创建实施计划。”

**上下文：**若在隔离 worktree 中工作，应在执行时通过 `tuanzii:using-git-worktrees` 技能创建它。

**计划保存位置：**`docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`
- 用户对计划位置的偏好优先于此默认位置。

## 范围检查
> 【老王注】跨多个子系统的 spec 必须拆成多份计划——每份计划都要能独立产出可运行、可测试的软件。

If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## 文件结构
> 【老王注】先定文件清单再拆任务：哪些文件新建、哪些改动、各负什么责——分解决策在这一步就锁死了，后面再改代价很大。

Before defining tasks, map out which files will be created or modified and what each one is responsible for. This is where decomposition decisions get locked in.

- Design units with clear boundaries and well-defined interfaces. Each file should have one clear responsibility.
- You reason best about code you can hold in context at once, and your edits are more reliable when files are focused. Prefer smaller, focused files over large ones that do too much.
- Files that change together should live together. Split by responsibility, not by technical layer.
- In existing codebases, follow established patterns. If the codebase uses large files, don't unilaterally restructure - but if a file you're modifying has grown unwieldy, including a split in the plan is reasonable.

This structure informs the task decomposition. Each task should produce self-contained changes that make sense independently.

## 任务粒度控制
> 【老王注】任务要"右尺寸"：每个任务自带测试闭环、能独立交付。脚手架、配置、文档步骤并入用到它们的任务里，不单独成任务。
> 【老王注】拆分标准就一条：评审者有没有可能打回这个任务却放过隔壁那个？没有就别拆。

A task is the smallest unit that carries its own test cycle and is worth a
fresh reviewer's gate. When drawing task boundaries: fold setup,
configuration, scaffolding, and documentation steps into the task whose
deliverable needs them; split only where a reviewer could meaningfully
reject one task while approving its neighbor. Each task ends with an
independently testable deliverable.

## 可执行步骤的粒度
> 【老王注】任务讲右尺寸，步骤讲咬得动——每步 2-5 分钟一个动作：写失败测试、跑、最小实现、跑、提交，五步走就是一个 TDD 微循环。

**每一步只包含一个动作，耗时 2 至 5 分钟：**
- "Write the failing test" - step
- "Run it to make sure it fails" - step
- "Implement the minimal code to make the test pass" - step
- "Run the tests and make sure they pass" - step
- "Commit" - step

## 计划文档头部
> 【老王注】计划头部模板里的 Global Constraints 是重点：版本下限、依赖限制、命名规则等从 spec 逐字照抄，每个任务默认继承，不用在任务里重复写。

**每份计划必须以如下头部开始：**

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use tuanzii:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about approach]

**Tech Stack:** [Key technologies/libraries]

## Global Constraints

[The spec's project-wide requirements — version floors, dependency limits,
naming and copy rules, platform requirements — one line each, with exact
values copied verbatim from the spec. Every task's requirements implicitly
include this section.]

---
```

## 任务结构
> 【老王注】Interfaces 块是任务之间的契约，务必点透：实现 agent 只看得到自己这一个任务，它全靠 Consumes/Produces 知道隔壁任务的函数名、参数和返回类型。
> 【老王注】所以这里必须写精确签名，写糊了任务之间就接不上。

````markdown
### Task N: [Component Name]

**Files:**
- Create: `exact/path/to/file.py`
- Modify: `exact/path/to/existing.py:123-145`
- Test: `tests/exact/path/to/test.py`

**Interfaces:**
- Consumes: [what this task uses from earlier tasks — exact signatures]
- Produces: [what later tasks rely on — exact function names, parameter
  and return types. A task's implementer sees only their own task; this
  block is how they learn the names and types neighboring tasks use.]

- [ ] **Step 1: Write the failing test**

```python
def test_specific_behavior():
    result = function(input)
    assert result == expected
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/path/test.py::test_name -v`
Expected: FAIL with "function not defined"

- [ ] **Step 3: Write minimal implementation**

```python
def function(input):
    return expected
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/path/test.py::test_name -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/path/test.py src/path/file.py
git commit -m "feat: add specific feature"
```
````

## 禁止占位符
> 【老王注】计划里写"TBD"或"加点错误处理"等于没写——实现 agent 只会瞎猜，这算计划事故，不算实现事故。
> 【老王注】"同 Task N"也不行：任务可能乱序执行，代码必须完整重贴。

每一步必须包含工程师所需的实际内容。以下属于**计划失败**，绝不可写入：
- "TBD", "TODO", "implement later", "fill in details"
- "Add appropriate error handling" / "add validation" / "handle edge cases"
- "Write tests for the above" (without actual test code)
- "Similar to Task N" (repeat the code — the engineer may be reading tasks out of order)
- Steps that describe what to do without showing how (code blocks required for code steps)
- References to types, functions, or methods not defined in any task

## 请牢记
- Exact file paths always
- Complete code in every step — if a step changes code, show the code
- Exact commands with expected output
- DRY, YAGNI, TDD, frequent commits

## 自审
> 【老王注】写完自己过三关：spec 每条需求都能指到任务、全文扫描占位符、前后任务的函数名和类型对得上（Task 3 叫 clearLayers、Task 7 叫 clearFullLayers 就是 bug）。

完整计划写完后，以全新的视角重看规格，并据此检查计划。这是自行执行的检查清单，不是子 Agent 派发。

**1. Spec coverage:** Skim each section/requirement in the spec. Can you point to a task that implements it? List any gaps.

**2. Placeholder scan:** Search your plan for red flags — any of the patterns from the "No Placeholders" section above. Fix them.

**3. Type consistency:** Do the types, method signatures, and property names you used in later tasks match what you defined in earlier tasks? A function called `clearLayers()` in Task 3 but `clearFullLayers()` in Task 7 is a bug.

If you find issues, fix them inline. No need to re-review — just fix and move on. If you find a spec requirement with no task, add the task.

## 执行交接
> 【老王注】收尾交给 subagent 驱动执行：每任务派 fresh agent、任务间评审、迭代快。

保存计划后，交接给执行阶段：

**"Plan complete and saved to `docs/superpowers/plans/<filename>.md`. Ready to execute?"**

**执行：**
- **REQUIRED SUB-SKILL:** Use tuanzii:subagent-driven-development
- Fresh subagent per task + two-stage review
