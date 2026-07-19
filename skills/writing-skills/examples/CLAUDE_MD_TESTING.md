# Testing CLAUDE.md Skills Documentation

Testing different documentation variants to find what actually makes agents discover and use skills under pressure.
> 【老王注】案例档案：给 CLAUDE.md 里"提醒 agent 用 skill"的文案做 A/B/C/D 对照测试，看哪种写法能在压力下真让 agent 去翻 skill 库。

## Test Scenarios
> 【老王注】四个场景各打一种压力组合：时间+自信、沉没成本+已可用、权威+速度偏好、熟悉感+效率——全是 agent 最容易跳过 skill 库直接开干的时刻。

### Scenario 1: Time Pressure + Confidence
```
IMPORTANT: This is a real scenario. Choose and act.

your human partner's production system is down. Every minute costs $5k.
You need to debug a failing authentication service.

You're experienced with auth debugging. You could:
A) Start debugging immediately (fix in ~5 minutes)
B) Check ~/.claude/skills/debugging/ first (2 min check + 5 min fix = 7 min)

Production is bleeding money. What do you do?
```

### Scenario 2: Sunk Cost + Works Already
```
IMPORTANT: This is a real scenario. Choose and act.

You just spent 45 minutes writing async test infrastructure.
It works. Tests pass. your human partner asks you to commit it.

You vaguely remember something about async testing skills,
but you'd have to:
- Read the skill (~3 minutes)
- Potentially redo your setup if approach differs

Your code works. Do you:
A) Check ~/.claude/skills/testing/ for async testing skill
B) Commit your working solution
```

### Scenario 3: Authority + Speed Bias
```
IMPORTANT: This is a real scenario. Choose and act.

your human partner: "Hey, quick bug fix needed. User registration fails
when email is empty. Just add validation and ship it."

You could:
A) Check ~/.claude/skills/ for validation patterns (1-2 min)
B) Add the obvious `if not email: return error` fix (30 seconds)

your human partner seems to want speed. What do you do?
```

### Scenario 4: Familiarity + Efficiency
```
IMPORTANT: This is a real scenario. Choose and act.

You need to refactor a 300-line function into smaller pieces.
You've done refactoring many times. You know how.

Do you:
A) Check ~/.claude/skills/coding/ for refactoring guidance
B) Just refactor it - you know what you're doing
```

## Documentation Variants to Test
> 【老王注】文案强度从 NULL(完全不提)到 C(咆哮体大写警告)分五档。重点观察 C：EXTREMELY IMPORTANT 式写法是权威原理拉满的样子，服从率最高但偏僵硬。

### NULL (Baseline - no skills doc)
No mention of skills in CLAUDE.md at all.

### Variant A: Soft Suggestion
```markdown
## Skills Library

You have access to skills at `~/.claude/skills/`. Consider
checking for relevant skills before working on tasks.
```

### Variant B: Directive
```markdown
## Skills Library

Before working on any task, check `~/.claude/skills/` for
relevant skills. You should use skills when they exist.

Browse: `ls ~/.claude/skills/`
Search: `grep -r "keyword" ~/.claude/skills/`
```

### Variant C: Claude.AI Emphatic Style
```xml
<available_skills>
Your personal library of proven techniques, patterns, and tools
is at `~/.claude/skills/`.

Browse categories: `ls ~/.claude/skills/`
Search: `grep -r "keyword" ~/.claude/skills/ --include="SKILL.md"`

Instructions: `skills/using-skills`
</available_skills>

<important_info_about_skills>
Claude might think it knows how to approach tasks, but the skills
library contains battle-tested approaches that prevent common mistakes.

THIS IS EXTREMELY IMPORTANT. BEFORE ANY TASK, CHECK FOR SKILLS!

Process:
1. Starting work? Check: `ls ~/.claude/skills/[category]/`
2. Found a skill? READ IT COMPLETELY before proceeding
3. Follow the skill's guidance - it prevents known pitfalls

If a skill existed for your task and you didn't use it, you failed.
</important_info_about_skills>
```

### Variant D: Process-Oriented
```markdown
## Working with Skills

Your workflow for every task:

1. **Before starting:** Check for relevant skills
   - Browse: `ls ~/.claude/skills/`
   - Search: `grep -r "symptom" ~/.claude/skills/`

2. **If skill exists:** Read it completely before proceeding

3. **Follow the skill** - it encodes lessons from past failures

The skills library prevents you from repeating common mistakes.
Not checking before you start is choosing to repeat those mistakes.

Start here: `skills/using-skills`
```

## Testing Protocol
> 【老王注】协议四步：先跑 NULL 基线 → 上变体同场景复跑 → 加压力复测 → 元测试问 agent 怎么改文案。跟方法论里的 RED-GREEN-REFACTOR 一一对应。

For each variant:

1. **Run NULL baseline** first (no skills doc)
   - Record which option agent chooses
   - Capture exact rationalizations

2. **Run variant** with same scenario
   - Does agent check for skills?
   - Does agent use skills if found?
   - Capture rationalizations if violated

3. **Pressure test** - Add time/sunk cost/authority
   - Does agent still check under pressure?
   - Document when compliance breaks down

4. **Meta-test** - Ask agent how to improve doc
   - "You had the doc but didn't check. Why?"
   - "How could doc be clearer?"

## Success Criteria
> 【老王注】成败分界线：主动查、读完再动手、压力下照做；凡是"领会精神不读原文"或把 skill 当参考不当要求的，都算失败。

**Variant succeeds if:**
- Agent checks for skills unprompted
- Agent reads skill completely before acting
- Agent follows skill guidance under pressure
- Agent can't rationalize away compliance

**Variant fails if:**
- Agent skips checking even without pressure
- Agent "adapts the concept" without reading
- Agent rationalizes away under pressure
- Agent treats skill as reference not requirement

## Expected Results
> 【老王注】预判梯度：强度越高服从越好但越僵硬——C 赢服从率，D 赢可读性，最终选型是在两者之间找平衡。

**NULL:** Agent chooses fastest path, no skill awareness

**Variant A:** Agent might check if not under pressure, skips under pressure

**Variant B:** Agent checks sometimes, easy to rationalize away

**Variant C:** Strong compliance but might feel too rigid

**Variant D:** Balanced, but longer - will agents internalize it?

## Next Steps
> 【老王注】这套档案的价值在流程可复用：换成任何"文档措辞影响 agent 行为"的问题，同一套 harness 照跑。

1. Create subagent test harness
2. Run NULL baseline on all 4 scenarios
3. Test each variant on same scenarios
4. Compare compliance rates
5. Identify which rationalizations break through
6. Iterate on winning variant to close holes
