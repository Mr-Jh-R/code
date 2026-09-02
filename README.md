# SDD 工作流与代码规范包

这个仓库提供可复制、可固定版本的 AI 开发工作流和代码规范：

- [`skills/sdd-workflow/SKILL.md`](skills/sdd-workflow/SKILL.md)：与具体 AI 工具和技术栈解耦的 SDD/OpenSpec 工作流。
- [`conventions/backend-conventions.md`](conventions/backend-conventions.md)：后端规范选择入口。
- [`conventions/backend/core.md`](conventions/backend/core.md)：跨语言、框架和数据库的后端工程基线。
- [`conventions/backend/design-patterns.md`](conventions/backend/design-patterns.md)：设计模式、数据模式和分布式可靠性模式选型。
- [`conventions/backend/project-profile.template.md`](conventions/backend/project-profile.template.md)：项目画像模板。
- `conventions/backend/{languages,frameworks,databases,extensions}/`：按需加载的技术附录。
- [`conventions/frontend-conventions.md`](conventions/frontend-conventions.md)：前端规范选择入口。

OpenSpec 保存“做什么、为什么和进度”；Codex、Claude Code 或其他 AI 工具执行探索、实现、调试、审查与验证。工具能力名称可以不同，产出和完成标准保持一致。

## 后端规范结构

```text
backend-conventions.md              选择入口
backend/
├── core.md                         所有后端项目必读
├── design-patterns.md              设计/重构复杂模块时读取
├── project-profile.template.md     复制后填写项目事实
├── languages/java.md               Java 项目按需读取
├── frameworks/spring-boot.md       Spring Boot 项目按需读取
├── databases/mysql.md              MySQL 项目按需读取
├── databases/postgresql.md         PostgreSQL 项目按需读取
├── extensions/ai-llm.md            AI/LLM 项目按需读取
└── legacy/spring-mybatis-plus-v1.md
```

通用核心只保存跨项目稳定的安全、协议、事务、并发、数据和运维规则。框架、语言和数据库特有行为留在附录，项目通过画像选择，不加载无关上下文。

## 版本策略

生产项目必须固定 release tag，不直接复制不断变化的 `main`：

```bash
git clone --branch v2.0.0 --depth 1 https://github.com/Mr-Jh-R/code.git ../code-standards
```

版本遵循 [Semantic Versioning](https://semver.org/)：

- major：规则行为、目录、安装或兼容策略发生破坏性变化；
- minor：增加向后兼容的规则、附录或检查；
- patch：修正措辞、示例、链接和不改变要求的缺陷。

详细规则见 [`VERSIONING.md`](VERSIONING.md)，版本变化见 [`CHANGELOG.md`](CHANGELOG.md)。

## 安装后端规范

在目标项目根目录执行。以下示例将整个后端规范包复制到项目中，再创建项目画像：

### PowerShell

```powershell
$standardsRepo = "..\code-standards"
New-Item -ItemType Directory -Force "docs\conventions" | Out-Null
Copy-Item "$standardsRepo\conventions\backend-conventions.md" "docs\conventions\"
Copy-Item "$standardsRepo\conventions\backend" "docs\conventions\" -Recurse
Copy-Item "docs\conventions\backend\project-profile.template.md" "docs\conventions\backend-project-profile.md"
```

### Bash

```bash
standards_repo=../code-standards
mkdir -p docs/conventions
cp "$standards_repo/conventions/backend-conventions.md" docs/conventions/
cp -R "$standards_repo/conventions/backend" docs/conventions/
cp docs/conventions/backend/project-profile.template.md docs/conventions/backend-project-profile.md
```

填写 `backend-project-profile.md`，删除未使用附录的选择项。复制整个目录是为了保持本地链接稳定；Agent 只读取画像选中的附录。

在 `AGENTS.md`、`CLAUDE.md` 或等价项目入口中加入：

```text
修改、设计或审查后端代码，以及变更 API、数据库、并发、安全或外部集成前，
必须完整读取 docs/conventions/backend-conventions.md、
docs/conventions/backend/core.md 和 docs/conventions/backend-project-profile.md；
设计新抽象或重构复杂流程时再读取 design-patterns.md；
只读取项目画像 selected_appendices 中列出的技术附录。
```

## 安装 SDD Skill

复制完整 Skill 目录，不再把普通 Markdown 文件重命名为 `SKILL.md`：

### Codex

```powershell
New-Item -ItemType Directory -Force ".agents\skills" | Out-Null
Copy-Item "..\code-standards\skills\sdd-workflow" ".agents\skills\" -Recurse
```

```bash
mkdir -p .agents/skills
cp -R ../code-standards/skills/sdd-workflow .agents/skills/
```

### Claude Code

```powershell
New-Item -ItemType Directory -Force ".claude\skills" | Out-Null
Copy-Item "..\code-standards\skills\sdd-workflow" ".claude\skills\" -Recurse
```

```bash
mkdir -p .claude/skills
cp -R ../code-standards/skills/sdd-workflow .claude/skills/
```

在项目入口中声明真实路径：

```text
新功能、重大缺陷、API 或数据库变更、跨模块工作使用
.agents/skills/sdd-workflow/SKILL.md 中的 SDD 工作流。
```

Claude Code 项目将路径替换为 `.claude/skills/sdd-workflow/SKILL.md`。只安装实际使用工具的副本，避免两个副本独立演进。

如果项目尚未安装 OpenSpec，根据 [OpenSpec 官方仓库](https://github.com/Fission-AI/OpenSpec) 的当前说明安装，再从项目根目录初始化并检查实际命令：

```bash
npm install -g @fission-ai/openspec@latest
openspec init
openspec --help
```

不要把 README 中的 CLI 示例当作永久接口；执行前以当前 `openspec --help` 为准。

## 选择前端规范

先读取 [`conventions/frontend-conventions.md`](conventions/frontend-conventions.md)，根据目标包的构建文件只选择实际技术栈：

| 技术栈 | 规范 |
|---|---|
| React、Next.js（React）、React + Vite | [`conventions/frontend-conventions-react.md`](conventions/frontend-conventions-react.md) |
| Vue 3、Vue Router、Pinia、Nuxt（Vue）、Vue + Vite | [`conventions/frontend-conventions-vue.md`](conventions/frontend-conventions-vue.md) |

monorepo 按目标包分别选择，不把 React 和 Vue 规则同时应用于同一个包。

## 从 v1 迁移

v1 是绑定 Spring Boot、MyBatis-Plus 和 MySQL 的模板；v2 将通用基线与技术选型分开，并修正 HTTP 错误语义等规则。不要让同一项目同时启用 v1 和 v2。

存量项目可以继续固定 `v1.0.0`，然后通过单独的 SDD change 迁移。完整步骤见 [`MIGRATION-v1-to-v2.md`](MIGRATION-v1-to-v2.md)。

## 验证仓库

本仓库不依赖项目构建工具。提交前运行：

```bash
python scripts/validate_repository.py
```

验证器检查本地 Markdown 链接、代码围栏、尾随空白、版本文件和 Skill frontmatter。GitHub Actions 执行同一命令。

## 许可证

本仓库使用 [Apache License 2.0](LICENSE)。项目复制或修改规范和示例时保留适用的版权与许可证说明。
