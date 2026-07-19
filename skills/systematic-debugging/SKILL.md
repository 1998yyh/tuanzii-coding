---
name: systematic-debugging
description: 遇到任何缺陷、测试失败或意外行为时，在提出修复方案之前使用。
---

# 系统化调试

## 概述
> 【老王注】这一节定调：随机乱改既浪费时间又制造新 bug，快补丁只是把底层问题盖住。
> 【老王注】核心原则一句话：先找根因再动手，症状修复就是失败——你压住的那个报错只是替罪羊。

随机修复会浪费时间并制造新缺陷；快速补丁只会掩盖底层问题。

**核心原则：**尝试修复前必须先找到根因；只修复症状就是失败。

**违反本流程的字面要求，同样是违反调试的精神。**

## 铁律
> 【老王注】铁律：没做根因调查就不许提修复方案。Phase 1 没走完，后面一切免谈。

```
未先调查根因，不得修复
```

未完成阶段一，就不能提出修复方案。

## 何时使用
> 【老王注】任何技术问题都适用。越是时间紧、越想"就改这一下试试"的时候，越要走这套流程——急着跳步必然返工。

适用于**任何**技术问题：
- 测试失败
- 生产环境缺陷
- 意外行为
- 性能问题
- 构建失败
- 集成问题

**尤其在以下情况使用：**
- 时间紧迫，紧急情况容易诱发猜测
- “只做一个快速修复”看起来很明显
- 已经尝试过多个修复
- 之前的修复没有生效
- 尚未完全理解问题

**不得因以下原因跳过：**
- 问题看似简单，简单缺陷也有根因
- 赶时间，仓促必然返工
- 管理者要求立刻修复，系统化排查比反复试错更快

## 四个阶段
> 【老王注】四个阶段是硬门槛：必须走完当前阶段才能进下一个，不许跳步。顺序是 查根因 → 找模式 → 提假设并验证 → 实施修复。

必须完成当前阶段后才能进入下一阶段。

### 阶段一：根因调查
> 【老王注】阶段一只做一件事：取证。逐行读报错、稳定复现、查最近改动——复现不出来就继续收集数据，别猜。

**尝试任何修复之前：**

1. **仔细阅读错误信息**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **稳定复现**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?
   - If not reproducible → gather more data, don't guess

3. **检查近期改动**
   - What changed that could cause this?
   - Git diff, recent commits
   - New dependencies, config changes
   - Environmental differences

4. **在多组件系统中收集证据**

   **WHEN system has multiple components (CI → build → signing, API → service → database):**

   **BEFORE proposing fixes, add diagnostic instrumentation:**
   ```
   For EACH component boundary:
     - Log what data enters component
     - Log what data exits component
     - Verify environment/config propagation
     - Check state at each layer

   Run once to gather evidence showing WHERE it breaks
   THEN analyze evidence to identify failing component
   THEN investigate that specific component
   ```

   **Example (multi-layer system):**
   ```bash
   # Layer 1: Workflow
   echo "=== Secrets available in workflow: ==="
   echo "IDENTITY: ${IDENTITY:+SET}${IDENTITY:-UNSET}"

   # Layer 2: Build script
   echo "=== Env vars in build script: ==="
   env | grep IDENTITY || echo "IDENTITY not in environment"

   # Layer 3: Signing script
   echo "=== Keychain state: ==="
   security list-keychains
   security find-identity -v

   # Layer 4: Actual signing
   codesign --sign "$IDENTITY" --verbose=4 "$APP"
   ```

   **This reveals:** Which layer fails (secrets → workflow ✓, workflow → build ✗)

5. **追踪数据流**

   **WHEN error is deep in call stack:**

   See `root-cause-tracing.md` in this directory for the complete backward tracing technique.

   **Quick version:**
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source
   - Fix at source, not at symptom
> 【老王注】多组件系统（CI→构建→签名、API→服务→数据库）的关键打法：先在每个组件边界埋日志取证——进什么数据、出什么数据、环境变量传没传到——跑一次看断在哪一层，再扎进那一层细查，别靠猜决定修哪个组件。

### 阶段二：模式分析
> 【老王注】阶段二找参照物：在代码库里找能跑通的相似实现，逐行读完再对比差异——"那点差别应该不碍事"往往就是病根。

**修复前先找到模式：**

1. **Find Working Examples**
   - Locate similar working code in same codebase
   - What works that's similar to what's broken?

2. **Compare Against References**
   - If implementing pattern, read reference implementation COMPLETELY
   - Don't skim - read every line
   - Understand the pattern fully before applying

3. **Identify Differences**
   - What's different between working and broken?
   - List every difference, however small
   - Don't assume "that can't matter"

4. **Understand Dependencies**
   - What other components does this need?
   - What settings, config, environment?
   - What assumptions does it make?

### 阶段三：提出假设并测试
> 【老王注】阶段三走科学方法：一次只提一个假设、一次只改一个变量。验证失败就换新假设，绝不把多个修复叠在一起——叠了就分不清哪一刀起的作用。

**科学方法：**

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Write it down
   - Be specific, not vague

2. **Test Minimally**
   - Make the SMALLEST possible change to test hypothesis
   - One variable at a time
   - Don't fix multiple things at once

3. **Verify Before Continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form NEW hypothesis
   - DON'T add more fixes on top

4. **When You Don't Know**
   - Say "I don't understand X"
   - Don't pretend to know
   - Ask for help
   - Research more

### 阶段四：实施
> 【老王注】阶段四才许动手：先写一个能复现 bug 的失败测试，再修根因，一次只改一处，"顺手优化"是禁令。

**修复根因，而非症状：**

1. **Create Failing Test Case**
   - Simplest possible reproduction
   - Automated test if possible
   - One-off test script if no framework
   - MUST have before fixing
   - Use the `tuanzii:test-driven-development` skill for writing proper failing tests

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time
   - No "while I'm here" improvements
   - No bundled refactoring

3. **Verify Fix**
   - Test passes now?
   - No other tests broken?
   - Issue actually resolved?

4. **If Fix Doesn't Work**
   - STOP
   - Count: How many fixes have you tried?
   - If < 3: Return to Phase 1, re-analyze with new information
   - **If ≥ 3: STOP and question the architecture (step 5 below)**
   - DON'T attempt Fix #4 without architectural discussion

5. **If 3+ Fixes Failed: Question Architecture**

   **Pattern indicating architectural problem:**
   - Each fix reveals new shared state/coupling/problem in different place
   - Fixes require "massive refactoring" to implement
   - Each fix creates new symptoms elsewhere

   **STOP and question fundamentals:**
   - Is this pattern fundamentally sound?
   - Are we "sticking with it through sheer inertia"?
   - Should we refactor architecture vs. continue fixing symptoms?

   **Discuss with your human partner before attempting more fixes**

   This is NOT a failed hypothesis - this is a wrong architecture.
> 【老王注】熔断机制记住这条：连续 3 次修复失败 = 架构问题，不是假设没猜对。每修一处又冒新症状、修复要做"大重构"才能落地，都是架构报警信号。停手，先和人讨论要不要换架构，别试第 4 刀。

## 红旗：停止并遵循流程
> 【老王注】红旗清单：脑子里冒出"先快修一下回头再查""多改几处一起跑测试"这类念头，就是在给自己找借口——全部意味着停手回 Phase 1。

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "Add multiple changes, run tests"
- "Skip the test, I'll manually verify"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- "Pattern says X but I'll adapt it differently"
- "Here are the main problems: [lists fixes without investigation]"
- Proposing solutions before tracing data flow
- **"One more fix attempt" (when already tried 2+)**
- **Each fix reveals new problem in different place**

**出现以上任一情况，都表示必须停止并返回阶段一。**

**若 3 次以上修复失败：**质疑架构，见阶段四的第 5 步。

## 人类协作者指出方向错误的信号
> 【老王注】搭档的这些话都是纠偏信号："你验证过吗""别猜了""再往深想一层"——听到就停，回 Phase 1。

**留意这些纠偏信号：**
- "Is that not happening?" - You assumed without verifying
- "Will it show us...?" - You should have added evidence gathering
- "Stop guessing" - You're proposing fixes without understanding
- "Ultra-think this" - Question fundamentals, not just symptoms
- "We're stuck?" (frustrated) - Your approach isn't working

**看到这些信号时：**停止并返回阶段一。

## 常见自我辩解
> 【老王注】自我合理化对照表：左边是你对自己说的借口，右边是现实。最毒的一条是"再来最后一刀"——失败 3 次以上就该质疑架构，而不是继续修。

| 借口 | 事实 |
|--------|---------|
| "Issue is simple, don't need process" | Simple issues have root causes too. Process is fast for simple bugs. |
| "Emergency, no time for process" | Systematic debugging is FASTER than guess-and-check thrashing. |
| "Just try this first, then investigate" | First fix sets the pattern. Do it right from the start. |
| "I'll write test after confirming fix works" | Untested fixes don't stick. Test first proves it. |
| "Multiple fixes at once saves time" | Can't isolate what worked. Causes new bugs. |
| "Reference too long, I'll adapt the pattern" | Partial understanding guarantees bugs. Read it completely. |
| "I see the problem, let me fix it" | Seeing symptoms ≠ understanding root cause. |
| "One more fix attempt" (after 2+ failures) | 3+ failures = architectural problem. Question pattern, don't fix again. |

## 快速参考
> 【老王注】速查表：四阶段各自干什么、什么算过关，卡壳时回来对一下。

| 阶段 | 关键活动 | 成功标准 |
|-------|---------------|------------------|
| **1. 根因** | 阅读错误、复现、检查改动、收集证据 | 理解是什么以及为什么 |
| **2. 模式** | 寻找可工作的示例并比较 | 找出差异 |
| **3. 假设** | 提出理论并做最小测试 | 验证或提出新假设 |
| **4. 实施** | 创建测试、修复、验证 | 缺陷解决，测试通过 |

## 当流程显示“没有根因”时
> 【老王注】真有查不出根因的情况（环境、时序、外部依赖）：走完整流程、记录排查过程、加监控收尾。但 95% 的"查不出根因"其实是没查完。

If systematic investigation reveals issue is truly environmental, timing-dependent, or external:

1. You've completed the process
2. Document what you investigated
3. Implement appropriate handling (retry, timeout, error message)
4. Add monitoring/logging for future investigation

**But:** 95% of "no root cause" cases are incomplete investigation.

## 支持技术
> 【老王注】本目录配套三件工具：回溯调用链找根因、分层校验让 bug 在结构上不可能、用条件轮询替掉拍脑袋的 sleep。

以下技术属于系统化调试，并位于本目录中：

- **`root-cause-tracing.md`** - Trace bugs backward through call stack to find original trigger
- **`defense-in-depth.md`** - Add validation at multiple layers after finding root cause
- **`condition-based-waiting.md`** - Replace arbitrary timeouts with condition polling

**相关技能：**
- **tuanzii:test-driven-development** - For creating failing test case (Phase 4, Step 1)
- **tuanzii:verification-before-completion** - Verify fix worked before claiming success

## 实际成效
> 【老王注】实测对比：系统化排查 15-30 分钟修完、一次成功率 95%；乱改要折腾 2-3 小时还容易带进新 bug。

来自调试会话的数据：
- 系统化方法：15 至 30 分钟修复
- 随机修复方法：2 至 3 小时反复试错
- 首次修复成功率：95% 对 40%
- 引入新缺陷：接近零 对 经常发生
