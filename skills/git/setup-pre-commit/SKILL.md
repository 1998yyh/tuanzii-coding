---
name: setup-pre-commit
description: 在当前仓库配置 Husky pre-commit 钩子，集成 lint-staged（Prettier）、typecheck 和测试。当用户想添加 pre-commit 钩子、配置 Husky、配置 lint-staged、或在提交时做格式化/类型检查/测试时使用。触发词：pre-commit 钩子、提交前检查、Husky 配置。
---

# 配置 Pre-Commit 钩子

## 会配置什么

- **Husky** pre-commit 钩子
- **lint-staged**：对所有暂存文件运行 Prettier
- **Prettier** 配置（如缺失）
- pre-commit 钩子中的 **typecheck** 与 **test** 脚本

## 步骤

### 1. 识别包管理器

检查 `package-lock.json`（npm）、`pnpm-lock.yaml`（pnpm）、`yarn.lock`（yarn）、`bun.lockb`（bun），以存在的为准。无法判断时默认 npm。

### 2. 安装依赖

以 devDependencies 安装：

```
husky lint-staged prettier
```

### 3. 初始化 Husky

```bash
npx husky init
```

这会创建 `.husky/` 目录，并在 package.json 中加入 `prepare: "husky"`。

### 4. 创建 `.husky/pre-commit`

写入以下内容（Husky v9+ 无需 shebang）：

```
npx lint-staged
npm run typecheck
npm run test
```

**按需调整**：把 `npm` 替换为识别到的包管理器。如果 package.json 中没有 `typecheck` 或 `test` 脚本，省略对应行并告知用户。

### 5. 创建 `.lintstagedrc`

```json
{
  "*": "prettier --ignore-unknown --write"
}
```

### 6. 创建 `.prettierrc`（如缺失）

仅在不存在任何 Prettier 配置时创建。使用以下默认值：

```json
{
  "useTabs": false,
  "tabWidth": 2,
  "printWidth": 80,
  "singleQuote": false,
  "trailingComma": "es5",
  "semi": true,
  "arrowParens": "always"
}
```

### 7. 验证

- [ ] `.husky/pre-commit` 存在且可执行
- [ ] `.lintstagedrc` 存在
- [ ] package.json 中 `prepare` 脚本为 `"husky"`
- [ ] Prettier 配置存在
- [ ] 运行 `npx lint-staged` 确认可用

### 8. 提交

暂存所有新增/修改的文件，提交信息使用：`Add pre-commit hooks (husky + lint-staged + prettier)`

这次提交会触发刚配置的 pre-commit 钩子——正好作为一次冒烟测试，验证一切正常。

## 备注

- Husky v9+ 的钩子文件不需要 shebang
- `prettier --ignore-unknown` 会跳过 Prettier 无法解析的文件（如图片）
- pre-commit 先跑 lint-staged（快、只处理暂存文件），再跑完整的 typecheck 和测试
