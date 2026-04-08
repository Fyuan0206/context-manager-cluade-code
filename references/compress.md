---
name: 记忆压缩脚本
description: 智能压缩对话历史的辅助脚本，当对话历史过长时生成摘要
---

# 记忆压缩脚本

## 功能概述

这个脚本帮助智能体在对话历史过长时生成高质量的压缩摘要。

## 使用方法

```python
from scripts.compress_memory import compress_conversation

# 压缩对话历史
summary = compress_conversation(
    messages=conversation_history,
    max_tokens=200000,
    model="claude-3-sonnet-20240229"
)
```

## 压缩策略

### 1. 预压缩准备
- 剥离图像和文档块（替换为占位符）
- 移除系统消息（保留最后一条）
- 过滤虚拟消息

### 2. 摘要生成
使用分块策略处理长对话：
1. 将历史分成语义块（按工具调用边界）
2. 逐块生成摘要
3. 合并块摘要为最终摘要

### 3. 后处理
- 保留关键细节（文件路径、错误信息）
- 保持时间线连贯性
- 标记不确定的部分

## 配置选项

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `max_tokens` | 触发压缩的 token 阈值 | 200000 |
| `model` | 用于压缩的模型 | 主对话模型 |
| `preserve_images` | 是否保留图像引用 | false |
| `keep_last_n` | 保留最近 N 条消息不压缩 | 10 |

## 输出格式

压缩后的消息结构：
```json
{
  "type": "system",
  "content": "这是之前对话的摘要：[摘要内容]\n\n关键文件：src/main.ts\n重要决策：选择了 PostgreSQL 作为数据库",
  "metadata": {
    "compressed_at": "2026-04-08T10:30:00Z",
    "original_message_count": 156,
    "compression_ratio": 0.85
  }
}
```

## 最佳实践

1. **压缩时机**：在 80% 的 token 限制时预压缩，留出缓冲
2. **保持上下文**：最近的消息和关键工具调用永远不压缩
3. **增量压缩**：多次压缩比单次深度压缩更可靠
4. **用户控制**：提供 `/compact` 手动触发和 `/expand` 恢复
