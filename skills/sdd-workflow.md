---
name: sdd-workflow
description: Use when starting new features, substantial bug fixes, API or database schema changes, cross-module work, or when the user asks to follow SDD, OpenSpec, or the project development workflow in Codex, Claude Code, or another AI coding tool.
---

# SDD 工作流

本 Skill 定义与 AI 工具无关的开发流程。OpenSpec 保存“做什么”和进度；当前 AI 工具负责探索、计划、实现、调试、审查和验证。Claude Code 与 Codex 的调用名称可以不同，但产出物和完成标准相同。

## 开始前

1. 读取项目级说明，例如 `AGENTS.md`、`CLAUDE.md`、README 和目标目录附近的约束文件。
2. 检查 `openspec/`、现有 change、当前分支、工作区状态和项目验证命令。
3. 识别技术栈和包管理器，不擅自替换项目已有工具。
4. 需要前端规范时，先读取 `docs/conventions/frontend-conventions.md`：
   - React、Next.js（React）、React + Vite 只读取 `frontend-conventions-react.md`；
   - Vue 3、Vue Router、Pinia、Nuxt（Vue）、Vue + Vite 只读取 `frontend-conventions-vue.md`；
   - monorepo 按目标包分别选择，不能混用两份规范。
5. 版本以项目 `package.json`、lockfile、workspace 和 peer dependency 约束为准。新项目使用当前稳定、兼容、推荐版本，不把本 Skill 中的示例版本当作永久要求。

## 能力映射

优先使用当前环境已经提供的能力；不存在完全同名能力时，执行相同的步骤，不要虚构命令。

| 目标 | Claude Code 常见能力 | Codex 常见能力 | 无插件时 |
| --- | --- | --- | --- |
| 探索需求 | Superpowers brainstorming | `brainstorming` / 对话探索 | 阅读代码后逐项澄清 |
| 制定变更 | OpenSpec 命令或 Skill | `openspec-propose` / OpenSpec CLI | 创建 proposal、design、specs、tasks |
| 实现 | Superpowers TDD / executing plans | `openspec-apply-change`、`test-driven-development` | 按 tasks 逐项 TDD |
| 调试 | systematic debugging | `systematic-debugging` | 复现、假设、实验、根因、修复 |
| 验证 | verification before completion | `openspec-verify-change`、`verification-before-completion` | 运行项目验证命令并核对 specs |
| 归档 | OpenSpec archive | `openspec-archive-change` | `openspec archive <change-name>` |

能力名称只是提示。实际执行前必须先确认当前环境是否存在该 Skill、插件或命令。

## 选择流程

根据修改范围选择足够但不过度的流程：

- 新功能、跨模块修改、API/数据库变更：完整执行探索、提案、实现、验证、归档。
- 边界清晰的中型修改：可简化探索，但必须有 OpenSpec change、tasks 和验证。
- 小型格式、文案或局部低风险修复：可不创建 OpenSpec change，但仍须读取项目约束并运行适用验证。
- 难以稳定复现的 bug：先系统化调试；未定位根因前不进入大范围修改。

不要为了完成流程而制造无价值文档，也不要以“小改动”为理由跳过必要验证。

## 阶段一：探索

适用于需求存在歧义、边界不清或有多个合理方案的情况。

1. 阅读相关代码、历史变更和现有 specs。
2. 明确目标、用户场景、范围外内容、异常路径和兼容性要求。
3. 对关键设计给出可比较的方案和取舍。
4. 记录已确认决策及被否决方案，避免后续重复讨论。
5. 未获得必要决策时，不假设会显著改变行为或范围的答案。

产出可以写入 proposal/design，也可以先形成简短探索文档；最终必须进入 OpenSpec change。

## 阶段二：创建或继续 OpenSpec Change

先检查现有 change：

```bash
openspec list
```

如果已有同一目标的 change，继续它，不要创建重复 change。新建 change 时优先使用环境提供的 OpenSpec Skill。CLI 会演进，先运行 `openspec --help`；当前 CLI 可使用：

```bash
openspec new change <change-name>
openspec status --change <change-name>
openspec instructions <artifact> --change <change-name>
```

至少维护以下产出：

- `proposal.md`：背景、目标、非目标和影响范围；
- `design.md`：技术方案、关键决策、替代方案、迁移和风险；
- `specs/`：可验证的行为场景；
- `tasks.md`：按依赖顺序拆分且带验收条件的任务。

开始实现前检查：

- 每项需求都有对应场景；
- API、数据模型、权限、错误处理和兼容性已明确；
- tasks 覆盖实现、测试、文档、迁移和验证；
- 计划没有写死与项目无关的依赖版本。

## 阶段三：隔离工作区

遵循仓库现有分支与 worktree 规则。工作区有用户未提交修改时必须保留，不得重置或覆盖。

大型或并行变更优先使用独立分支/worktree；很小的修改可在当前分支完成，但仍需检查工作区状态。分支名尽量与 OpenSpec change name 对应。

## 阶段四：TDD 实现

按 `tasks.md` 的依赖顺序逐项执行：

1. 读取当前任务、design 和对应 specs。
2. 先新增或调整测试，确认测试因缺少目标行为而失败。
3. 编写使测试通过的最小实现。
4. 在测试保持通过的前提下重构。
5. 运行当前模块的格式化、lint、类型检查和测试。
6. 只有任务及其验证完成后，才把 checkbox 改为 `[x]`。

测试至少覆盖正常路径、边界条件和关键错误路径。生成代码只通过生成器更新，不直接编辑会被覆盖的文件。

## 阶段五：系统化调试

遇到 bug 或意外失败时：

1. 建立稳定复现步骤，并记录期望与实际结果。
2. 收集错误日志、调用链、输入输出、环境差异和近期变更。
3. 提出少量可证伪的根因假设。
4. 用最小实验逐个验证，不同时修改多个不相关因素。
5. 确认根因后先补回归测试，再做最小修复。
6. 运行相关测试和更广范围的回归验证。

不得把隐藏错误、增加无界重试或扩大超时当作根因修复。

## 阶段六：审查与验证

先核对实现与 specs，再审查代码质量。重点检查：

- 所有 Scenario 是否实现，是否存在未说明的行为变化；
- 数据库/API 兼容性、权限、错误处理和迁移是否完整；
- 是否遵守目标技术栈规范，React/Vue 规范是否选对；
- 是否引入不必要依赖、重复实现或越界重构；
- tests 是否真正覆盖新行为和回归风险。

运行仓库实际提供的命令。下面只是常见示例，不是固定命令：

```bash
pnpm format:check
pnpm lint
pnpm typecheck
pnpm test
pnpm build
mvn test
openspec validate <change-name> --strict
```

`openspec validate` 只验证 change/spec 产物，不证明实现符合设计。还必须使用当前环境提供的 `openspec-verify-change` 等实现验证能力，或人工逐项核对实现、tasks 和所有 Scenario。

声称“完成”“修复”或“测试通过”前，必须报告刚刚执行的命令和结果。无法运行的检查要明确说明原因和剩余风险。

## 阶段七：归档

满足以下条件后才能归档：

- tasks 全部完成；
- specs 与实现一致；
- 必要测试、lint、类型检查和构建通过；
- 数据迁移、文档和兼容性说明已完成；
- 没有未解释的验证失败。

优先使用环境提供的归档能力，否则按项目支持的 CLI 执行：

```bash
openspec archive <change-name>
```

归档后检查主 specs 是否已同步，以及 git diff 是否只包含预期文件。

## 中断恢复

恢复工作时不要依赖旧对话记忆：

1. 读取项目说明和本 Skill；
2. 查看 `openspec list`、change 的 proposal/design/specs/tasks；
3. 查看当前分支、`git status` 和最近提交；
4. 从第一个未完成 task 继续，并重新运行与该任务相关的验证。

## 完成输出

最终结果应简洁包含：

- 完成了哪些行为变化；
- 主要修改文件或模块；
- 实际运行的验证命令及结果；
- 尚未完成或无法验证的事项；
- 如已提交或推送，提供分支和提交信息。
