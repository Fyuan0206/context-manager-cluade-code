---
name: context-manager
description: 智能上下文管理技能，帮助其他智能体像 Claude Code 一样管理对话上下文。使用这个技能来：1) 维护分层记忆系统（user/feedback/project/reference 四种记忆类型）；2) 自动发现和加载项目上下文文件（CLAUDE.md 系列）；3) 在对话历史过长时智能压缩；4) 优化 prompt 缓存策略；5) 从对话中自动提取关键信息并保存到记忆。当用户提到"记忆"、"上下文"、"记住"、"历史对话压缩"、"CLAUDE.md"或需要跨会话保持状态时，务必使用此技能。
compatibility:
  tools:
    - Read
    - Write
    - Bash
    - Glob
    - Grep
---

# 上下文管理器 (Context Manager)

## 概述

这个技能将其他智能体转变为具有 Claude Code 级别上下文管理能力的助手。它提供了一套完整的系统，用于跨会话维护项目状态、用户偏好、反馈记录和外部参考资料。

## 核心能力

### 1. 分层记忆架构

智能体使用**文件系统作为数据库**来存储持久化记忆。记忆分为四种类型，每种类型有明确的用途和保存时机：

#### User 记忆（关于用户）
- **用途**：记录用户的角色、偏好、工作习惯
- **何时保存**：学习到用户角色、职责、知识背景时
- **示例**：
  - "用户是前端工程师，偏好 TypeScript"
  - "用户喜欢先写测试再写代码"
  - "用户使用 VS Code，快捷键偏好 vim 模式"

#### Feedback 记忆（反馈记录）
- **用途**：记录用户对工作方式的指导和纠正
- **何时保存**：用户明确纠正("不要那样做")或确认("这样很好")时
- **结构**：规则本身 + **Why:**（原因）+ **How to apply:**（应用场景）
- **示例**：
  - "不要 mock 数据库——上次生产环境出过问题"
  - "回复要简洁，不需要总结"

#### Project 记忆（项目进度）
- **用途**：记录项目状态、待办事项、阻塞、截止日期
- **何时保存**：了解到"谁在做什么、为什么、何时完成"时
- **关键**：相对日期转绝对日期（"周四" → "2026-04-10"）
- **示例**：
  - "登录功能 UI 完成，API 接口进行中"
  - "周四前冻结合并，移动端发布分支"

#### Reference 记忆（参考资料）
- **用途**：记录外部系统位置（文档、链接、API）
- **何时保存**：用户提到外部资源时
- **示例**：
  - "bug 跟踪：Linear 项目 INGEST"
  - "Grafana 仪表板：grafana.internal/d/api-latency"

### 2. 记忆存储结构

```
记忆目录结构：
~/.claude/
├── CLAUDE.md                    # 用户全局记忆（合并视图）
├── rules/                       # 用户规则片段（细粒度）
│   ├── 01-testing.md
│   └── 02-code-style.md
├── memory/                      # 自动提取的记忆（memdir 格式）
│   ├── MEMORY.md               # 入口点（索引文件）
│   ├── user.md                 # User 记忆
│   ├── feedback.md             # Feedback 记忆
│   ├── project.md              # Project 记忆
│   └── reference.md            # Reference 记忆
└── projects/
    └── <project-slug>/
        └── memory/             # 项目级自动记忆
            ├── MEMORY.md
            └── ...

项目目录：
<repo>/
├── CLAUDE.md                   # 项目级记忆（已提交）
├── .claude/
│   ├── CLAUDE.md              # 项目级记忆（已提交）
│   ├── rules/                 # 项目规则
│   │   ├── api.md
│   │   └── testing.md
│   └── memory/               # 本地自动记忆（gitignored）
│       ├── MEMORY.md
│       └── ...
└── CLAUDE.local.md           # 本地覆盖（gitignored）
```

### 3. CLAUDE.md 文件发现与合并

智能体自动发现并合并多层 CLAUDE.md 文件，优先级从低到高：

1. `/etc/claude-code/CLAUDE.md` - 系统管理员（全局）
2. `~/.claude/CLAUDE.md` - 用户私有
3. `~/.claude/rules/*.md` - 用户规则
4. `<repo>/CLAUDE.md` - 项目级（已提交）
5. `<repo>/.claude/CLAUDE.md` - 项目级（已提交）
6. `<repo>/.claude/rules/*.md` - 项目规则
7. `<repo>/CLAUDE.local.md` - 本地覆盖（gitignored）
8. `~/.claude/memory/memory.md` - 自动记忆（最高）
9. `TEAMMEM` - 团队共享记忆（如启用）

**发现算法**：从当前工作目录向上遍历目录树，直到文件系统根。每个层级的文件内容按优先级合并，高优先级覆盖低优先级。

**@include 指令支持**：
```markdown
@./docs/guide.md        # 相对路径
@~/templates.md         # 用户主目录
@/etc/global.md         # 绝对路径
@../shared/config.md    # 父目录
```

**Frontmatter 路径限制**：
```yaml
---
paths:
  - src/**/*.ts
  - "!node_modules/**"
globs:
  - "*.config.js"
---
```

### 4. 上下文构建流水线

每次用户输入时，智能体按以下流程构建上下文：

```
用户输入
   ↓
[1] 上下文获取（并行）
   ├─ get_system_context()   → Git 状态、最近提交、分支
   ├─ get_user_context()     → 合并所有 CLAUDE.md 文件
   └─ get_system_prompt()    → 构建系统提示词
   ↓
[2] 消息规范化
   ├─ 附件重新排序（attachment bubble-up）
   ├─ 工具结果配对验证
   └─ 图像剥离（压缩时）
   ↓
[3] 压缩检查（token 计数）
   ├─ 超过阈值 → 触发 compact
   └─ 否则继续
   ↓
[4] API 调用（带 prompt caching）
   ↓
响应处理 & 历史记录
```

#### 系统提示词分段构建

系统提示词分为**静态部分**（全局缓存）和**动态部分**（会话级缓存）：

```
[静态 - 可全局缓存]
├─ 身份介绍
├─ 基础指令
├─ 工具使用指南
├─ 输出风格
└─ 效率指南

[DYNAMIC BOUNDARY - 不缓存的分隔符]

[动态 - 会话级缓存]
├─ 会话指导（启用的工具）
├─ Memory（CLAUDE.md 内容）
├─ 环境信息（OS、Shell、CWD）
├─ 语言偏好
├─ MCP 服务器指令
├─ Scratchpad 说明
└─ 工具结果清理
```

**缓存键设计**：
```typescript
cache_key = hash(
  system_prompt_prefix +   // 静态部分（全局缓存）
  user_context +           // 用户上下文（CLAUDE.md）
  system_context           // 系统上下文（Git 状态）
)
```

### 5. 智能压缩机制

当对话历史接近 token 限制时，自动或手动触发压缩：

**触发条件**：
- 配置的 token 阈值（默认约 200K）
- 检测到即将超过模型限制

**压缩流程**：
1. 执行 PreCompact hooks（可修改 customInstructions）
2. 剥离图像（替换为 `[image]` 占位符）
3. 构建压缩请求（简化版系统提示词 + FileReadTool）
4. 调用 Claude 生成摘要（优先使用 forked agent 共享 prompt cache）
5. 执行 PostCompact hooks

**压缩结果**：用一条 `system` 消息替换历史消息，内容为"这是之前对话的摘要..."

### 6. 自动记忆提取

在每次完整查询循环结束时，后台代理自动分析对话并提取持久化记忆：

**提取内容**：
- 用户提到的偏好和约束
- 项目进度更新
- 外部资源引用
- 重要的反馈和决策

**写入位置**：`~/.claude/projects/<project-slug>/memory/` 目录

**触发时机**：助手产生最终响应且无工具调用时

## 使用指南

### 初始化记忆系统

首次使用时，创建记忆目录结构：

```bash
# 用户级记忆
mkdir -p ~/.claude/memory
mkdir -p ~/.claude/rules

# 项目级记忆（在项目目录中）
mkdir -p .claude/memory
mkdir -p .claude/rules
```

### 手动保存记忆

使用 `/remember` 命令或直接调用记忆写入工具：

```markdown
用户：记住我喜欢用 Prettier 格式化代码

助手：[saves feedback memory: 用户偏好使用 Prettier 自动格式化代码]
```

**记忆文件格式**（frontmatter）：
```markdown
---
name: 用户偏好 Prettier
description: 代码格式化偏好
type: feedback
---

用户明确表示偏好使用 Prettier 进行代码自动格式化。
在提交代码前应该运行 `prettier --write` 检查。

**Why:** 用户之前手动格式花费太多时间

**How to apply:** 每次保存文件后自动运行 Prettier，PR 提交前再次确认
```

### 读取相关记忆

在对话开始时，智能体自动：
1. 扫描记忆目录中的所有 `.md` 文件
2. 读取 `MEMORY.md` 索引
3. 根据当前对话内容选择相关记忆（使用向量检索或关键词匹配）
4. 将记忆注入系统提示词

### 触发压缩

当对话变长时：
- **自动**：接近 token 限制时自动压缩
- **手动**：用户执行 `/compact` 命令
- **部分压缩**：选择特定消息进行压缩

### 清除记忆

使用 `/forget` 命令删除特定记忆，或直接编辑记忆文件。

## 最佳实践

### 何时保存记忆

- **User**：当你学到用户的角色、背景、技能水平、工作习惯时
- **Feedback**：每当用户纠正或确认你的工作方式时（包括否定和肯定）
- **Project**：当了解到项目进度、待办事项、截止日期、阻塞因素时
- **Reference**：当用户提到外部资源（链接、文档、仪表板）时

### 何时 NOT 保存

- 代码模式（可从代码库推导）
- 架构决策（可从代码/commit 历史推导）
- 文件结构（可从文件系统推导）
- 临时状态（会话记忆即可）

### 记忆文件大小限制

- **单文件**：最多 40,000 字符
- **MEMORY.md 索引**：最多 200 行或 25,000 字节
- 超出时自动截断并显示警告

### 缓存优化

为了最大化 prompt caching 收益：

1. **稳定内容放静态部分**：系统身份、基础指令
2. **变化内容放动态部分**：会话特定的工具列表、环境信息
3. **使用 `cache_control`**：
   - `ephemeral` - 永不缓存
   - `persistent: { ttl: "session" }` - 会话级缓存

## 实现参考

这个技能基于 Claude Code 的开源代码实现，核心模块包括：

- `src/context.ts` - 上下文获取接口
- `src/memdir/memdir.ts` - 记忆文件系统（21,000+ 行）
- `src/memdir/memoryTypes.ts` - 四型记忆定义
- `src/services/extractMemories/` - 自动提取代理
- `src/services/compact/compact.ts` - 压缩引擎（1,700+ 行）
- `src/constants/prompts.ts` - 系统提示词构建

完整源码参考：Claude Code v2.1.92.9d1

## 示例对话

**场景 1：学习用户偏好**
```
用户：我是后端工程师，主要用 Go 和 Python
助手：[保存 user 记忆：用户是后端工程师，主要使用 Go 和 Python]
```

**场景 2：记录项目状态**
```
用户：我们周四前要冻结合并，移动端要发布分支
助手：[保存 project 记忆：2026-04-10 前冻结合并，移动端发布分支]
```

**场景 3：保存外部资源**
```
用户：bug 跟踪用 Linear 的 INGEST 项目
助手：[保存 reference 记忆：bug 跟踪在 Linear 项目 INGEST]
```

**场景 4：记录反馈**
```
用户：不要用 console.log，用 debug 库
助手：[保存 feedback 记忆：使用 debug 库而非 console.log]
```

## 故障排除

### 记忆未加载
- 检查 `MEMORY.md` 是否存在且格式正确
- 确认记忆目录路径正确
- 查看 frontmatter 的 `type` 字段是否有效

### 压缩未触发
- 检查 token 计数是否超过阈值
- 手动执行 `/compact` 测试
- 查看压缩日志（`--debug` 模式）

### 缓存未命中
- 确认系统提示词的分段标记正确
- 检查动态边界标记位置
- 验证缓存键的一致性

---

**版本**：基于 Claude Code v2.1.92.321 蒸馏
**维护者**：Claude Code 团队
**许可**：MIT
