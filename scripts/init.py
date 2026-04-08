#!/usr/bin/env python3
"""
上下文管理器初始化脚本
运行此脚本以在项目中设置完整的上下文管理基础设施
"""

import sys
import os
from pathlib import Path
import subprocess

def run_cmd(cmd, silent=False):
    """运行 shell 命令"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if not silent and result.returncode != 0:
        print(f"❌ 命令失败: {cmd}")
        print(f"   错误: {result.stderr}")
    return result.returncode == 0

def init_context_manager(project_root=None):
    """
    在项目中初始化上下文管理器

    创建以下结构：
    .claude/
    ├── CLAUDE.md           # 项目级记忆
    ├── rules/              # 项目规则
    │   ├── 01-coding.mdown
    │   ├── 02-testing.md
    │   └── 03-security.md
    └── memory/             # 自动记忆（gitignored）
        ├── MEMORY.md
        ├── user.md
        ├── feedback.md
        ├── project.md
        └── reference.md
    """
    root = Path(project_root or Path.cwd()).resolve()
    print(f"📁 初始化目录: {root}")

    # 1. 创建 .claude 目录
    claude_dir = root / '.claude'
    claude_dir.mkdir(exist_ok=True)
    print("✓ 创建 .claude/ 目录")

    # 2. 创建子目录
    (claude_dir / 'rules').mkdir(exist_ok=True)
    (claude_dir / 'memory').mkdir(exist_ok=True)
    print("✓ 创建 rules/ 和 memory/ 子目录")

    # 3. 创建项目级 CLAUDE.md
    claude_md = claude_dir / 'CLAUDE.md'
    if not claude_md.exists():
        project_name = root.name
        claude_md.write_text(f"""---
name: {project_name} 项目规则
description: 适用于 {project_name} 项目的开发规范和指南
paths:
  - src/**/*
  - tests/**/*
  - "!node_modules/**"
---

# 项目：{project_name}

## 概述
在此添加项目简介

## 技术栈
- 后端：
- 前端：
- 数据库：

## 代码风格
（在此定义命名约定、提交规范等）

## 重要文件
- `src/main.*` - 入口文件
- `config/` - 配置目录

## 外部资源
- API 文档：
- 设计稿：
- 问题跟踪：

## 当前状态
（记录项目进度、待办事项、阻塞）

---
*此文件由 context-manager 技能初始化于 {get_today()}*
""", encoding='utf-8')
        print(f"✓ 创建 {claude_md.relative_to(root)}")
    else:
        print(f"ℹ {claude_md.relative_to(root)} 已存在，跳过")

    # 4. 创建用户级 CLAUDE.md（如果不存在）
    user_claude = Path.home() / '.claude' / 'CLAUDE.md'
    if not user_claude.exists():
        user_claude.parent.mkdir(parentist=True)
        user_claude.write_text(f"""---
# 用户配置
---

# 我的配置

## 角色
（你的职位、团队、职责）

## 偏好
### 编码风格
### 沟通风格
### 工作习惯

## 当前项目
（你正在工作的主要项目）

---
*由 context-manager 技能初始化*
""", encoding='utf-8')
        print(f"✓ 创建 {user_claude}")
    else:
        print(f"ℹ 用户 CLAUDE.md 已存在")

    # 5. 创建记忆目录
    user_memory = Path.home() / '.claude' / 'memory'
    user_memory.mkdir(parents=True, exist_ok=True)
    print(f"✓ 确保记忆目录存在: ~/.claude/memory/")

    # 6. 创建 MEMORY.md 索引文件
    memory_index = user_memory / 'MEMORY.md'
    if not memory_index.exists():
        memory_index.write_text("""# 记忆索引

## 关于我
## 反馈记录
## 项目进度
## 参考资料

---
*自动管理：此文件由 context-manager 维护*
""", encoding='utf-8')
        print(f"✓ 创建 {memory_index}")
    else:
        print(f"ℹ MEMORY.md 已存在")

    # 7. 创建示例规则文件
    rules = {
        '01-coding.md': """---
paths:
  - src/**/*.ts
  - src/**/*.py
---

## 代码规范

- 遵循项目的 ESLint/Prettier 配置
- 提交前运行 `npm test`
- 确保类型检查通过
""",
        '02-testing.md': """---
paths:
  - tests/**/*
  - "*.test.ts"
---

## 测试要求

- 新功能必须包含测试
- 覆盖率 > 80%
- 包含边界情况测试
""",
        '03-security.md': """---
paths:
  - src/**/*.ts
  - api/**/*
---

## 安全准则

- 永远不要硬编码密钥
- 用户输入必须验证
- 使用参数化查询
"""
    }

    rules_dir = claude_dir / 'rules'
    for filename, content in rules.items():
        rule_file = rules_dir / filename
        if not rule_file.exists():
            rule_file.write_text(content, encoding='utf-8')
            print(f"✓ 创建规则: rules/{filename}")
        else:
            print(f"ℹ 规则 {filename} 已存在")

    # 8. 更新 .gitignore
    gitignore = root / '.gitignore'
    if gitignore.exists():
        content = gitignore.read_text()
        entries_to_add = [
            '.claude/CLAUDE.local.md',
            '.claude/memory/',  # 本地自动记忆不提交
        ]
        for entry in entries_to_add:
            if entry not in content:
                with open(gitignore, 'a') as f:
                    f.write(f'\n# Claude Code context manager\n{entry}\n')
                print(f"✓ 更新 .gitignore: {entry}")

    # 9. 验证安装
    print("\n" + "="*50)
    print("✅ 初始化完成！")
    print("="*50)
    print("\n下一步：")
    print("1. 编辑 .claude/CLAUDE.md 添加项目特定规则")
    print("2. 编辑 ~/.claude/CLAUDE.md 添加个人偏好")
    print("3. 开始编码，context-manager 会自动工作")
    print("\n测试命令：")
    print(f"  cd {root}")
    print("  尝试说：'记住我喜欢用 Prettier 格式化代码'")
    print("\n查看记忆：")
    print("  ls ~/.claude/memory/")
    print("  cat ~/.claude/memory/MEMORY.md")

def get_today():
    """获取今天的日期"""
    from datetime import datetime
    return datetime.now().strftime('%Y-%m-%d')

def main():
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = None

    try:
        init_context_manager(project_root)
    except KeyboardInterrupt:
        print("\n❌ 初始化取消")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
