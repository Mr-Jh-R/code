# SDD 开发工作流 Skill

## 概述

本 Skill 整合了 SDD（规范驱动开发）最佳实践，包含需求探索（grill-me）、规范制定、TDD 实现、系统化调试、代码审查等完整工作流。适用于任何多模块 AI 辅助开发项目，**与具体项目无关，按照新项目实际情况填充配置区即可**。

## 📎 配套规范文件

> 安装本 Skill 后，将以下规范文件复制到项目中，并在 CLAUDE.md 中引用路径。

| 文件 | 路径 | 说明 |
|------|------|------|
| 前端规范 | `conventions/frontend-conventions.md` | API 自动生成、组件优先级、类型命名规范 |
| 后端规范 | `conventions/backend-conventions.md` | 分层架构、响应体、异常体系、权限注解 |

**AI 读取规范的方式**：在 CLAUDE.md 中声明路径后，每次对话 AI 自动加载。示例：

```markdown
## 代码规范引用
- 前端规范：`docs/conventions/frontend-conventions.md`
- 后端规范：`docs/conventions/backend-conventions.md`
```

---

## 🔧 新项目配置区（使用前填写）

```
项目名称：___________
技术栈：___________（例：Next.js + Spring Boot + PostgreSQL）
包管理器：___________（例：pnpm / npm / maven）
测试框架：___________（例：vitest / JUnit）
数据库迁移工具：___________（例：Drizzle / Flyway / Liquibase）
分支命名约定：feature/xxx | fix/xxx
```

---

## 安装依赖

```bash
# 安装 OpenSpec CLI（规范驱动开发框架）
npm install -g @fission-ai/openspec@latest

# 在项目根目录初始化 OpenSpec
cd your-project
openspec init
```

---

## 工作流总览

```
需求探索(grill-me) → 规范制定(propose) → 工作区隔离(worktree) → TDD实现(apply) → 验证(verify) → 归档(archive)
```

> **Action Not Phases 原则**：每个操作是独立能力，不是必须按顺序完成的阶段。小修复可跳过探索直接 propose，大特性走完整流程。

---

## Skill 一：需求探索（grill-me）

### 何时使用
- 需求不清晰，只有截图或模糊描述时
- 开始新功能前，需要澄清边界条件时
- 产品文档缺失，需要从用户角度推导需求时

### 使用方式

在对话中触发：
```
我想做 [功能描述]，请用 grill-me 模式帮我探索需求
```

### AI 执行流程

1. **探索项目结构**：理解现有代码架构和约束
2. **逐一提问**（一次只问一个问题）：
   - 功能边界：哪些在范围内，哪些明确不做？
   - 用户场景：谁在什么情况下使用？
   - 异常情况：错误如何处理？幂等性如何保证？
   - 性能约束：并发量、响应时间要求？
3. **提出 2-3 种方案**：列出技术选型对比
4. **逐段确认设计**：分段展示，逐步确认
5. **输出结构化文档**：写入 `docs/specs/[feature-name].md`

### 产出物模板

```markdown
# 功能探索：[功能名称]

## 需求澄清
- 核心目标：
- 用户角色：
- 功能范围（In Scope）：
- 明确不做（Out of Scope）：

## 边界条件
- 异常场景：
- 幂等性处理：
- 并发约束：

## 方案对比
| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| 方案 A | | | |
| 方案 B | | | |

## 结论
采用方案 X，理由：
```

---

## Skill 二：规范制定（propose）

### 使用方式
```bash
openspec propose [change-name]
# 例：openspec propose add-user-refund-feature
```

### 自动生成三个文件

**proposal.md**（为什么做）
```markdown
# Proposal: [change-name]

## Why
[业务背景和痛点]

## Goals
- [ ] 目标 1
- [ ] 目标 2

## Non-Goals
- 不支持 X（本次范围外）

## Impact
- 模块 A：变更说明
- 数据库：新增/修改哪些表
```

**design.md**（怎么做）
```markdown
# Design: [change-name]

## 技术方案
[选择的方案及理由]

## 替代方案
[被否决的方案及原因]

## 接口设计
[API 定义、数据结构]
```

**tasks.md**（做什么）
```markdown
# Tasks: [change-name]

- [ ] 任务 1：描述（含验收标准）
- [ ] 任务 2：描述
- [ ] 编写单元测试
- [ ] 更新 API 文档
```

### Scenario 格式（specs/ 目录）
```markdown
### Scenario: [场景名称]
- GIVEN [前置条件]
- WHEN [触发动作]
- THEN [期望结果]
- AND [附加断言]
```

---

## Skill 三：TDD 实现

### 铁律：测试先行

```
写测试（红） → 实现代码（绿） → 重构（优化）
```

### 对话触发方式
```
请用 TDD 方式实现 [功能]，先写测试，确认测试定义正确后再写实现
```

### AI 执行步骤

1. **阅读 tasks.md**，理解当前任务
2. **写测试文件**：
   - 覆盖正常路径（Happy Path）
   - 覆盖边界条件（Edge Cases）
   - 覆盖错误路径（Error Cases）
3. **确认测试方案**：向用户展示测试用例，等待确认
4. **实现最小可用代码**：让测试从红变绿
5. **重构**：在测试保护下优化代码质量
6. **打勾 tasks.md**：完成一个任务后更新 checkbox

### 测试文件模板

#### JavaScript / TypeScript（vitest / jest）
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

#### Java（JUnit）
```java
class ServiceTest {
    @Test
    void shouldReturnSuccessWhenValidInput() {
        // Given
        // When
        // Then
    }

    @Test
    void shouldThrowExceptionWhenInvalidInput() {}
}
```

---

## Skill 四：系统化调试

### 使用时机
遇到 bug、测试失败、意外行为时，**先调试再提方案**。

### 对话触发方式
```
遇到这个 bug：[描述]，请系统化地帮我分析根因，不要直接给解决方案
```

### 调试步骤

1. **重现问题**：确认 bug 可以稳定复现
2. **收集信息**：
   ```bash
   git log --oneline -10   # 查看最近变更
   git diff HEAD~1          # 对比差异
   ```
3. **形成假设**：列出 2-3 个可能的根因
4. **验证假设**：用最小测试用例逐一验证
5. **定位根因**：确认真正的问题所在
6. **修复**：只修改必要的代码
7. **验证修复**：确认测试通过，无副作用

### 常见问题排查（按技术栈填写）

| 问题类型 | 排查方向 |
|---------|---------|
| 数据库字段不存在 | 检查 schema 变更是否已生成迁移并应用 |
| 认证失败 | 检查 Token/Cookie 是否正确传递 |
| 前后端数据不一致 | 核查接口响应格式与文档是否匹配 |
| 环境变量缺失 | 检查 .env.local 是否配置正确 |
| 依赖服务连接失败 | 确认服务是否启动、端口是否正确 |

---

## Skill 五：代码审查

### 审查维度

1. **正确性**：是否实现了 specs 定义的场景？
2. **完整性**：是否覆盖了所有边界条件？
3. **一致性**：是否符合项目编码规范？
4. **安全性**：是否有权限校验？数据是否验证？

### 对话触发方式
```
请审查这段代码，对照 [design.md路径] 检查是否符合设计规范
```

### 通用审查 Checklist

- [ ] 是否有对应的测试用例？
- [ ] 错误是否有统一处理？
- [ ] 是否有遗漏的异常场景？
- [ ] 是否符合项目包管理器规范（不混用）？
- [ ] 数据库操作是否通过正确的抽象层？
- [ ] 涉及权限的接口是否有鉴权？
- [ ] 外部调用是否有超时控制？

---

## Skill 六：验证闭环

### 不允许声称"完成"的场景
- 未运行测试
- 未检查类型错误（如有类型系统）
- 未对照 specs 验证场景覆盖

### 验证命令（按项目填写）

```bash
# 前端验证
pnpm typecheck    # 类型检查
pnpm test         # 单元测试
pnpm lint         # 代码规范

# 后端验证
mvn test          # 单元测试（Java）
# 或 go test ./...（Go）
# 或 pytest（Python）

# OpenSpec 验证
openspec verify [change-name]   # 三维度：完整性 × 正确性 × 一致性
```

---

## 完整工作流示例

以"添加用户头像功能"为例：

```bash
# Step 1: 需求探索（如需求清晰可跳过）
# 对话：请用 grill-me 模式探索"用户头像上传"需求

# Step 2: 规范制定
openspec propose add-user-avatar

# Step 3: 实现（TDD）
# 对话：请按 TDD 方式实现 tasks.md 中的任务

# Step 4: 数据库变更（如涉及）
# 按项目数据库迁移工具执行（Drizzle / Flyway 等）

# Step 5: 验证
openspec verify add-user-avatar
# 运行项目测试命令

# Step 6: 归档
openspec archive add-user-avatar
```

---

## 任务中断与恢复

```bash
# 查看当前变更状态
openspec list

# 继续上次未完成的任务
openspec continue [change-name]
```

AI 会读取 tasks.md 中的 checkbox 状态，自动从未完成的任务继续执行。任意步骤之间可以安全 `/clear`，状态在文件系统中，不在对话历史里。

---

## 在新项目中安装本 Skill

1. **复制本文件**到新项目的 `.claude/skills/` 目录
2. **填写配置区**：修改顶部"新项目配置区"中的技术栈信息
3. **安装 openspec**：`npm install -g @fission-ai/openspec@latest`
4. **初始化 openspec**：`openspec init`
5. **配置 CLAUDE.md**：在项目 CLAUDE.md 中注明采用 SDD 工作流，引用本 Skill 路径
6. **告知 AI 使用本 Skill**：在对话开始时说"请参考 `.claude/skills/sdd-workflow.md` 中的工作流"

---

## 参考资料

- [mattpocock/skills](https://github.com/mattpocock/skills) - 工程师技能库（含 grill-me、tdd、diagnosing-bugs 等）
- [Superpowers Plugin](https://github.com/obra/superpowers) - Claude Code 执行纪律插件
- OpenSpec 文档：`openspec --help`
