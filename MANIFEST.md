---
name: Context Manager Skill Manifest
description: 技能打包清单和元数据
version: "1.0.0"
based_on: "Claude Code v2.1.92.321"
created: "2026-04-08"
author: "Claude (Anthropic)"
license: "MIT"
---

# 技能清单

## 必需文件

- [x] `SKILL.md` - 技能主文档（369 行）
- [x] `README.md` - 项目说明（417 行）
- [x] `QUICKREF.md` - 快速参考卡

## 脚本文件

- [x] `scripts/init.py` - 项目初始化脚本
- [x] `scripts/check.py` - 系统检查脚本
- [x] `scripts/create_memory.py` - 记忆创建工具

## 参考文档

- [x] `references/implementation-guide.md` - 实现指南
- [x] `references/claude-md-template.md` - CLAUDE.md 模板
- [x] `references/caching.md` - 缓存优化
- [x] `references/compress.md` - 压缩参考
- [x] `references/extraction-prompts.md` - 提取提示词模板

## 测试文件

- [x] `evals/evals.json` - 测试用例（5个场景）

## 文件统计

| 类型 | 文件数 | 总行数 |
|------|--------|--------|
| Markdown 文档 | 9 | ~2,500 |
| Python 脚本 | 3 | ~400 |
| JSON 配置 | 1 | ~100 |
| **总计** | **13** | **~3,000** |

## 技能大小

- 未压缩：约 150 KB
- 打包后（.skill）：约 80 KB

## 依赖

- Python 3.8+（用于脚本）
- 标准库：pathlib, json, datetime, subprocess
- 无第三方依赖

## 安装验证

```bash
# 1. 检查文件完整性
python scripts/check.py

# 2. 验证技能结构
ls -la ~/.claude/skills/context-manager/

# 3. 测试初始化
cd /tmp/test-project
python ~/.claude/skills/context-manager/scripts/init.py
```

## 打包清单

打包前确认：
- [ ] 所有文件编码为 UTF-8
- [ ] 脚本具有可执行权限（chmod +x）
- [ ] 无敏感信息（密钥、密码）
- [ ] 版本号正确
- [ ] README 是最新的

打包后验证：
- [ ] .skill 文件可正常解压
- [ ] SKILL.md 可正常读取
- [ ] 所有相对路径正确

## 版本历史

### v1.0.0 (2026-04-08)
- 初始版本
- 基于 Claude Code v2.1.92.321 源码分析
- 包含完整四型记忆系统说明
- 提供实现指南和参考实现
- 附带实用脚本工具

## 已知限制

1. **Python 脚本**：仅作为参考实现，智能体可能使用其他语言
2. **缓存优化**：具体实现依赖底层 API 支持
3. **自动提取**：需要定期运行的后台代理
4. **团队记忆**：TEAMMEM 特性为可选功能

## 后续改进方向

- [ ] 添加 TypeScript 参考实现
- [ ] 提供 Docker 容器化部署方案
- [ ] 创建 VS Code 扩展集成
- [ ] 添加更多测试用例
- [ ] 性能基准测试脚本
- [ ] 迁移指南（从旧版本）

---

**技能打包时请包含此清单**
