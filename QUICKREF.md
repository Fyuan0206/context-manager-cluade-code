# Context Manager - 快速参考卡

## 一句话总结
让任何智能体都能像 Claude Code 一样管理跨会话的上下文和记忆。

## 核心功能

| 功能 | 命令/触发词 | 说明 |
|------|------------|------|
| 保存记忆 | "记住..." / 自动提取 | 四种类型：user/feedback/project/reference |
| 回忆记忆 | 自动 | 根据对话内容检索相关记忆 |
| 压缩历史 | `/compact` / 自动 | 对话过长时生成摘要 |
| 查看记忆 | `/memory` | 列出所有保存的记忆 |
| 删除记忆 | `/forget <关键词>` | 删除特定记忆 |

## 记忆类型速查

```markdown
type: user        → 用户背景、技能、偏好
type: feedback   → 工作方式指导（带 Why + How）
type: project    → 项目进度、待办、截止日期
type: reference  → 外部资源链接
```

## 文件位置

```bash
# 用户级
~/.claude/CLAUDE.md              # 用户配置
~/.claude/rules/*.md            # 用户规则
~/.claude/memory/               # 自动记忆目录
~/.claude/memory/MEMORY.md      # 记忆索引

# 项目级
<project>/.claude/CLAUDE.md     # 项目规则
<project>/.claude/rules/*.md    # 项目规则片段
<project>/.claude/memory/       # 项目自动记忆
<project>/CLAUDE.local.md       # 本地覆盖
```

## CLAUDE.md 优先级（高覆盖低）

```
1. CLAUDE.local.md           (本地，gitignored)
2. ~/.claude/memory/memory.md (自动记忆)
3. <repo>/.claude/rules/*.md
4. <repo>/.claude/CLAUDE.md
5. <repo>/CLAUDE.md
6. ~/.claude/rules/*.md
7. ~/.claude/CLAUDE.md
8. /etc/claude-code/CLAUDE.md
```

## 常用命令

```bash
# 初始化项目
python scripts/init.py

# 检查系统
python scripts/check.py

# 手动创建记忆
python scripts/create_memory.py \
  --type feedback \
  --title "Prettier 格式化" \
  --content "使用 Prettier 自动格式化代码"

# 列出记忆
ls ~/.claude/memory/

# 查看记忆索引
cat ~/.claude/memory/MEMORY.md
```

## 记忆文件格式

```markdown
---
name: 简短标题
description: 一句话描述
type: user|feedback|project|reference
---

## 正文

内容详细描述...

**Why:** （仅 feedback）原因

**How to apply:** （仅 feedback）应用场景

**创建日期:** YYYY-MM-DD
```

## 触发条件（何时使用此技能）

当用户提到以下关键词时，智能体应该使用此技能：

- "记住" / "记住这个"
- "记忆" / "保存到记忆"
- "上下文" / "保持上下文"
- "跨会话"
- "历史对话压缩"
- "CLAUDE.md"
- "项目规则"
- "我的偏好"
- "/compact" 命令
- 对话历史 > 100 轮

## 最佳实践

✅ **要做的事**
- 用户明确提到偏好时立即保存
- 项目状态变更时更新 project 记忆
- 使用绝对日期而非相对日期
- Feedback 类型包含 Why 和 How to apply
- 定期审查和清理旧记忆

❌ **不要做的事**
- 保存可从代码推导的信息
- 记忆文件超过 40K 字符
- 在 CLAUDE.md 中存储敏感数据
- 使用模糊的标题
- 忘记更新 MEMORY.md 索引

## 缓存优化三原则

1. **静态 vs 动态分离**
   - 静态（全局缓存）：身份、基础指令
   - 动态（会话缓存）：环境、工具列表

2. **边界标记法**
   ```
   静态内容
   __DYNAMIC_BOUNDARY__
   动态内容
   ```

3. **稳定序列化**
   - 对象按键排序
   - 路径规范化
   - 避免随机值

## 故障排除速查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 记忆不加载 | MEMORY.md 格式错误 | 运行 `check.py` 验证 |
| 压缩不触发 | token 未超阈值 | 手动 `/compact` |
| @include 失败 | 路径错误或循环引用 | 检查路径和 `visited` 集 |
| 缓存未命中 | 系统提示词无边界标记 | 参考 `caching.md` 重构 |
| 文件被截断 | 超过 40K 字符限制 | 拆分为多个文件 |

## 关键数字

| 限制 | 值 | 说明 |
|------|---|------|
| 单记忆文件大小 | 40,000 字符 | 超过会截断 |
| MEMORY.md 行数 | 200 行 | 索引文件限制 |
| MEMORY.md 字节数 | 25,000 字节 | 防止超大行 |
| 压缩阈值 | 200K tokens | 默认触发点 |
| 保留历史 | 100 条 | 本地历史文件 |
| 保留最近对话 | 10 轮 | 压缩时 |

## 有用链接

- 完整文档：`README.md`
- 实现指南：`references/implementation-guide.md`
- CLAUDE.md 模板：`references/claude-md-template.md`
- 缓存优化：`references/caching.md`
- 提取提示词：`references/extraction-prompts.md`
- 压缩参考：`references/compress.md`

## 示例对话

```
用户：我是前端工程师，主要用 React 和 TypeScript
助手：[保存 user 记忆]

用户：不要用 any 类型，用 unknown 替代
助手：[保存 feedback 记忆，包含 Why 和 How]

用户：登录功能周四前完成，等后端 API
助手：[保存 project 记忆，日期转换]

用户：API 文档在 api.example.com/docs
助手：[保存 reference 记忆]
```

## 提示词片段（供智能体使用）

```markdown
## 使用 context-manager 技能

1. 检测到用户提到"记住"、"偏好"、"进度"等关键词
2. 识别记忆类型（user/feedback/project/reference）
3. 使用 create_memory.py 脚本创建文件
4. 更新 MEMORY.md 索引
5. 向用户确认

## 检索相关记忆

1. 读取 ~/.claude/memory/MEMORY.md
2. 扫描所有记忆文件
3. 基于当前对话相关性排序
4. 选择 top-3 相关记忆
5. 注入系统提示词
```

---

**版本**: 1.0.0
**基于**: Claude Code v2.1.92.321
**最后更新**: 2026-04-08
