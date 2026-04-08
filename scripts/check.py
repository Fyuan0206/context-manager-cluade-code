#!/usr/bin/env python3
"""
上下文系统检查脚本
验证记忆系统是否正确配置和运行
"""

import sys
from pathlib import Path
import json

def check_user_memory():
    """检查用户级记忆系统"""
    print("🔍 检查用户级记忆系统...")

    home = Path.home()
    issues = []

    # 检查 ~/.claude/memory 目录
    memory_dir = home / '.claude' / 'memory'
    if not memory_dir.exists():
        issues.append("❌ 记忆目录不存在: ~/.claude/memory/")
        print("  建议: 运行 context-manager 的 init 脚本创建")
    else:
        print(f"✓ 记忆目录存在: {memory_dir}")
        files = list(memory_dir.glob('*.md'))
        print(f"  包含 {len(files)} 个记忆文件")

        # 检查 MEMORY.md
        memory_index = memory_dir / 'MEMORY.md'
        if memory_index.exists():
            print(f"✓ MEMORY.md 索引文件存在")
            content = memory_index.read_text()
            # 检查引用格式
            bad_refs = [line for line in content.split('\n')
                       if line.strip().startswith('- [') and '](' not in line]
            if bad_refs:
                issues.append(f"⚠ MEMORY.md 中有 {len(bad_refs)} 条格式错误的引用")
        else:
            issues.append("⚠ 缺少 MEMORY.md 索引文件")

    # 检查 ~/.claude/CLAUDE.md
    user_claude = home / '.claude' / 'CLAUDE.md'
    if user_claude.exists():
        print(f"✓ 用户 CLAUDE.md 存在")
    else:
        issues.append("ℹ 用户 CLAUDE.md 不存在（可选）")

    return issues

def check_project_memory(project_root=None):
    """检查项目级记忆系统"""
    print("\n🔍 检查项目级记忆系统...")

    root = Path(project_root or Path.cwd()).resolve()
    issues = []

    claude_dir = root / '.claude'

    # 检查 .claude 目录
    if not claude_dir.exists():
        issues.append("❌ 项目缺少 .claude/ 目录")
        print(f"  建议: 在 {root} 运行 init 脚本")
        return issues

    print(f"✓ .claude/ 目录存在")

    # 检查 CLAUDE.md
    project_claude = claude_dir / 'CLAUDE.md'
    if project_claude.exists():
        print(f"✓ 项目 CLAUDE.md 存在")

        # 验证 frontmatter
        content = project_claude.read_text()
        if '---' in content:
            frontmatter_end = content.index('---', 3)
            frontmatter = content[4:frontmatter_end]
            if 'type:' in frontmatter or 'paths:' in frontmatter:
                print("  ✓ 包含 frontmatter 配置")
            else:
                issues.append("ℹ CLAUDE.md 没有 frontmatter（可选但推荐）")
    else:
        issues.append("ℹ 项目 CLAUDE.md 不存在（可选）")

    # 检查 rules 目录
    rules_dir = claude_dir / 'rules'
    if rules_dir.exists():
        rule_files = list(rules_dir.glob('*.md'))
        print(f"✓ 包含 {len(rule_files)} 条规则文件")
        for rule in rule_files:
            print(f"  - {rule.name}")
    else:
        print("ℹ rules/ 目录不存在（可选）")

    # 检查 memory 目录
    memory_dir = claude_dir / 'memory'
    if memory_dir.exists():
        print(f"✓ memory/ 目录存在")
        # 检查是否被 git 跟踪
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain', str(memory_dir)],
                capture_output=True, text=True
            )
            if result.stdout:
                issues.append(f"⚠ memory/ 目录未被 gitignore（可能包含敏感数据）")
        except:
            pass
    else:
        print("ℹ memory/ 目录不存在（将在首次使用时自动创建）")

    return issues

def check_claude_files_discovery():
    """检查 CLAUDE.md 文件发现是否正常工作"""
    print("\n🔍 检查 CLAUDE.md 文件发现...")

    # 模拟向上遍历
    current = Path.cwd()
    found = []

    for i in range(10):  # 最多向上 10 层
        for pattern in ['CLAUDE.md', '.claude/CLAUDE.md', 'CLAUDE.local.md']:
            candidate = current / pattern
            if candidate.exists():
                found.append(str(candidate))

        if current.parent == current:
            break
        current = current.parent

    if found:
        print(f"✓ 发现 {len(found)} 个 CLAUDE.md 文件:")
        for f in found:
            print(f"  - {f}")
    else:
        print("ℹ 未发现 CLAUDE.md 文件")

    return []

def check_memory_format():
    """检查现有记忆文件的格式"""
    print("\n🔍 检查记忆文件格式...")

    home = Path.home()
    memory_dir = home / '.claude' / 'memory'

    if not memory_dir.exists():
        print("ℹ 记忆目录不存在，跳过格式检查")
        return []

    issues = []
    md_files = list(memory_dir.glob('*.md'))

    for md_file in md_files:
        if md_file.name == 'MEMORY.md':
            continue

        content = md_file.read_text()
        filename = md_file.name

        # 检查 frontmatter
        if not content.startswith('---'):
            issues.append(f"⚠ {filename}: 缺少 frontmatter")
            continue

        # 解析 frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            issues.append(f"⚠ {filename}: frontmatter 格式错误")
            continue

        frontmatter = parts[1]
        required_fields = ['name', 'type']

        for field in required_fields:
            if f'{field}:' not in frontmatter:
                issues.append(f"⚠ {filename}: 缺少必需字段 '{field}'")

        # 检查 type 有效性
        valid_types = ['user', 'feedback', 'project', 'reference']
        for line in frontmatter.split('\n'):
            if line.startswith('type:'):
                type_value = line.split(':', 1)[1].strip()
                if type_value not in valid_types:
                    issues.append(f"⚠ {filename}: 无效的 type 值 '{type_value}'")

    if issues:
        print(f"发现 {len(issues)} 个格式问题")
    else:
        print("✓ 所有记忆文件格式正确")

    return issues

def main():
    print("="*60)
    print("  Context Manager 系统检查")
    print("="*60)

    all_issues = []

    # 运行检查
    all_issues.extend(check_user_memory())
    all_issues.extend(check_project_memory())
    all_issues.extend(check_claude_files_discovery())
    all_issues.extend(check_memory_format())

    # 汇总报告
    print("\n" + "="*60)
    if all_issues:
        print(f"⚠ 发现 {len(all_issues)} 个问题：")
        for issue in all_issues:
            print(f"  {issue}")
        print("\n💡 建议：")
        print("  运行以下命令修复：")
        print("  python scripts/init.py")
    else:
        print("✅ 所有检查通过！上下文管理系统配置正确。")

    print("="*60)

    return 0 if not all_issues else 1

if __name__ == '__main__':
    sys.exit(main())
