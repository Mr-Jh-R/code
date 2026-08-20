# SDD 工作流 Skill 包

> **Claude Code + OpenSpec + Superpowers 三件套**，规范驱动开发（SDD）完整工具包，开箱即用。

## 📦 包含内容

```
sdd-skill-repo/
├── skills/
│   └── sdd-workflow.md          # 核心 Skill（AI 工作流完整指令）
├── conventions/
│   ├── frontend-conventions.md  # 前端代码规范
│   └── backend-conventions.md   # 后端代码规范
└── README.md
```

## 🎯 解决什么问题？

传统"Vibe Coding"的三个致命缺陷：
- AI 在长对话后遗忘早期约束，brainstorm 中否决的方案在第 50 轮被重新提出
- `/clear` 释放上下文后，之前达成的共识全部丢失
- AI 没有纪律：不会主动先写测试、不会系统定位 bug 根因、不会在写代码前检查 spec

本 Skill 通过 **三件套协同** 彻底解决：

| 工具 | 职责 | 核心价值 |
|------|------|---------|
| **OpenSpec** | 管"写什么" | 规范的单一真相源，提案-审查-实施-归档 |
| **Superpowers** | 管"怎么做" | AI 执行的纪律警察，强制四步流程 |
| **Claude Code** | 管"谁来跑" | SDD 的最佳执行引擎 |

---

## 🚀 快速安装（10 分钟）

### 第一步：克隆本仓库

```bash
git clone https://github.com/Mr-Jh-R/code.git sdd-skills
```

### 第二步：安装 Superpowers

在 Claude Code 会话中执行：

```
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

### 第三步：安装 OpenSpec CLI

```bash
npm install -g @fission-ai/openspec@latest
```

### 第四步：复制 Skill 到你的项目

```bash
# 在你的项目根目录执行
mkdir -p .claude/skills
cp sdd-skills/skills/sdd-workflow.md .claude/skills/

mkdir -p docs/conventions
cp sdd-skills/conventions/frontend-conventions.md docs/conventions/
cp sdd-skills/conventions/backend-conventions.md docs/conventions/
```

### 第五步：初始化 OpenSpec

```bash
cd your-project
openspec init
```

### 第六步：配置 CLAUDE.md

在项目根目录的 `CLAUDE.md` 中添加（让规范在每次对话自动生效）：

```markdown
## AI 开发工作流（SDD）

本项目采用规范驱动开发（SDD），三件套：OpenSpec + Superpowers + Claude Code。

### 技术栈
- 语言/框架：[填写你的技术栈]
- 包管理器：[pnpm / npm / maven / go]
- 数据库迁移工具：[Drizzle / Flyway / Liquibase]
- 测试框架：[vitest / JUnit / pytest]

### 代码规范引用
- 前端规范：`docs/conventions/frontend-conventions.md`
- 后端规范：`docs/conventions/backend-conventions.md`
- Skill 文件：`.claude/skills/sdd-workflow.md`

### 开发四步原则
1. **需求先探索**：不清晰的需求先 brainstorm 澄清
2. **规范先制定**：用 `openspec propose` 生成 proposal/design/tasks
3. **测试先编写**：TDD，实现前先写测试
4. **验证后声称完成**：运行测试和类型检查通过才能说完成

### 分支命名规范
- 功能分支：`feature/功能简称`
- 修复分支：`fix/问题描述`
- 分支名与 OpenSpec change name 保持一致
```

---

## 📋 工作流速查

### 完整开发流程

```
Brainstorm → Git Worktree → Write a Plan (propose) → Execute (apply + TDD) → Verify → Archive
```

**核心理念：Action Not Phases**——每个操作是独立能力，不是必须按顺序完成的阶段。小修复可跳过 brainstorm 直接 propose，大特性走完整流程。

### 常用命令速查

```bash
# 需求探索（对话触发）
# → "我想做 [功能]，请先 brainstorm"

# 规范制定
openspec propose [change-name]

# 工作区隔离（对话触发）
# → "开始实现 [change-name]"

# TDD 实现
openspec apply [change-name]

# 查看变更列表
openspec list

# 验证（三维度：完整性 × 正确性 × 一致性）
openspec verify [change-name]

# 中断后恢复
openspec continue [change-name]

# 归档
openspec archive [change-name]
```

### 对话触发关键词

| 场景 | 对话指令 |
|------|---------|
| 需求不清晰 | `我想做 [功能]，请先 brainstorm` |
| 开始实现 | `开始实现 [change-name]` |
| TDD 实现 | `请按 TDD 方式实现 tasks.md 中的任务` |
| 遇到 bug | `遇到这个 bug：[描述]，请系统化分析根因，不要直接给解决方案` |
| 代码审查 | `请审查这段代码，对照 [design.md] 检查是否符合设计规范` |
| 中断恢复 | `继续上次 [change-name] 的任务` |

---

## 📚 规范文件说明

### 前端规范（`conventions/frontend-conventions.md`）

适用于 React / Vue / Next.js / Umi 项目：
- API 接口自动生成（`@umijs/openapi`），禁止手写 fetch/axios
- 组件使用优先级：`@ant-design/x` > `Ant Design 5` > `ProComponents` > 社区库 > 手写
- 类型命名规范：`API.XxxRequest` / `API.XxxVO`
- 响应格式统一：`BaseResponse`，用 `res.code === 0` 判断成功

### 后端规范（`conventions/backend-conventions.md`）

适用于 Spring Boot / Java 项目：
- 分层架构：`controller → service → mapper`
- 统一响应体：`BaseResponse<T>` + `ResultUtils`
- 异常体系：`ErrorCode` 枚举 + `BusinessException` + `ThrowUtils`
- 权限注解：`@AuthCheck(mustRole="admin")`
- Entity 规范：雪花 ID、逻辑删除（`@TableLogic`）、Javadoc

---

## 🔧 技术栈适配

本 Skill 设计为**技术栈无关**，内置模板支持：

| 层 | 支持 |
|----|------|
| 前端 | React / Vue / Next.js / Umi / Angular |
| 后端 | Java（Spring Boot）/ Go（Gin）/ Python（FastAPI）/ Node.js |
| 数据库迁移 | Drizzle / Flyway / Liquibase / Alembic / golang-migrate |
| 测试框架 | vitest / jest / JUnit / pytest / go test |
| 包管理器 | pnpm / npm / yarn / maven / gradle / go mod |

---

## 🛡️ Superpowers 四步纪律

Superpowers 的核心是强制 AI 遵守四步流程，防止无约束的 Vibe Coding：

1. **Brainstorm** — 探索需求，澄清边界，提出方案，分段确认（一次只问一个问题）
2. **Git Worktree** — 自动创建隔离工作区和功能分支，防止污染主分支
3. **Write a Plan** — 生成 proposal/design/tasks 三件套，形成"不会失忆"的规范文档
4. **Execute** — TDD 实现：先写测试（红）→ 实现（绿）→ 重构（优化），逐任务打勾

---

## 💡 使用技巧

### 避坑指南

- **不要跳过探索阶段**：Brainstorm 是 ROI 最高的环节，30 分钟澄清边界远比编码后返工划算
- **利用 Action Not Phases 灵活性**：小修复可直接 propose，不必每次走完整流程
- **tasks.md 是进度锚点**：中断后 AI 通过 checkbox 状态自动定位，可以安全 /clear
- **设计.md 要记录否决方案**：防止 AI 在第 50 轮对话中重新提出被否决的方案

### 任务中断恢复（三层持久化）

```
第 1 层（项目级）：CLAUDE.md — 每次对话自动读取
第 2 层（功能级）：openspec/changes/[name]/ — proposal + design + tasks（checkbox 就是进度）
第 3 层（代码级）：git worktree + branch — 分支名 = 功能名，commit 历史 = 实现进度
```

任意步骤间可安全 `/clear`，状态在文件系统中，不在对话历史里。

---

## 🤝 参考资料

- [mattpocock/skills](https://github.com/mattpocock/skills) — 工程师技能库（grill-me、tdd、diagnosing-bugs 等）
- [Superpowers Plugin](https://github.com/obra/superpowers) — Claude Code 执行纪律插件
- OpenSpec CLI 帮助：`openspec --help`
