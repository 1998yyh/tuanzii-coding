# 三层边界模型编写指南

三层边界模型是 CLAUDE.md 的核心约束机制。它不是通用编程规范，而是从项目实际踩坑经验中提炼的硬性规则。

## 结构

```markdown
## 三层边界模型

### ✅ 必须执行
[违反即视为任务未完成的硬性规则]

### ⚠️ 需先询问
[改之前必须获得确认的操作，防止破坏性变更]

### ❌ 禁止操作
[绝对不能做的事情，通常来自历史事故]
```

## 编写原则

### "必须执行" 层

来源：
- 项目的 CI/CD 强制检查项
- 代码中观察到的一致性模式（所有文件都遵循的约定）
- 文档同步机制（改代码必须同步改文档的规则）
- 测试覆盖率硬性要求

示例模板：
```markdown
### ✅ 必须执行

- 改代码前先查 `docs/` 相关文档了解现有逻辑
- **DRY**: 写新功能前先搜索代码库，有可复用实现优先复用
- 改核心业务逻辑后更新 `docs/[对应目录]/` 的流程图
- 新增/改核心模块必须配测试，覆盖率 ≥[从 CI 配置中读取]%
- `[测试运行命令]` 验证通过后再提交
- 完整类型注解 + [从代码中观察到的 docstring 风格]
- **Fail Fast**: 核心业务逻辑严格校验、失败立即抛异常
```

### "需先询问" 层

来源：
- 可能影响其他人工作的操作
- 不可逆或高代价的变更
- 跨模块/跨团队的改动

示例模板：
```markdown
### ⚠️ 需先询问

- 改数据库模型或迁移脚本
- 改核心架构设计 / API 接口签名
- 删除或重构大量代码（>100行）
- 升级核心依赖版本
- 修改 CI/CD 配置
```

### "禁止操作" 层

来源：
- 历史事故/踩坑经验（从 git log、issue、病例库中提取）
- 安全红线
- 环境特殊限制

示例模板：
```markdown
### ❌ 禁止操作

- 跳过测试直接提交
- 改代码不更新文档/流程图
- 核心逻辑静默回退/回滚（吞异常）
- 复制粘贴 >5 行相同代码
- 直接改生产配置
- 硬编码敏感信息
- [环境特定的禁止操作，如 NFS 下禁止 os.path.exists()]
```

## 如何从代码中提取边界规则

### 搜索模式

```bash
# 找 lint/format 强制规则
grep -r "error" .eslintrc* pyproject.toml setup.cfg --include="*.toml" --include="*.json" --include="*.yaml"

# 找 CI 中的强制检查
grep -r "fail\|error\|exit 1" .github/workflows/ .gitlab-ci.yml Jenkinsfile

# 找代码中的 raise/assert 模式（Fail Fast 证据）
grep -rn "raise\|assert\|throw" app/ src/ --include="*.py" --include="*.ts" | head -20

# 找测试覆盖率配置
grep -r "coverage\|cov" pyproject.toml jest.config* .nycrc* pytest.ini

# 找文档同步线索
grep -rn "docs/\|README\|CHANGELOG" Makefile scripts/ .github/workflows/
```

### 判断标准

一条规则值得写入边界模型的条件：
1. **频率** — 代码库中 >80% 的文件都遵循此约定
2. **后果** — 违反会导致 CI 失败、运行时错误、或团队冲突
3. **非显而易见** — 不是 "写好的代码" 这种废话，而是项目特定的硬约束
4. **可验证** — 能通过 grep/lint/test 客观验证是否遵守
