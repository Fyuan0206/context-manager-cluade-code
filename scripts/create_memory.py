#!/usr/bin/env python3
"""
记忆文件创建脚本 - 帮助智能体快速创建标准格式的记忆文件
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import argparse

def create_memory_file(memory_type: str, title: str, content: str, memory_dir: str = None):
    """
    创建标准格式的记忆文件

    Args:
        memory_type: 记忆类型 (user/feedback/project/reference)
        title: 记忆标题
        content: 记忆正文内容
        memory_dir: 记忆目录路径（默认自动检测）
    """
    valid_types = ['user', 'feedback', 'project', 'reference']
    if memory_type not in valid_types:
        print(f"错误：记忆类型必须是 {valid_types} 之一")
        return False

    # 自动检测记忆目录
    if memory_dir is None:
        # 尝试常见的位置
        candidates = [
            Path.home() / '.claude' / 'memory',
            Path.cwd() / '.claude' / 'memory',
            Path.cwd() / '..' / '.claude' / 'memory',
        ]
        for candidate in candidates:
            if candidate.exists():
                memory_dir = str(candidate)
                break
        if memory_dir is None:
            memory_dir = str(Path.home() / '.claude' / 'memory')
            os.makedirs(memory_dir, exist_ok=True)

    # 生成文件名（标题转 snake_case）
    filename = title.lower().replace(' ', '-').replace('_', '-')
    filename = ''.join(c if c.isalnum() or c == '-' else '' for c in filename)
    filename = f"{memory_type}_{filename}.md"

    filepath = Path(memory_dir) / filename

    # 构建文件内容
    today = datetime.now().strftime('%Y-%m-%d')
    file_content = f"""---
name: {title}
description: 自动创建的记忆条目
type: {memory_type}
---

{content}

**创建日期:** {today}
**自动管理:** 此文件由 context-manager 技能管理
"""

    # 写入文件
    filepath.write_text(file_content, encoding='utf-8')
    print(f"✓ 已创建记忆文件: {filepath}")

    # 更新 MEMORY.md 索引
    update_memory_index(str(Path(memory_dir).parent), filename, title)

    return True

def update_memory_index(memory_root: str, filename: str, title: str):
    """更新 MEMORY.md 索引文件"""
    memory_md = Path(memory_root) / 'MEMORY.md'

    if not memory_md.exists():
        # 创建新的索引文件
        index_content = f"""# 记忆索引

- [{title}](./memory/{filename}) — 自动添加

"""
        memory_md.write_text(index_content, encoding='utf-8')
        return

    # 读取现有索引
    content = memory_md.read_text(encoding='utf-8')

    # 在适当位置插入新条目（保持分类）
    categories = {
        'user': '## 关于我',
        'feedback': '## 反馈记录',
        'project': '## 项目进度',
        'reference': '## 参考资料'
    }

    category = categories.get(filename.split('_')[0], '## 其他')
    new_entry = f"- [{title}](./memory/{filename}) — 自动添加"

    if category in content:
        # 在分类后插入
        lines = content.split('\n')
        new_lines = []
        inserted = False
        for i, line in enumerate(lines):
            new_lines.append(line)
            if line == category and not inserted:
                # 找到下一个标题或文件条目位置
                j = i + 1
                while j < len(lines) and not lines[j].startswith('##'):
                    j += 1
                # 插入新条目
                new_lines.append(new_entry)
                inserted = True
        memory_md.write_text('\n'.join(new_lines), encoding='utf-8')
    else:
        # 追加到末尾
        memory_md.write_text(content + '\n' + new_entry + '\n', encoding='utf-8')

    print(f"✓ 已更新索引: {memory_md}")

def main():
    parser = argparse.ArgumentParser(description='创建标准格式的记忆文件')
    parser.add_argument('--type', required=True, choices=['user', 'feedback', 'project', 'reference'],
                        help='记忆类型')
    parser.add_argument('--title', required=True, help='记忆标题')
    parser.add_argument('--content', required=True, help='记忆正文内容')
    parser.add_argument('--dir', help='记忆目录路径（可选，自动检测）')

    args = parser.parse_args()

    success = create_memory_file(args.type, args.title, args.content, args.dir)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
