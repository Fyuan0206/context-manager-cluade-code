---
name: 缓存优化参考
description: Prompt caching 最佳实践和策略指南
---

# Prompt Caching 优化指南

## 缓存层级

Claude API 支持三级缓存策略：

### 1. Ephemeral（不缓存）
```typescript
{
  cache_control: { type: "ephemeral" }
}
```
- 永不缓存
- 用于敏感数据或每次必变的内容

### 2. Session（会话级缓存）
```typescript
{
  cache_control: { type: "persistent", ttl: "session" }
}
```
- 会话期间缓存
- 默认的动态部分缓存 scope

### 3. Global（全局缓存）
```typescript
{
  cache_control: { type: "persistent", ttl: "session" },
  cache_scope: "global"  // 或由位置决定
}
```
- 跨会话复用
- 用于稳定不变的内容

## 缓存键设计

完整的缓存键 = `hash(static_prefix + user_context + system_context)`

### 静态部分（可全局缓存）
- 模型身份定义
- 基础工具列表
- 核心系统指令
- 输出格式指南

### 动态部分（会话级缓存）
- 技能列表
- MCP 服务器指令
- 环境变量
- 当前项目路径
- 语言偏好

### 系统上下文（会话级缓存）
- Git 状态（分支、未提交文件）
- 最近提交（5条）
- 当前工作目录

## 优化策略

### 策略 1：边界标记法

在系统提示词中插入明确的分界符：

```
[STATIC CONTENT - 可全局缓存]
你是 Claude Code，一个 AI 编程助手...
基础工具：Bash, Grep, Glob, Read, Write...

[DYNAMIC BOUNDARY]
[此标记之后的内容不会进入全局缓存]

[DYNAMIC CONTENT - 会话级缓存]
当前项目：/path/to/project
启用的技能：context-manager, git-helper
MCP 服务器：3个已连接
```

实现：
```typescript
export const SYSTEM_PROMPT_DYNAMIC_BOUNDARY = '__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__'

function buildSystemPrompt() {
  const static = getStaticPrefix()
  const dynamic = getDynamicSections()
  return static + BOUNDARY + dynamic
}
```

### 策略 2：分段缓存控制

对系统提示词的每个区块独立设置 `cache_control`：

```typescript
const blocks = [
  { text: staticPrefix, cache_control: undefined },  // 全局缓存
  { text: userInstructions, cache_control: { type: "ephemeral" } },  // 不缓存
  { text: memoryContent, cache_control: { type: "persistent", ttl: "session" } },  // 会话缓存
  { text: envInfo, cache_control: { type: "persistent", ttl: "session" } },
]
```

### 策略 3：缓存键稳定化

确保相同请求产生相同缓存键：

- **稳定排序**：对象键按字母序
- **规范化路径**：绝对路径、真实路径（resolve symlinks）
- **确定性输出**：相同输入永远相同输出
- **避免随机数**：如必须用，固定 seed

### 策略 4：缓存命中监控

监控缓存效果：

```typescript
// API 响应中的缓存信息
{
  "usage": {
    "cache_creation_input_tokens": 15000,
    "cache_read_input_tokens": 5000,
    "input_tokens": 2000
  }
}

// 命中率计算
hit_rate = cache_read_tokens / (cache_creation_tokens + cache_read_tokens)
```

## 常见陷阱

| 陷阱 | 后果 | 解决方案 |
|------|------|----------|
| 时间戳嵌入系统提示词 | 每次请求缓存失效 | 移除或移至动态部分 |
| 随机 UUID | 缓存键不同 | 使用确定性 ID |
| 无序对象 | 序列化不一致 | 稳定排序 |
| 绝对路径暴露用户信息 | 隐私问题 | 规范化路径或替换为项目相对路径 |
| 过大的静态部分 | 每次请求传输大量数据 | 拆分为动态可选项 |

## 性能影响

典型场景下的缓存收益：

| 场景 | 无缓存 token | 有缓存 token | 节省 |
|------|-------------|-------------|------|
| 首次请求 | 50,000 | 50,000 | 0% |
| 后续请求 | 50,000 | 5,000 | 90% |
| 100 次对话 | 5,000,000 | 550,000 | 89% |

**成本影响**：缓存读写价格不同，需权衡创建成本 vs 读取收益。

## 诊断工具

### 检查缓存状态
```bash
# Claude Code 调试模式
claude --debug 2>&1 | grep -i cache

# 查看缓存命中日志
tail -f ~/.claude/logs/debug.log | grep cache_read
```

### 验证缓存键一致性
```typescript
// 在代码中打印缓存键的 hash
console.log("Cache key hash:", hash(static + dynamic))
```

## 参考资料

- [Claude API Prompt Caching 文档](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
- `src/constants/prompts.ts` - Claude Code 系统提示词构建
- `src/services/api/claude.ts` - 缓存控制实现
