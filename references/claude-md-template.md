---
name: CLAUDE.md 模板
description: 项目级 CLAUDE.md 文件的标准模板，包含 frontmatter 配置
---

# CLAUDE.md 模板

## 基础模板

```markdown
---
# Frontmatter: 路径限制（可选）
# 此 CLAUDE.md 仅对匹配的路径生效
paths:
  - src/**/*.ts
  - tests/**/*.ts
  - "!node_modules/**"
  - "!dist/**"
---

# 项目：{项目名称}

## 概述
{项目简介}

## 技术栈
- 后端：{技术栈}
- 前端：{技术栈}
- 数据库：{技术栈}

## 代码风格

### 命名约定
- 变量/函数：camelCase
- 组件/类：PascalCase
- 常量：UPPER_SNAKE_CASE
- 文件：kebab-case.ts

### 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 测试
chore: 构建/工具变更
```

## 开发流程

1. 从 main 分支创建 feature 分支
2. 编写测试（测试覆盖率 > 80%）
3. 运行 lint 和类型检查
4. 提交（遵循提交规范）
5. 创建 PR，等待审查

## 重要文件

- `src/main.ts` - 入口文件
- `src/config/` - 配置目录
- `tests/` - 测试文件

## 外部资源

- API 文档：{URL}
- Figma 设计：{URL}
- Confluence：{URL}

## 当前项目状态

{项目进度、待办事项、阻塞项}
```

## 用户级 CLAUDE.md (~/.claude/CLAUDE.md)

```markdown
# 用户配置：{用户名}

## 我的角色
{职位、团队、职责}

## 我的偏好

### 编码风格
- 语言：{偏好语言}
- 格式化：{Prettier/ESLint 配置}
- 测试框架：{偏好测试框架}

### 沟通风格
- 回复长度：{简洁/详细}
- 代码示例：{需要/不需要}
- 解释深度：{入门/高级}

### 工作习惯
- 先写测试再写代码
- 喜欢 TDD 流程
- 代码审查重点关注：{安全/性能/可读性}

## 我的项目
当前主要项目：{项目路径}

## 快捷方式
常用命令：
- 测试：{命令}
- 构建：{命令}
- 部署：{命令}
```

## 规则文件示例 (~/.claude/rules/)

### 01-testing.md
```markdown
---
paths:
  - tests/**/*.ts
  - src/**/*.test.ts
---

## 测试规范

所有新代码必须包含测试：
- 单元测试：覆盖核心逻辑
- 集成测试：关键路径
- E2E 测试：用户流程

运行测试：
```bash
npm test -- --coverage
```

覆盖率要求：> 80%
```

### 02-security.md
```markdown
---
paths:
  - src/**/*.ts
  - api/**/*.ts
---

## 安全要求

- 永远不要硬编码密钥
- 用户输入必须验证
- SQL 查询使用参数化
- JWT 令牌设置合理过期时间
```

## @include 示例

```markdown
# 主配置文件
@./docs/coding-standards.md   # 相对路径
@~/templates/api-guidelines.md # 用户主目录
@/etc/team-standards.md        # 绝对路径

# 内联内容
## 本地覆盖
对于这个特定目录，我们使用不同的配置...
```

## Frontmatter 完整示例

```yaml
---
# 元数据
name: 后端 API 服务规则
description: 适用于后端 API 开发的规范和指南

# 路径限制 - 仅对这些路径生效
paths:
  - src/api/**/*.ts
  - src/server/**/*.ts

# 排除模式
globs:
  - "*.test.ts"      # 测试文件不适用
  - "*.d.ts"         # 类型定义文件不适用

# 自定义标签（可选）
tags:
  - api
  - backend
  - security
---
```

## 最佳实践

1. **保持简洁**：每条规则聚焦单一主题
2. **解释 Why**：说明规则的原因，不只是 "怎么做"
3. **提供示例**：展示正确和错误的做法
4. **避免冲突**：规则之间不要相互矛盾
5. **定期审查**：过时的规则要及时更新或删除

## 文件大小限制

- 单文件：≤ 40,000 字符
- MEMORY.md 索引：≤ 200 行或 25,000 字节
- 超出部分自动截断，建议拆分

## 团队共享

使用 `TEAMMEM` 特性实现团队记忆共享：

```
~/.claude/team-memory/
├── MEMORY.md          # 团队索引
├── shared-rules.md    # 团队共享规则
└── project-context.md # 项目上下文
```

每个成员在自己的 `~/.claude/CLAUDE.md` 中包含：
```markdown
@~/team-memory/MEMORY.md
```
