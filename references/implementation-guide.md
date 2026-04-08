---
name: 实现指南
description: 如何在其他智能体中实现类似 Claude Code 的上下文管理系统
---

# 实现指南：为智能体添加上下文管理能力

## 概述

本指南将帮助你在自己的智能体系统中实现类似 Claude Code 的上下文管理能力。核心是**分层记忆系统** + **CLAUDE.md 发现** + **智能压缩**。

## 架构概览

```
┌─────────────────────────────────────────────────────┐
│           智能体上下文管理器                         │
├─────────────────────────────────────────────────────┤
│  1. 记忆文件系统 (memdir)                           │
│     - 四型记忆：user/feedback/project/reference     │
│     - 文件存储 + MEMORY.md 索引                     │
│     - @include 支持                                 │
├─────────────────────────────────────────────────────┤
│  2. CLAUDE.md 发现引擎                              │
│     - 向上遍历目录树                                 │
│     - 多层合并（系统/用户/项目/本地）                │
│     - 路径过滤（frontmatter）                       │
├─────────────────────────────────────────────────────┤
│  3. 上下文构建流水线                                │
│     输入 → 并行获取 → 规范化 → 压缩 → API 调用      │
├─────────────────────────────────────────────────────┤
│  4. 压缩引擎                                        │
│     - Token 阈值检查                                 │
│     - 自动/手动触发                                  │
│     - 摘要生成                                       │
├─────────────────────────────────────────────────────┤
│  5. Prompt 缓存优化                                 │
│     - 静态/动态分段                                  │
│     - 缓存键设计                                     │
│     - 边界标记法                                     │
└─────────────────────────────────────────────────────┘
```

## 步骤 1：实现记忆文件系统

### 1.1 目录结构

```python
from pathlib import Path
from datetime import datetime

class MemorySystem:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path.cwd())
        self.memory_root = self.project_root / '.claude' / 'memory'
        self.memory_root.mkdir(parents=True, exist_ok=True)

    def get_memory_files(self):
        """扫描记忆目录，返回所有 .md 文件"""
        files = {}
        for md_file in self.memory_root.glob('*.md'):
            if md_file.name == 'MEMORY.md':
                continue  # 索引文件单独处理
            memory_type = md_file.stem.split('_')[0]  # user_xxx → user
            files[memory_type] = md_file
        return files
```

### 1.2 记忆文件格式

```markdown
---
name: 简短标题
description: 一句话描述
type: user|feedback|project|reference
---

## 正文内容

这里是记忆的详细内容。

**Why:** （仅 feedback 类型需要）原因解释

**How to apply:** （仅 feedback 类型需要）应用场景

**创建日期:** 2026-04-08
**来源:** 用户对话 @ 2026-04-08 10:30
```

### 1.3 MEMORY.md 索引

```markdown
# 记忆索引

## 关于我
- [用户角色](./user_role.md)
- [技术偏好](./user_tech-preferences.md)

## 反馈记录
- [Prettier 格式化](./feedback_prettier.md)

## 项目进度
- [登录功能开发](./project_login-feature.md)

## 参考资料
- [Linear 项目](./reference_linear.md)
```

## 步骤 2：实现 CLAUDE.md 发现

### 2.1 向上遍历目录树

```python
def find_claude_files(start_path: Path):
    """从起始路径向上遍历，查找所有 CLAUDE.md"""
    claude_files = []
    current = start_path.resolve()

    while True:
        # 检查当前目录
        for filename in ['CLAUDE.md', '.claude/CLAUDE.md', 'CLAUDE.local.md']:
            candidate = current / filename
            if candidate.exists():
                claude_files.append(candidate)

        # 到达根目录？
        if current.parent == current:
            break
        current = current.parent

    return claude_files
```

### 2.2 合并内容

```python
def merge_claude_files(files: list[Path]):
    """按优先级合并多个 CLAUDE.md 文件"""
    merged = []

    # 低优先级先加载，高优先级后加载（覆盖）
    priority_order = [
        '/etc/claude-code/CLAUDE.md',
        Path.home() / '.claude' / 'CLAUDE.md',
        # ... 项目文件
    ]

    for filepath in sorted(files, key=lambda f: priority_order.index(str(f))):
        content = parse_claude_file(filepath)
        merged.append({
            'source': str(filepath),
            'content': content,
            'priority': get_priority(filepath)
        })

    return merged
```

### 2.3 解析 @include

```python
def resolve_includes(content: str, base_dir: Path, visited=None):
    """递归解析 @include 指令"""
    if visited is None:
        visited = set()

    lines = content.split('\n')
    result = []

    for line in lines:
        if line.strip().startswith('@'):
            include_path = line.strip()[1:].strip()

            # 解析路径
            if include_path.startswith('~'):
                full_path = Path(include_path.replace('~', str(Path.home())))
            elif include_path.startswith('/'):
                full_path = Path(include_path)
            else:
                full_path = (base_dir / include_path).resolve()

            # 循环引用检测
            if str(full_path) in visited:
                result.append(f"[循环引用跳过: {include_path}]")
                continue
            visited.add(str(full_path))

            # 递归读取
            if full_path.exists():
                included = full_path.read_text()
                result.append(resolve_includes(included, full_path.parent, visited))
        else:
            result.append(line)

    return '\n'.join(result)
```

## 步骤 3：上下文构建

### 3.1 获取系统上下文

```python
import subprocess

async def get_system_context(project_root: Path):
    """收集系统级上下文"""
    context = {}

    # Git 状态
    git_status = await run_git(['status', '--short'], cwd=project_root)
    git_log = await run_git(['log', '--oneline', '-n', '5'], cwd=project_root)
    branch = await run_git(['branch', '--show-current'], cwd=project_root)

    context['git_status'] = git_status[:2000]  # 长度限制
    context['git_branch'] = branch
    context['recent_commits'] = git_log

    return context
```

### 3.2 获取用户上下文

```python
def get_user_context():
    """加载所有 CLAUDE.md 文件并合并"""
    all_files = find_claude_files(Path.cwd())
    merged = merge_claude_files(all_files)

    # 按优先级应用覆盖
    final_content = {}
    for item in merged:
        final_content.update(item['content'])

    return final_content
```

### 3.3 构建系统提示词

```python
def build_system_prompt(static_parts, dynamic_parts):
    """
    构建分段的系统提示词

    静态部分（可全局缓存）：
    - 身份定义
    - 基础工具说明

    动态部分（会话级缓存）：
    - 记忆内容
    - 环境信息
    """
    STATIC_BOUNDARY = "__SYSTEM_PROMPT_DYNAMIC_BOUNDARY__"

    static_content = '\n'.join(static_parts)
    dynamic_content = '\n'.join(dynamic_parts)

    return f"{static_content}\n{STATIC_BOUNDARY}\n{dynamic_content}"
```

## 步骤 4：实现压缩

### 4.1 Token 计数检查

```python
import tiktoken

def count_tokens(messages):
    """估算消息的 token 数量"""
    encoding = tiktoken.encoding_for_model("claude-3-sonnet-20240229")
    total = 0
    for msg in messages:
        total += len(encoding.encode(msg['content']))
    return total

def maybe_compress(messages, max_tokens=200000):
    """检查是否需要压缩"""
    if count_tokens(messages) > max_tokens * 0.8:
        return compress_conversation(messages)
    return messages
```

### 4.2 压缩实现

```python
async def compress_conversation(messages):
    """生成对话摘要"""
    # 1. 剥离图像
    stripped = strip_images(messages)

    # 2. 选择压缩的轮次（保留最近 10 轮）
    to_compress = stripped[:-10]

    # 3. 调用 Claude 生成摘要
    summary = await call_claude(
        system="你是一个对话压缩助手。将以下对话总结为简洁的摘要。",
        messages=to_compress
    )

    # 4. 替换历史
    compressed_history = [
        {
            'role': 'system',
            'content': f"这是之前对话的摘要：\n\n{summary}"
        }
    ] + stripped[-10:]

    return compressed_history
```

## 步骤 5：Prompt 缓存集成

### 5.1 缓存键生成

```python
import hashlib
import json

def make_cache_key(static_prefix, user_context, system_context):
    """生成提示词缓存键"""
    key_material = json.dumps({
        'static': static_prefix,
        'user': user_context,
        'system': system_context
    }, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(key_material.encode()).hexdigest()
```

### 5.2 API 调用时设置缓存

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=4096,
    system=system_prompt,  # 分段内容
    messages=messages,
    extra_headers={
        "anthropic-beta": "prompt-caching-2024-07-31"
    }
)
```

**分段缓存控制**：

```python
system_blocks = [
    {
        "type": "text",
        "text": static_prefix,
        # 无 cache_control → 默认全局缓存
    },
    {
        "type": "text",
        "text": f"\n{DYNAMIC_BOUNDARY}\n",
        "cache_control": {"type": "ephemeral"}  # 边界标记不缓存
    },
    {
        "type": "text",
        "text": dynamic_content,
        "cache_control": {"type": "persistent", "ttl": "session"}
    }
]
```

## 步骤 6：自动记忆提取

### 6.1 在对话结束时触发

```python
async def maybe_extract_memories(conversation_history, user_input, assistant_response):
    """在完整响应后自动提取记忆"""

    # 构建 transcript
    transcript = format_transcript(conversation_history + [
        {"role": "user", "content": user_input},
        {"role": "assistant", "content": assistant_response}
    ])

    # 调用提取代理
    extraction_prompt = f"""
    分析以下对话，提取值得保存的记忆。

    对话：
    {transcript}
    """

    result = await call_claude(
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": extraction_prompt}]
    )

    # 解析并保存记忆
    memories = parse_memories(result.content)
    for memory in memories:
        save_memory(memory)
```

### 6.2 保存记忆

```python
def save_memory(memory_data, memory_type=None):
    """保存记忆到文件"""
    memory_type = memory_type or memory_data['type']
    memory_dir = Path.home() / '.claude' / 'memory'

    # 生成文件名
    title_slug = slugify(memory_data['title'])
    filename = f"{memory_type}_{title_slug}.md"
    filepath = memory_dir / filename

    # 写入文件
    content = format_memory_file(memory_data)
    filepath.write_text(content)

    # 更新索引
    update_memory_index(memory_dir, filename, memory_data['title'])
```

## 性能优化

### 1. 增量更新
- 仅扫描修改的记忆文件
- 缓存已解析的 frontmatter

### 2. 并行加载
```python
import asyncio

async def load_all_contexts():
    tasks = [
        get_system_context(),
        get_user_context(),
        load_memory_prompt()
    ]
    return await asyncio.gather(*tasks)
```

### 3. 智能选择相关记忆
```python
def find_relevant_memories(query: str, top_k: int = 5):
    """基于相关性检索记忆"""
    # 简单的关键词匹配（可替换为向量搜索）
    scores = {}
    for memory in all_memories:
        score = compute_relevance(query, memory.content)
        scores[memory.id] = score

    # 返回 top-k
    return sorted(scores, key=scores.get, reverse=True)[:top_k]
```

## 测试

### 单元测试
```python
def test_memory_creation():
    system = MemorySystem()
    system.save_memory({
        'type': 'user',
        'title': 'Test User',
        'content': 'Test content'
    })
    assert (system.memory_root / 'user_test-user.md').exists()

def test_claude_file_discovery():
    files = find_claude_files(Path('/path/to/project'))
    assert len(files) > 0
```

### 集成测试
```python
def test_context_building():
    context = build_context(
        user_input="写一个 Python 脚本",
        project_root="/path/to/project"
    )
    assert 'git_status' in context['system']
    assert 'user_preferences' in context['user']
```

## 生产就绪检查清单

- [ ] 记忆目录自动创建
- [ ] 文件锁处理并发写入
- [ ] 路径遍历安全检查
- [ ] Frontmatter 验证
- [ ] 循环引用检测（@include）
- [ ] 文件大小限制
- [ ] 异常处理和日志
- [ ] 缓存失效策略
- [ ] 备份机制（记忆文件 Git 友好）
- [ ] 迁移路径（版本升级）

## 参考资料

完整实现参考：
- `src/memdir/memdir.ts` - 记忆文件系统（TypeScript, 21K 行）
- `src/context.ts` - 上下文获取（TypeScript, 6K 行）
- `src/services/compact/compact.ts` - 压缩引擎（TypeScript, 17K 行）
- `src/utils/claudemd.ts` - CLAUDE.md 解析（TypeScript, 14K 行）

这些模块共同构成了 Claude Code 的上下文管理核心。
