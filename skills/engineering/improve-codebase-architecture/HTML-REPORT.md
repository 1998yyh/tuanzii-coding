# HTML 报告格式

架构评审渲染为操作系统临时目录下的单个自包含 HTML 文件。Tailwind 和 Mermaid 都从 CDN 引入。Mermaid 可靠地处理图状结构的图示；手工 div 和内联 SVG 处理更偏编辑排版的视觉（体量图、剖面图）。两者混用——不要什么都靠 Mermaid，那样会开始显得千篇一律。

## 骨架

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Architecture review — {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* small custom layer for things Tailwind doesn't cover cleanly:
         dashed seam lines, hand-drawn-feeling arrow heads, etc. */
      .seam { stroke-dasharray: 4 4; }
      .leak { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="candidates" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## 页头

仓库名、日期，加一个紧凑的图例：实线框 = module，虚线 = seam，红色箭头 = 泄漏，粗黑框 = deep module。不要介绍性段落——直接进入候选方案。

## 候选卡片

图示承担主要表达。文字要稀疏、平实，直接使用词汇表术语（来自 `tuanzii:codebase-design` skill），不加客套。

每个候选是一个 `<article>`：

- **标题**——简短，点明这次深化（例如“合并 Order 接入流水线”）。
- **徽章行**——推荐强度（`Strong` = emerald，`Worth exploring` = amber，`Speculative` = slate），再加一个依赖类别标签（`in-process`、`local-substitutable`、`ports & adapters`、`mock`）。
- **Files**——等宽字体列表，`font-mono text-sm`。
- **Before / After 图**——核心。两栏并排。模式见下。
- **Problem**——一句话。哪里疼。
- **Solution**——一句话。改什么。
- **Wins**——要点列表，每条尽量短。例如“测试只打一个 interface”、“定价逻辑停止泄漏”、“删掉 4 个浅层 wrapper”。
- **ADR callout**（如适用）——琥珀色底框里的一行字。

不要大段解释。如果一张图需要一段话才能看懂，就重画这张图。

## 图示模式

挑选适合该候选的模式。混着用。不要让每张图长一个样——多样性本身就是目的。

### Mermaid 图（依赖 / 调用流的主力）

当重点是“X 调 Y 调 Z，看看这一团乱麻”时，用 Mermaid 的 `flowchart` 或 `graph`。用 Tailwind 样式的卡片包住它，免得显得突兀。用 classDef 把泄漏的边染红、把 deep module 染深色。时序图很适合表达“before：6 次往返；after：1 次”。

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      A[OrderHandler] --> B[OrderValidator]
      B --> C[OrderRepo]
      C -.leak.-> D[PricingClient]
      classDef leak stroke:#dc2626,stroke-width:2px;
      class C,D leak
  </pre>
</div>
```

### 手工盒子加箭头（当 Mermaid 的布局跟你作对时）

module 用带边框和标签的 `<div>`，箭头用绝对定位在 relative 容器上的内联 SVG `<line>` 或 `<path>`。当你想让 “after” 图呈现为一个粗边框 deep module、内部件灰显的效果时用这种——Mermaid 渲染不出那种分量感。

### 剖面图（适合分层的 shallowness）

堆叠横向条带（`h-12 border-l-4`）展示一次调用穿过的层。Before：6 个薄层，每层什么都不做。After：1 个厚条带，标注合并后的职责。

### 体量图（适合“interface 和实现一样宽”）

每个 module 画两个矩形——一个表示 interface 表面积，一个表示实现。Before：interface 矩形几乎和实现矩形一样高（shallow）。After：interface 矩形很矮，实现矩形很高（deep）。

### 调用图塌缩

Before：函数调用树渲染为嵌套盒子。After：同一棵树塌缩成一个盒子，现在已成内部调用的部分以淡化样式显示在里面。

## 样式指引

- 偏编辑排版感，而不是企业仪表盘感。留白要慷慨。标题可用衬线字体（`font-serif` 配 stone/slate 效果不错）。
- 克制用色：一个强调色（emerald 或 indigo），红色留给泄漏，琥珀色留给警告。
- 图的高度控制在 ~320px，让 before/after 不用滚动就能舒适地并排展示。
- 图内的 module 标签用 `text-xs uppercase tracking-wider`——读起来要像示意图，而不是 UI。
- 脚本只有 Tailwind CDN 和 Mermaid ESM import 两个。报告其余部分完全静态——没有应用代码，除了 Mermaid 自身的渲染外没有交互。

## Top recommendation 区块

一张更大的卡片。候选名、一句为什么、指向其卡片的锚链接。就这些。

## 语气

中文行文要平实、简洁——但架构名词与动词直接取自 `tuanzii:codebase-design` skill。简洁不是漂移的借口。

**严格使用：** module、interface、implementation、depth、deep、shallow、seam、adapter、leverage、locality。

**绝不可替代：** component、service、unit（指 module 时）· API、signature（指 interface 时）· boundary（指 seam 时）· layer、wrapper（指的是 module 时）。

**符合风格的表述：**

- “Order 接入 module 是 shallow 的——interface 几乎和实现一样大。”
- “定价逻辑在跨越 seam 泄漏。”
- “深化：一个 interface，一个测试入口。”
- “两个 adapter 证明这个 seam 成立：生产用 HTTP，测试用内存实现。”

**Wins 要点**用词汇表术语点名收益：*“locality：bug 集中在一个 module”*、*“leverage：一个 interface，N 个调用点”*、*“interface 收缩；实现吸收掉这些 wrapper”*。不要写*“更易维护”*或*“代码更干净”*——这些词不在词汇表里，不配占这个位置。

不闪烁其词，不绕弯子，不写“值得注意的是……”。一句话能改成要点就改成要点；一个要点能删就删。一个术语不在 `tuanzii:codebase-design` 词汇表里，就先从词汇表里找一个，别自造新词。
