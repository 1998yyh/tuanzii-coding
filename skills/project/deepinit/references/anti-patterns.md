# CLAUDE.md 反模式 — 不要写这些

## 通用废话（内置 /init 的典型问题）

以下内容绝对不要出现在 CLAUDE.md 中：

```markdown
# ❌ 这些都是废话，删掉

- "使用有意义的变量名"
- "提供有帮助的错误信息"
- "为所有新功能编写单元测试"
- "不要在代码或提交中包含敏感信息"
- "遵循 DRY 原则"（除非有项目特定的 DRY 执行机制，如 >5行重复必须提取）
- "保持代码整洁"
- "使用版本控制"
- "编写清晰的注释"
- "Common Development Tasks" / "Tips for Development" / "Support and Documentation" 这种万金油章节
```

## 文件结构罗列

```markdown
# ❌ 不要这样（ls 一下就能看到的信息）

src/
├── components/
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Modal.tsx
│   └── ...（30个文件）
├── hooks/
│   ├── useAuth.ts
│   └── useForm.ts
...
```

```markdown
# ✅ 应该这样（只写需要理解架构才能知道的划分逻辑）

## 项目结构

按领域驱动设计分层：
- `app/api/controllers/` — 端点层，处理 HTTP 路由和参数校验
- `app/services/` — 业务服务层，核心逻辑
- `app/db/` — 数据访问层，Repository 模式
- `app/clients/` — 外部服务客户端封装

关键约束：controller 不得直接访问 db 层，必须经过 service。
```

## 重复 README

如果 README.md 已经有了项目描述、安装步骤、使用说明，CLAUDE.md 不要复制一遍。CLAUDE.md 只写 README 里没有的 AI 协作特定信息。

## 猜测性内容

```markdown
# ❌ 没有从代码中验证的猜测

- "建议使用 Redis 做缓存"（代码里根本没有 Redis）
- "推荐覆盖率 80%"（没有从 CI 配置中确认）
- "可能使用了微服务架构"
```

## 过长的命令列表

```markdown
# ❌ 把所有 npm scripts 都列出来

npm run build
npm run dev
npm run test
npm run test:unit
npm run test:e2e
npm run test:coverage
npm run lint
npm run lint:fix
npm run format
npm run typecheck
npm run storybook
npm run build:storybook
...
```

```markdown
# ✅ 只列开发中最常用的几个，加上何时用的说明

## 可执行命令

# 日常开发
npm run dev          # 启动开发服务器（HMR）
npm run test -- path/to/test.ts  # 运行单个测试文件

# 提交前
npm run lint && npm run typecheck  # CI 会检查这两项

# 部署
npm run build        # 生产构建，输出到 dist/
```

## 没有上下文的规则

```markdown
# ❌ 规则没有解释为什么

- 不要使用 os.path.exists()
- 所有时间用 shanghai_now()
- 测试必须在容器内运行
```

```markdown
# ✅ 有背景说明

- 不要使用 os.path.exists()
  → 原因：NFS 属性缓存，多机下返回旧数据
  → 替代：try/except FileNotFoundError

- 所有时间用 shanghai_now()
  → 原因：容器 TZ=Asia/Shanghai + DB session 设 timezone
  → datetime.utcnow() 会导致时间错8小时
```
