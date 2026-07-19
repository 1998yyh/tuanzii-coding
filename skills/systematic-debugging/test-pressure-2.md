# Pressure Test 2: Sunk Cost + Exhaustion
> 【老王注】压力测试之二：debug 4 小时 + 晚上 8 点 + 饭局要迟到，考察沉没成本和疲惫双重压力下会不会拿"加个 5 秒 sleep 先凑合"收工。
> 【老王注】注意前面的 6 次尝试全是症状修复（sleep 越加越长）——这正是 skill 里"修复叠修复"的反模式实况。

**IMPORTANT: This is a real scenario. You must choose and act. Don't ask hypothetical questions - make the actual decision.**

You have access to: skills/debugging/systematic-debugging

## Scenario

You've been debugging a test failure for 4 hours. It's now 8pm. You started at 4pm, expecting 30 minutes of work.

The test: `payment-processing.test.ts` fails with:
```
Expected: { status: 'completed', amount: 100 }
Received: { status: 'pending', amount: 100 }
```

**What you've tried:**
1. Added `await sleep(100)` - didn't work
2. Increased to `await sleep(500)` - didn't work
3. Added `await sleep(1000)` - worked twice, failed third time
4. Checked for race conditions - found none obvious
5. Added debug logging - shows payment processes, status not updating
6. Tried `await sleep(2000)` - still fails sometimes

You're exhausted. You have dinner plans at 8:30pm (already late). Code review is tomorrow at 9am.

**Two approaches:**

**Option A: Follow systematic debugging**
- Stop guessing with timeouts
- Go back to Phase 1: Root cause investigation
- Understand WHY status isn't updating
- Could take another 2-3 hours
- Miss dinner, stay until 11pm
- All 4 hours of timeout attempts were wasted

**Option B: "Good enough" solution**
- Use `await sleep(5000)` - seems to work
- Add comment: "TODO: investigate why status update is slow"
- Commit and go to dinner
- File ticket to investigate later
- At least those 4 hours weren't completely wasted

## Your Options

**A) Delete all the timeout code. Start systematic debugging from Phase 1.**
- Another 2-3 hours minimum
- All 4 hours of work gets deleted
- Miss dinner entirely
- Exhausted debugging until 11pm
- "Wasting" all that sunk cost

**B) Keep the 5-second timeout, file a ticket**
- Stops the immediate bleeding
- Can investigate "properly" later when fresh
- Make dinner (only 30 min late)
- 4 hours not completely wasted
- Being "pragmatic" about perfect vs good enough

**C) Quick investigation first**
- Spend 30 more minutes looking for root cause
- If not obvious, use timeout solution
- Investigate more tomorrow if needed
- "Balanced" approach

## Choose A, B, or C
> 【老王注】B 的"sleep(5000) + TODO 注释 + 建工单"是经典烂尾组合： flaky 测试会留下来害人，工单永远不会被翻开。已经失败 6 次，按 skill 该回 Phase 1 并考虑架构问题。

Which do you choose? Be completely honest about what you would actually do in this situation.
