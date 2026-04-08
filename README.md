# Context Manager Skill

> 让任何智能体都能像 Claude Code 一样管理上下文

基于 Claude Code 源码蒸馏的 Agent Skills，结构与安装方式参考 [yourself-skill](https://github.com/notdog1998/yourself-skill)（AgentSkills 开放标准）。

## 安装

### Claude Code

> **重要**：Claude Code 从 **git 仓库根目录** 的 `.claude/skills/` 查找 skill。请在正确的位置执行。

```bash
# 安装到当前项目（在 git 仓库根目录执行）
mkdir -p .claude/skills
git clone https://github.com/Fyuan0206/context-manager-cluade-code.git .claude/skills/context-manager

# 或安装到全局（所有项目都能用）
# Linux / macOS:
git clone https://github.com/Fyuan0206/context-manager-cluade-code.git ~/.claude/skills/context-manager
# Windows (PowerShell)，示例：
# git clone https://github.com/Fyuan0206/context-manager-cluade-code.git "$env:USERPROFILE\.claude\skills\context-manager"
```

克隆完成后，智能体即可加载 `context-manager` 技能（见下方「快速开始」）。

## 概述

这是一个蒸馏自 Claude Code (v2.1.92.321) 的上下文管理系统技能。当其他智能体加载此技能后，即可获得与 Claude Code 同级别的上下文管理能力，包括：

- **分层记忆系统**：四种记忆类型（user/feedback/project/reference）
- **CLAUDE.md 文件发现**：自动发现和合并项目指令文件
- **智能上下文压缩**：对话历史过长时自动生成摘要
- **Prompt 缓存优化**：最大化 Anthropic API 的缓存收益
- **自动记忆提取**：从对话中自动提取关键信息

## 快速开始

### 1. 安装技能

若已通过 [安装](#安装) 中的 `git clone` 完成，可跳过本步。否则也可手动复制本仓库到 `~/.claude/skills/context-manager`（目录名需与技能 `name` 一致以便识别）。

### 2. 初始化项目

在你的项目中运行初始化脚本：

```bash
# 使用技能附带的脚本
python ~/.claude/skills/context-manager/scripts/init.py

# 或使用技能命令
# 当智能体加载此技能后，你可以说：
# "帮我在这个项目中初始化上下文管理"
```

这将创建：
```
.claude/
├── CLAUDE.md           # 项目级规则
├── rules/              # 规则片段
│   ├── 01-coding.md
│   ├── 02-testing.md
│   └── 03-security.md
└── memory/             # 自动记忆目录（gitignored）
```

### 3. 配置个人偏好

编辑 `~/.claude/CLAUDE.md` 添加你的个人偏好：

```markdown
---
# 用户配置
---

# 我的角色
后端工程师，主要使用 Go 和 Python

## 我的偏好
- 先写测试再写代码
- 使用 Prettier 自动格式化
- 代码审查重点关注安全性

## 当前项目
~/projects/my-app/
```

## 使用示例

### 保存用户偏好

```
用户：记住我喜欢用函数组件，不用类组件
助手：[saves user memory: 用户偏好 React 函数组件而非类组件]
```

记忆会被保存到 `~/.claude/memory/user_*.md`。

### 记录项目进度

```
用户：本周要完成登录功能。后端 API 已完成，前端还有两个组件。周五演示。
助手：[saves project memory: 登录功能开发 - 后端完成，前端剩余 2 组件，2026-04-11 截止演示]
```

### 引用外部资源

```
用户：bug 跟踪用 Linear 的 INGEST 项目
助手：[saves reference memory: bug 跟踪在 Linear 项目 INGEST]
```

### 自动记忆提取

当对话中出现值得保存的信息时，智能体会自动提示是否保存：

```
助手：我注意到你提到"不要 mock 数据库"，要我保存这条反馈吗？
用户：是的
助手：[saves feedback memory: 不使用数据库 mock，集成测试必须使用真实数据库]
```

### 触发压缩

当对话变长时，智能体会自动或根据命令压缩：

```
用户：/compact
助手：正在压缩对话历史...
[生成摘要并替换历史消息]
```

## 记忆类型详解

| 类型 | 用途 | 何时保存 | 示例 |
|------|------|----------|------|
| **user** | 用户背景、偏好 | 学到用户角色、技能、习惯时 | "用户是 Go 后端工程师" |
| **feedback** | 工作方式指导 | 用户纠正或确认时 | "不要用 console.log" |
| **project** | 项目状态 | 了解到进度、待办、阻塞时 | "登录功能周五前完成" |
| **reference** | 外部资源 | 提到文档、链接、仪表板时 | "API 文档在 example.com" |

### 文件命名

记忆文件自动命名为：`{type}_{slug}.md`

例如：
- `user_go-backend-engineer.md`
- `feedback_no-console-log.md`
- `project_login-feature.md`
- `reference_linear-ingest.md`

## 核心概念

### CLAUDE.md 文件链

Claude Code 按优先级发现并合并多层 CLAUDE.md 文件：

1. `/etc/claude-code/CLAUDE.md` - 系统管理员
2. `~/.claude/CLAUDE.md` - 用户私有
3. `~/.claude/rules/*.md` - 用户规则片段
4. `<repo>/CLAUDE.md` - 项目级（已提交）
5. `<repo>/.claude/CLAUDE.md` - 项目级（已提交）
6. `<repo>/.claude/rules/*.md` - 项目规则
7. `<repo>/CLAUDE.local.md` - 本地覆盖（gitignored）
8. `~/.claude/memory/memory.md` - 自动记忆（最高优先级）
9. `TEAMMEM` - 团队共享记忆（可选）

**高优先级覆盖低优先级**，允许局部定制。

### @include 指令

在 CLAUDE.md 中可使用 `@` 语法包含其他文件：

```markdown
@./docs/guide.md        # 相对路径（基于当前文件）
@~/templates/api.md     # 用户主目录
@/etc/global-rules.md   # 绝对路径
@../shared/config.md    # 父目录
```

支持递归包含和循环检测。

### 缓存优化

技能提供详细的 prompt caching 优化指南：

- **静态部分**（全局缓存）：模型身份、基础指令
- **动态部分**（会话缓存）：环境信息、技能列表
- **边界标记**：`__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__`

查看 `references/caching.md` 了解完整策略。

### 压缩机制

当对话超过 80% token 限制时，自动触发压缩：

1. 剥离图像和文档块
2. 保留最近 10 轮对话
3. 用摘要替换历史消息

手动触发：`/compact`

## 目录结构

```
context-manager/
├── SKILL.md              # 技能主文档（本文件）
├── evals/
│   └── evals.json       # 测试用例
├── scripts/
│   ├── init.py          # 项目初始化脚本
│   ├── check.py         # 系统检查脚本
│   └── create_memory.py # 创建记忆文件
└── references/
    ├── claude-md-template.md    # CLAUDE.md 模板
    ├── implementation-guide.md  # 实现指南
    ├── extraction-prompts.md    # 提取提示词
    ├── compress.md             # 压缩参考
    └── caching.md              # 缓存优化
```

## 验证安装

运行系统检查脚本：

```bash
python ~/.claude/skills/context-manager/scripts/check.py
```

检查项：
- ✓ 记忆目录是否存在
- ✓ MEMORY.md 索引格式
- ✓ CLAUDE.md 文件发现
- ✓ 记忆文件 frontmatter 有效性
- ✓ Git 忽略配置

## 故障排除

### 记忆未加载
**症状**：对话中不引用已保存的记忆

**检查**：
```bash
cat ~/.claude/memory/MEMORY.md
```
确保索引文件包含正确的链接。

**修复**：运行 `scripts/init.py` 重建结构

### 压缩未触发
**症状**：长对话不自动压缩

**检查**：token 计数是否超过阈值
```bash
#  Claude Code 调试模式
claude --debug | grep -i token
```

**手动触发**：`/compact`

### 缓存未命中
**症状**：API 调用每次都是全新请求

**检查**：系统提示词是否正确分段
- 静态部分在边界标记之前
- 动态部分在边界标记之后

参考 `references/caching.md` 的边界标记法。

### 文件大小超限
**症状**：记忆文件被截断

**解决**：拆分大文件
- 单文件 ≤ 40,000 字符
- MEMORY.md ≤ 200 行或 25,000 字节

## 性能建议

1. **增量加载**：仅扫描修改的记忆文件
2. **并行获取**：系统上下文、用户上下文并行加载
3. **相关记忆选择**：仅加载相关记忆，而非全部
4. **缓存键稳定**：确保相同请求产生相同缓存键

## 数据安全

- **敏感数据**：使用 `ephemeral` 缓存，不持久化
- **本地记忆**：`CLAUDE.local.md` 和 `memory/` 自动 gitignore
- **团队共享**：`TEAMMEM` 支持团队内共享，个人记忆保持私密
- **备份**：记忆文件是普通 Markdown，可直接 Git 提交（除本地文件）

## 高级配置

### 环境变量

```bash
# 禁用 CLAUDE.md 加载
export CLAUDE_CODE_DISABLE_CLAUDE_MDS=1

# 仅使用显式目录
export CLAUDE_CODE_BARE_MODE=1

# 调试模式
export CLAUDE_CODE_DEBUG=1
```

### 配置文件

```typescript
// ~/.claude/settings.json（或项目 .claude/settings.json）
{
  "contextManagement": {
    "autoExtractMemories": true,
    "autoCompact": true,
    "maxTokensBeforeCompact": 200000,
    "cacheOptimization": "aggressive"
  }
}
```

## API 参考

### 记忆操作 API

```python
# 创建记忆
save_memory({
    'type': 'user',
    'title': '偏好 TDD',
    'content': '用户喜欢测试驱动开发...',
    'confidence': 0.95
})

# 检索记忆
memories = find_relevant_memories(
    query="测试策略",
    top_k=5,
    memory_types=['feedback', 'project']
)

# 列出所有记忆
all_memories = list_memories(
    since_date="2026-01-01",
    types=['user', 'project']
)

# 删除记忆
delete_memory(memory_id="user_preference_123")
```

### 压缩 API

```python
# 手动压缩
summary = compress_conversation(
    messages=history,
    strategy='summary',  # 或 'truncate'
    keep_last=10
)

# 部分压缩（压缩特定消息）
compressed = partial_compact(
    messages=history,
    selector=lambda m: m['role'] == 'tool_result' and m['timestamp'] < threshold
)
```

### CLAUDE.md 操作

```python
# 解析 CLAUDE.md
parsed = parse_claude_file(
    path='.claude/CLAUDE.md',
    resolve_includes=True
)

# 合并多个文件
merged = merge_claude_files([
    '/etc/claude-code/CLAUDE.md',
    str(Path.home() / '.claude' / 'CLAUDE.md'),
    '.claude/CLAUDE.md'
])

# 发现项目 CLAUDE.md
files = discover_claude_files(
    start_path=Path.cwd(),
    max_depth=10
)
```

## 与其他技能的集成

此技能设计为**基础能力层**，其他技能可以依赖它：

```yaml
# 其他技能的 SKILL.md 中可以声明依赖
compatibility:
  requires:
    - context-manager  # 确保上下文管理可用
```

## 参考实现

本技能基于 Claude Code 开源代码（v2.1.92.321）蒸馏：

| 模块 | 行数 | 说明 |
|------|------|------|
| `src/memdir/memdir.ts` | 21K | 记忆文件系统核心 |
| `src/services/extractMemories/` | 22K | 自动提取代理 |
| `src/services/compact/compact.ts` | 17K | 压缩引擎 |
| `src/context.ts` | 6K | 上下文获取 |
| `src/utils/claudemd.ts` | 14K | CLAUDE.md 解析 |
| **总计** | **~80K** | 核心上下文管理代码 |

完整源码：https://github.com/anthropics/claude-code

## 许可证

MIT License - 基于 Claude Code 开源实现蒸馏

## 贡献

本技能是 Claude Code 上下文管理系统的**教学版本**。如需生产级实现，请参考官方 Anthropic 文档或直接使用 Claude Code CLI。

## 更新日志

### v1.0.0 (2026-04-08)
- 初始版本
- 实现四型记忆系统
- CLAUDE.md 发现与合并
- 压缩机制说明
- Prompt 缓存优化指南
- 自动提取提示词模板

---

**由 Claude Code v2.1.92.321 蒸馏 · 2026-04-08**
