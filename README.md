# SDD 工作流与前端规范

这是一个与具体项目无关的规范包，提供：

- `skills/sdd-workflow.md`：面向 Claude Code、Codex 等 AI 编程工具的规范驱动开发（SDD）工作流；
- `conventions/frontend-conventions-react.md`：React / Next.js 前端规范；
- `conventions/frontend-conventions-vue.md`：Vue 3 / Vue Router / Pinia 前端规范；
- `conventions/frontend-conventions.md`：前端规范选择入口；
- `conventions/backend-conventions.md`：Spring Boot 后端规范模板，按项目实际情况选用。

工作流由 OpenSpec 记录“做什么”，由 AI 工具和其可用的 Superpowers 能力执行“怎么做”。工具不同，调用方式不同，但提案、实现、验证和归档的原则保持一致。

## 版本策略

规范不永久锁定 Vue、Vue Router、Pinia、React 或其他工具的具体版本。使用时遵循以下顺序：

1. 读取项目的 `package.json`、lockfile、workspace 配置和 peer dependency 约束；
2. 已有项目优先遵守现有依赖和运行时；
3. 新项目采用当前稳定、兼容、社区推荐的主版本；
4. 升级前核对框架、路由、状态管理、构建工具、TypeScript 和 UI 库的兼容性；
5. 需要可复现构建时提交 lockfile。只有项目明确要求时，才在项目文档中固定具体版本。

## 选择前端规范

先根据目标包的 `package.json` 判断技术栈，再只引用一份对应规范：

| 技术栈 | 规范 |
| --- | --- |
| React、Next.js（React）、React + Vite | [`conventions/frontend-conventions-react.md`](conventions/frontend-conventions-react.md) |
| Vue 3、Vue Router、Pinia、Nuxt（Vue）、Vue + Vite | [`conventions/frontend-conventions-vue.md`](conventions/frontend-conventions-vue.md) |

如果 monorepo 同时包含两种技术栈，按包或页面所在目录分别引用，不能混用 React 和 Vue 规范。

推荐在项目的 `AGENTS.md`、`CLAUDE.md` 或其他 AI 项目说明中加入：

```text
请先读取 docs/conventions/frontend-conventions.md。
根据目标包的 package.json 判断使用 React 还是 Vue，
然后只读取对应的 frontend-conventions-react.md 或 frontend-conventions-vue.md。
不要混用两份规范；版本以项目现有约束为准，否则采用当前稳定兼容版本。
```

## 快速安装

可以直接把仓库链接和下面这段话发给 Codex、Claude Code 或其他 AI 编程工具：

```text
请阅读 https://github.com/Mr-Jh-R/code 的 README，
把 SDD 工作流和适用的代码规范安装到当前项目。
先识别你是 Codex、Claude Code 还是其他工具，再选择对应的项目级 Skill 路径；
读取 package.json 判断前端是 React 还是 Vue，只引用适用的前端规范，不能混用；
保留项目现有依赖约束，新项目使用当前稳定兼容版本，不要把示例版本永久写死；
安装前列出将创建或修改的文件，安装后验证路径、Skill frontmatter 和本地 Markdown 链接。
```

### 1. 克隆仓库并安装 OpenSpec

以下命令均从目标项目根目录执行，将本仓库克隆到项目的相邻目录 `../sdd-skills`：

```bash
git clone https://github.com/Mr-Jh-R/code.git ../sdd-skills
npm install -g @fission-ai/openspec@latest
```

在目标项目根目录初始化 OpenSpec：

```bash
openspec init
openspec --help
```

需要非交互初始化时，根据当前工具二选一：`openspec init --tools codex` 或 `openspec init --tools claude`。同时使用多个工具时查看 `openspec init --help` 中的逗号分隔语法。

### 2. 手动安装

在目标项目根目录执行。先复制规范文件：

```bash
mkdir -p docs/conventions
cp ../sdd-skills/conventions/frontend-conventions.md docs/conventions/
cp ../sdd-skills/conventions/frontend-conventions-react.md docs/conventions/
cp ../sdd-skills/conventions/frontend-conventions-vue.md docs/conventions/
```

React 和 Vue 规范同时复制是为了保证选择入口中的本地链接完整；项目说明只能引用实际使用的一份。Spring Boot 项目可按需复制 `conventions/backend-conventions.md`，复制前先按项目包名、框架和安全策略适配。

再根据使用的 AI 工具选择一个项目级 Skill 路径：

```bash
# Codex
mkdir -p .agents/skills/sdd-workflow
cp ../sdd-skills/skills/sdd-workflow.md .agents/skills/sdd-workflow/SKILL.md

# Claude Code
mkdir -p .claude/skills/sdd-workflow
cp ../sdd-skills/skills/sdd-workflow.md .claude/skills/sdd-workflow/SKILL.md
```

只使用一个 AI 工具时，不需要创建另一个工具的目录。如果工具或项目仍使用旧的 Claude 单文件路径，也可以复制为 `.claude/skills/sdd-workflow.md`；同一个工具只保留一个实际生效的工作流副本，避免修改后不一致。

PowerShell 等价命令：

```powershell
$repo = "..\sdd-skills"
New-Item -ItemType Directory -Force docs\conventions | Out-Null
Copy-Item "$repo\conventions\frontend-conventions.md", "$repo\conventions\frontend-conventions-react.md", "$repo\conventions\frontend-conventions-vue.md" docs\conventions\

# Codex：只使用 Codex 时执行
New-Item -ItemType Directory -Force .agents\skills\sdd-workflow | Out-Null
Copy-Item "$repo\skills\sdd-workflow.md" ".agents\skills\sdd-workflow\SKILL.md"

# Claude Code：只使用 Claude Code 时执行
New-Item -ItemType Directory -Force .claude\skills\sdd-workflow | Out-Null
Copy-Item "$repo\skills\sdd-workflow.md" ".claude\skills\sdd-workflow\SKILL.md"
```

### 3. Claude Code

完成手动安装后，在 Claude Code 中安装 Superpowers（如果当前环境尚未安装）：

```text
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

将工作流复制到 `.claude/skills/sdd-workflow/SKILL.md` 后，Claude 会按项目级 Skill 读取。建议在 `CLAUDE.md` 中引用：

```markdown
## AI 开发工作流
- 工作流：`.claude/skills/sdd-workflow/SKILL.md`
- 前端入口：`docs/conventions/frontend-conventions.md`
- 后端规范（如已按需安装）：`docs/conventions/backend-conventions.md`
```

### 4. Codex

将工作流复制到 `.agents/skills/sdd-workflow/SKILL.md` 后，Codex 会按项目级 Skill 读取。也可以安装为当前用户的全局 Skill：

```bash
mkdir -p ~/.codex/skills/sdd-workflow
cp ../sdd-skills/skills/sdd-workflow.md ~/.codex/skills/sdd-workflow/SKILL.md
```

在项目的 `AGENTS.md` 中引用：

```markdown
## AI 开发工作流
- 工作流：`.agents/skills/sdd-workflow/SKILL.md`
- 前端入口：`docs/conventions/frontend-conventions.md`
- 后端规范（如已按需安装）：`docs/conventions/backend-conventions.md`
```

Codex 的 Superpowers 能力名称和安装方式取决于当前 Codex 环境。若环境已提供对应能力，可使用 `brainstorming`、`writing-plans`、`test-driven-development`、`systematic-debugging`、`verification-before-completion` 等能力；若未提供，仍应遵循本 Skill 中的同等步骤，并以项目命令完成验证。

## 工作流速查

完整流程：

```text
探索需求 → 创建隔离分支/工作区 → 创建 OpenSpec change → TDD 实现 → 验证 → archive
```

小型、边界清晰的修改可以跳过不必要的探索，但不能跳过对项目约束、测试和验证结果的检查。OpenSpec CLI 会演进，先用 `openspec --help` 确认当前语法。当前 CLI 的常用命令：

```bash
openspec new change <change-name>
openspec status --change <change-name>
openspec instructions <artifact> --change <change-name>
openspec instructions apply --change <change-name>
openspec validate <change-name> --strict
openspec archive <change-name>
```

`openspec validate` 只验证 change/spec 产物的结构和规则，不证明代码实现符合设计。实现一致性仍需由当前 AI 环境的 OpenSpec verify 能力或人工逐项对照 specs，并同时运行项目测试、类型检查、lint 和构建。

AI 工具的触发示例：

```text
我想实现 [功能]，请先按 SDD 工作流探索需求并给出方案。
请开始实现 [change-name]，先读取 proposal、design 和 tasks。
请按 TDD 实现 tasks.md，并在每个任务完成后更新勾选状态。
遇到这个 bug：[描述]，请先系统化定位根因，再提出修复。
请在声称完成前运行项目的测试、类型检查、lint、构建和 OpenSpec 实现一致性检查。
```

## 完成标准

声称完成前，必须根据项目实际脚本运行适用的格式化、lint、类型检查、测试和构建命令，并验证 OpenSpec 产物：

```bash
openspec validate <change-name> --strict
```

然后使用当前 AI 环境提供的 OpenSpec verify 能力或人工逐项核对实现与 specs。没有运行验证命令、没有检查实现一致性，或存在未解释的失败时，不应声称实现已完成。

## 目录结构

```text
.
├── skills/
│   └── sdd-workflow.md
├── conventions/
│   ├── frontend-conventions.md
│   ├── frontend-conventions-react.md
│   ├── frontend-conventions-vue.md
│   └── backend-conventions.md
└── README.md
```
