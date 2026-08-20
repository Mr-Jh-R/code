---
name: sdd-workflow
description: SDD（规范驱动开发）完整工作流 Skill，整合 OpenSpec + Superpowers + Claude Code 三件套。当用户要开始新功能、修复 bug、变更数据库 Schema、设计 API 接口，或说"开始做 XXX"、"我想实现 XXX"、"如何开发 XXX"时，必须使用本 Skill。包含需求探索(grill-me)、规范制定、Superpowers 四步纪律、TDD 实现、系统化调试、验证闭环、三层持久化等完整流程。
---

## 配套规范文件

> 将以下文件复制到项目后，在 CLAUDE.md 中引用路径，AI 每次对话自动加载。

| 文件 | 说明 |
|------|------|
| `conventions/frontend-conventions.md` | 前端规范：API 自动生成、组件优先级、类型命名 |
| `conventions/backend-conventions.md` | 后端规范：分层架构、响应体、异常体系、权限注解 |

---

## 三件套分工

| 工具 | 职责 | 核心价值 |
|------|------|---------|
| **OpenSpec** | 管"写什么" | 规范的单一真相源，提案-审查-实施-归档 |
| **Superpowers** | 管"怎么做" | AI 执行的纪律警察，强制四步流程 |
| **Claude Code** | 管"谁来跑" | SDD 的最佳执行引擎 |

**核心理念：Action Not Phases**——每个操作是独立能力，不是必须按顺序完成的阶段。大特性走完整流程，小修复可直接 propose，这不是"违规"而是灵活组合能力。

---

## 安装

```bash
# 安装 Superpowers（在 Claude Code 会话中执行）
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace

# 安装 OpenSpec CLI
npm install -g @fission-ai/openspec@latest

# 在项目根目录初始化 OpenSpec
openspec init
```

---

## Superpowers 强制四步流程

Superpowers 的核心是强制 AI 遵守四步纪律，防止"Vibe Coding"：

### Step 1：Brainstorm（头脑风暴）

**触发方式：**
```
我想做 [功能描述]，请先 brainstorm
```

**AI 执行流程：**
1. 探索项目结构，理解现有架构和约束
2. **一次只问一个问题**，逐步澄清需求：
   - 功能边界：哪些在范围内，哪些明确不做？
   - 用户场景：谁在什么情况下使用？
   - 异常处理：错误如何处理？幂等性如何保证？
   - 性能约束：并发量、响应时间要求？
3. 提出 2-3 种技术方案，列出对比
4. **分段展示设计，逐段确认**（不一次性输出所有内容）
5. 将达成共识的设计写入 `docs/specs/[feature-name].md` 并 commit

**产出物模板：**
```markdown
# 功能探索：[功能名称]

## 需求澄清
- 核心目标：
- 用户角色：
- In Scope：
- Out of Scope（明确不做）：

## 边界条件
- 异常场景：
- 幂等性处理：
- 并发约束：

## 方案对比
| 方案 | 优点 | 缺点 | 推荐 |
|------|------|------|------|
| 方案 A | | | |
| 方案 B | | | |

## 结论
采用方案 X，理由：
```

> **为什么不跳过？** Brainstorm 是整个流程 ROI 最高的环节。30 分钟澄清边界，远比编码后返工划算——返工成本至少翻三倍。

---

### Step 2：Git Worktree（工作区隔离）

**触发方式：**
```
开始实现 [change-name]
```

Superpowers 自动执行：
1. 创建 `.worktrees/[change-name]` 隔离工作区
2. 新建 `feature/[change-name]` 分支
3. 运行依赖安装
4. 验证测试基线通过

**为什么要隔离？** 主工作区保持干净，多个功能可以并行开发互不干扰。分支名 = OpenSpec change name，保持一致。

---

### Step 3：Write a Plan（规范制定）

```bash
openspec propose [change-name]
# 例：openspec propose add-user-login-api
```

**自动生成三个文件：**

**`proposal.md`（为什么做）**
```markdown
# Proposal: [change-name]

## Why
[业务背景和痛点]

## Goals
- [ ] 目标 1（可验证）
- [ ] 目标 2

## Non-Goals
- 不支持 X（本次范围外）

## Impact
- 模块 A：变更说明
- 数据库：新增/修改哪些表
```

**`design.md`（怎么做）**
```markdown
# Design: [change-name]

## 技术方案
[选择的方案及理由]

## 替代方案
[被否决的方案及原因——防止 AI 在第 50 轮对话中重新提出]

## 接口设计
[API 定义、数据结构]
```

**`tasks.md`（做什么，checkbox 就是进度）**
```markdown
# Tasks: [change-name]

- [ ] 任务 1：描述（含验收标准）
- [ ] 任务 2：描述
- [ ] 编写单元测试
- [ ] 更新 API 文档
```

**Scenario 格式（`specs/` 目录，GIVEN/WHEN/THEN 确保可验证）：**
```markdown
### Scenario: [场景名称]
- GIVEN [前置条件]
- WHEN [触发动作]
- THEN [期望结果]
- AND [附加断言]
```

---

### Step 4：Execute（TDD 实现）

```bash
openspec apply [change-name]
# 或在对话中：请按 TDD 方式实现 tasks.md 中的任务
```

**实现模式 A：Subagent-Driven（大功能推荐）**
1. 主 Agent 读取 tasks.md，提取每个任务
2. 派发 Subagent 实现任务（TDD：写测试 → 红 → 实现 → 绿 → 重构）
3. 派发 Spec Reviewer 检查是否符合 design.md
4. 派发 Code Reviewer 检查代码质量
5. tasks.md 对应任务打勾 `[x]`
6. 循环直到全部完成

**实现模式 B：直接执行（小功能）**
AI 在当前会话中逐任务实现，每完成一个打勾。

#### TDD 铁律

```
写测试（红） → 实现代码（绿） → 重构（优化）
```

AI **必须先写测试，确认测试方案后再实现**。测试覆盖：
- 正常路径（Happy Path）
- 边界条件（Edge Cases）
- 错误路径（Error Cases）

**测试模板（JS/TS）：**
```typescript
import { describe, it, expect } from 'vitest'

describe('[模块名]', () => {
  it('正常路径：should ...', async () => {
    // Arrange
    // Act
    // Assert
  })
  it('边界条件：should handle ...', async () => {})
  it('错误路径：should throw when ...', async () => {})
})
```

**测试模板（Java/JUnit）：**
```java
class ServiceTest {
    @Test
    void shouldReturnSuccessWhenValidInput() {
        // Given / When / Then
    }
    @Test
    void shouldThrowExceptionWhenInvalidInput() {}
}
```

---

## 验证与归档

### 验证（三维度检查）

```bash
openspec verify [change-name]   # 完整性 × 正确性 × 一致性
```

验证通过后，Superpowers 接管收尾：
- 自动运行全量测试
- 提供四个选项：合并 / 创建 PR / 保留分支 / 丢弃
- 清理 worktree

**声称"完成"前必须执行的验证命令（按项目填写）：**
```bash
# 前端
pnpm typecheck && pnpm test && pnpm lint

# 后端（Java）
mvn test

# 后端（Go）
go test ./...

# OpenSpec 验证
openspec verify [change-name]
```

**不允许声称完成的场景：**
- 未运行测试
- 未检查类型错误
- 未对照 specs 验证场景覆盖

### 归档

```bash
openspec archive [change-name]
```

变更目录自动移入 `openspec/changes/archive/[date]-[name]/`，Delta Spec 合并回主规范库。任何人（包括未来的 AI）都能追溯：当初为什么这样设计、做了哪些技术选型、考虑了哪些替代方案。

---

## 三层持久化（AI 不会"失忆"）

AI 有两个致命限制：上下文窗口有限（长对话后忘记前期约束）、会话不持久（关窗口 = 归零）。SDD 通过三层持久化解决：

| 层级 | 载体 | 内容 |
|------|------|------|
| **第 1 层：项目级** | `CLAUDE.md` + `openspec/config.yaml` | 每次新对话自动读取，相当于"置顶备忘录" |
| **第 2 层：功能级** | `openspec/changes/[name]/` | proposal（为什么做）、design（怎么组织）、tasks（做到哪了）|
| **第 3 层：代码级** | git worktree + branch | 分支名=功能名，commit 历史=实现进度 |

**中断后恢复：**
```bash
openspec list                          # 查看当前变更状态
openspec continue [change-name]        # 从未完成任务继续
```

任意步骤之间可以安全 `/clear`，状态在文件系统中，不在对话历史里。

---

## 系统化调试

**遇到 bug 时，先分析根因，再提解决方案。**

**触发方式：**
```
遇到这个 bug：[描述]，请系统化分析根因，不要直接给解决方案
```

**七步调试流程：**
1. **重现问题**：确认 bug 可以稳定复现
2. **收集信息**：查看错误日志、最近 git 变更（`git log --oneline -10`、`git diff HEAD~1`）
3. **形成假设**：列出 2-3 个可能根因
4. **验证假设**：用最小测试用例逐一验证
5. **定位根因**：确认真正的问题所在
6. **修复**：只修改必要的代码
7. **验证修复**：确认测试通过，无副作用

**常见问题排查：**

| 问题类型 | 排查方向 |
|---------|---------|
| 数据库字段不存在 | Schema 变更是否已生成迁移并应用？ |
| 认证失败 | Token/Cookie 是否正确传递？ |
| 前后端数据不一致 | 接口响应格式与文档是否匹配？ |
| 环境变量缺失 | `.env.local` 是否配置正确？ |
| 依赖服务连接失败 | 服务是否启动、端口是否正确？ |

---

## 代码审查 Checklist

**触发方式：**
```
请审查这段代码，对照 [design.md路径] 检查是否符合设计规范
```

**四维度审查：**
1. **正确性**：是否实现了 specs 定义的所有 Scenario？
2. **完整性**：是否覆盖了所有边界条件？
3. **一致性**：是否符合项目编码规范？
4. **安全性**：是否有权限校验？数据是否验证？

**通用 Checklist：**
- [ ] 是否有对应的测试用例？
- [ ] 错误是否有统一处理？
- [ ] 是否有遗漏的异常场景？
- [ ] 是否符合项目包管理器规范（不混用）？
- [ ] 数据库操作是否通过正确的抽象层？
- [ ] 涉及权限的接口是否有鉴权？
- [ ] 外部调用是否有超时控制？
- [ ] 涉及数据库变更的是否已生成并应用迁移？

---

## 完整工作流示例

以"添加用户头像上传功能"为例：

```
# Step 1: 需求探索（需求清晰可跳过）
对话："我想做用户头像上传，请先 brainstorm"
→ AI 逐一提问澄清边界，输出方案对比

# Step 2: 规范制定
openspec propose add-user-avatar-upload
→ 自动生成 proposal.md / design.md / tasks.md

# Step 3: 工作区隔离（对话触发）
对话："开始实现 add-user-avatar-upload"
→ Superpowers 自动创建 worktree + 分支

# Step 4: TDD 实现
openspec apply add-user-avatar-upload
→ 主 Agent 派发子 Agent，TDD 逐任务实现，tasks.md 打勾

# Step 5: 数据库变更（如涉及）
# 按项目迁移工具执行（Drizzle / Flyway 等）

# Step 6: 验证
openspec verify add-user-avatar-upload
pnpm typecheck && pnpm test   # 按项目调整命令

# Step 7: 归档
openspec archive add-user-avatar-upload
```

---

## CLAUDE.md 配置模板

新项目使用本 Skill 时，在 `CLAUDE.md` 中添加：

```markdown
## AI 开发工作流（SDD）

本项目采用规范驱动开发（SDD），三件套：OpenSpec + Superpowers + Claude Code。

### 技术栈（按项目填写）
- 语言/框架：___________
- 包管理器：___________
- 数据库迁移工具：___________
- 测试框架：___________

### Skill 文件
- 工作流：`.claude/skills/sdd-workflow.md`
- 前端规范：`docs/conventions/frontend-conventions.md`
- 后端规范：`docs/conventions/backend-conventions.md`

### 四步原则
1. **先 Brainstorm**：需求不清晰时，一次只问一个问题，逐步澄清
2. **先 Propose**：用 openspec propose 生成 proposal/design/tasks
3. **先写测试**：TDD 铁律，实现前先写测试
4. **验证再完成**：测试通过、类型检查通过才能声称完成

### 分支命名
- 功能分支：feature/[openspec-change-name]
- 修复分支：fix/[问题描述]
- 分支名与 OpenSpec change name 保持一致
```

---

## 在新项目中安装

```bash
# 1. 克隆 skill 仓库
git clone https://github.com/Mr-Jh-R/code.git sdd-skills

# 2. 复制文件到项目
mkdir -p .claude/skills docs/conventions
cp sdd-skills/skills/sdd-workflow.md .claude/skills/
cp sdd-skills/conventions/frontend-conventions.md docs/conventions/
cp sdd-skills/conventions/backend-conventions.md docs/conventions/

# 3. 安装工具
npm install -g @fission-ai/openspec@latest
openspec init

# 4. 在 Claude Code 中安装 Superpowers
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace

# 5. 在项目 CLAUDE.md 中按上方模板配置
```

---

## 参考资料

- [mattpocock/skills](https://github.com/mattpocock/skills) — 工程师技能库（grill-me、tdd、diagnosing-bugs 等原版技能）
- [Superpowers Plugin](https://github.com/obra/superpowers) — Claude Code 执行纪律插件
- OpenSpec 文档：`openspec --help`
