# 环境特殊规范模式库

当扫描到项目有以下特征时，在 CLAUDE.md 中生成对应的环境规范章节。

## NFS / 网络文件系统

**触发条件**: docker-compose 中有 NAS/NFS 挂载、代码中引用 `/data/` `/mnt/` 路径、有 `refresh_nfs_cache` 类工具函数

**规范模板**:
```markdown
## NFS 文件操作规范

工作目录挂载在 NFSv4 上。NFSv4 保证 close-to-open 一致性：写端 close() 后读端 open() 能读到最新数据；但 os.stat() / os.path.exists() 走属性缓存，多机下可能返回旧数据。

**适用范围**: NFS 挂载目录必须遵循；容器本地目录不受影响。

| 操作 | ✅ 正确做法 | ❌ 禁止做法 |
|------|------------|-----------|
| 读内容 | `open() + read()` | — |
| 读属性 | `open() + os.fstat(f.fileno())` | `os.stat(path)` |
| 判存在 | `try: open() except FileNotFoundError` | `os.path.exists()` |
```

## 时区统一

**触发条件**: Dockerfile 中有 `TZ=` 设置、代码中有自定义时区工具函数、数据库 session 有 timezone 设置

**规范模板**:
```markdown
## 时区规范（[时区名] 统一）

所有时间统一 [时区]，工具函数在 [路径]：

| 场景 | 使用函数 | 返回类型 |
|------|---------|---------|
| DB 写入 | `xxx_now()` | naive datetime |
| API 响应 | `xxx_isoformat(dt)` | ISO 字符串带时区 |

**禁止**: `datetime.utcnow()`、`datetime.now().isoformat()`
```

## Docker 容器执行

**触发条件**: 测试通过 docker exec 或脚本在容器内执行、有 Dockerfile + docker-compose

**规范模板**:
```markdown
## 容器内执行规范

测试和验证在容器内真实环境执行：
- 运行命令: `[具体脚本]`
- 验证方式: [HTTP API / DB 查询 / 日志检查]
- 注意: [容器网络/挂载/环境变量特殊配置]
```

## Git Worktree

**触发条件**: 代码中有 worktree 管理逻辑、.claude/ 下有 worktree 相关配置

**规范模板**:
```markdown
## Git Worktree 规范

worktree 共享 .git 但工作目录独立。
- 创建后必须: [项目特定的初始化步骤]
- 同步代码: `git checkout <branch> -- <file>`，不要直接复制
- 注意: [.env/.gitignore 文件的处理方式]
```

## 多机部署一致性

**触发条件**: docker-compose 有多实例配置、代码中有分布式锁/一致性相关逻辑

**规范模板**:
```markdown
## 多机一致性规范

[描述多机场景下的特殊约束]
- 文件操作: [一致性保证方式]
- 状态同步: [通过 DB/Redis/消息队列]
- 避免: [本地缓存/内存状态 在多机下的陷阱]
```
