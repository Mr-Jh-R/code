# 通用仓库布局与 AI 辅助开发工作流研究

> 研究日期：2026-09-21
> 目的：为本仓库将具体项目布局说明抽象为通用规范提供依据。本文只记录研究结论，不把某一种技术栈的目录当成所有项目的必选目录。

## 结论摘要

1. 主流工具的共同点是“按职责和工具约定放置文件”，而不是要求每个项目都创建一棵完整目录树。缺少可选目录是正常状态；当文件出现时，应按其职责放到约定位置。
2. 通用布局应把根目录作为项目入口和元数据区，把源码、测试、文档、脚本、构建产物、部署配置、AI 工作流产物分开，并明确“必选、按需、禁止提交”的边界。
3. Maven/Gradle 的 `src/main`、`src/test`，npm 的 `package.json`，以及 Python Packaging Guide 对 `src/` 布局的说明，都是技术栈约定，应作为可选附录而不是通用规范的硬编码。
4. OpenSpec 是规格驱动工作流；其当前 OPSX 设计强调可迭代的动作（探索、提案、应用、更新、同步、归档），不是必须一次走完的线性阶段。GitHub Spec Kit 也把 SDD、Bug fixing、Idea assessment 作为独立入口。
5. “surpown”不是已识别的标准术语。证据最接近两种候选：`subagent`（子代理机制）或 `Superpowers`（obra/superpowers 项目的方法论，含 subagent-driven-development）。不能仅凭拼写确定用户指的是哪一个。

## 通用仓库布局应抽象什么

### 根目录职责

根目录只放项目级入口、元数据和少量跨工具配置，例如：

- `README.md`：项目用途、快速开始和导航；
- `LICENSE`、`NOTICE`：许可证和法律声明（适用时）；
- `CONTRIBUTING.md`、`CODE_OF_CONDUCT.md`、`SECURITY.md`：协作、安全和行为约定（适用时）；
- 构建/依赖入口（例如 `pom.xml`、`build.gradle`、`package.json`、`pyproject.toml`）；
- 顶层工具配置（例如 `.gitignore`、格式化/静态检查配置）；
- `.github/`：Issue/PR 模板、工作流和代码所有者配置（使用 GitHub 时）。

根目录不应成为任意临时文档、日志、导出文件和构建产物的堆放区。它们应进入有语义的目录，或被 `.gitignore` 排除。

GitHub 官方将仓库描述为包含代码、文件和修订历史的协作单元，并支持把已有仓库作为模板，复用其目录、分支和文件结构：
<https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories>
<https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository>

### 推荐的职责分区（按需创建）

下面是通用语义，不代表每个项目必须拥有所有目录：

| 目录/位置 | 放置内容 | 备注 |
| --- | --- | --- |
| `src/` 或技术栈约定的源码目录 | 可发布的生产源码 | 单体项目通常一个源码根；多模块项目可在模块内重复该约定 |
| `tests/`、`test/` 或技术栈约定的测试目录 | 单元、集成、端到端测试 | 测试目录应能按源码/模块追溯 |
| `docs/` | 用户文档、API、架构、决策记录、研究笔记 | 研究记录可放 `docs/research/`；不要把临时计划混入稳定文档 |
| `scripts/` 或 `tools/` | 可复用的开发、检查、迁移、发布脚本 | 按用途分组并写明入口与副作用 |
| `config/`、`deploy/`、`infra/` | 部署、基础设施和环境模板 | 机密值放密钥系统，不提交到仓库 |
| `.github/` 或其他托管平台目录 | CI、模板、CODEOWNERS 等托管平台配置 | 与应用源码分开 |
| `.agents/skills/`、`.claude/skills/` 等 | AI 工具可发现的项目级技能/指令 | 采用工具官方约定；具体路径见工具附录 |
| `openspec/` | OpenSpec 规格、变更和归档（启用 OpenSpec 时） | 不启用时无需创建 |
| `build/`、`dist/`、`target/`、`node_modules/`、缓存目录 | 生成物或依赖缓存 | 通常由构建生成并加入 `.gitignore`，除非项目明确发布它们 |

规范应同时给出“按文件意图选择路径”的决策表。例如：API 文档进入 `docs/api/`，架构决策进入 `docs/architecture/` 或 `docs/adr/`，可执行检查进入 `scripts/validate/`，而不是要求这些目录预先存在。

### 技术栈官方约定（附录）

- **Maven**：Apache Maven 的标准布局使用 `src/main/java`、`src/main/resources`、`src/test/java`、`src/test/resources`，构建输出在 `target/`。来源：<https://maven.apache.org/guides/introduction/introduction-to-the-standard-directory-layout.html>
- **Gradle Java Plugin**：Gradle Java 插件默认采用 `src/main/java`、`src/main/resources` 和 `src/test/java` 等目录，并允许按需配置。来源：<https://docs.gradle.org/current/userguide/java_plugin.html>
- **Python**：Python Packaging User Guide 比较 flat layout 与 `src` layout；`src` layout 可避免从项目根目录运行时误把未安装的源码导入，适合需要验证打包/安装行为的项目。来源：<https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/>
- **Node/npm**：npm 的项目元数据、脚本、依赖和发布行为由 `package.json` 定义；npm 文档没有要求所有 Node 项目采用唯一的源码目录，应用的 `src/`、测试和构建目录应由项目约定决定。来源：<https://docs.npmjs.com/cli/v11/configuring-npm/package-json>

因此，通用规范应写“采用对应生态的默认布局，必要时在项目级规范中覆盖”，而不是把 Java、Node、Python 的细节混为一棵强制目录树。

## AI 辅助开发与规格驱动工作流

### OpenSpec（Fission-AI）

OpenSpec 官方 README 将其定位为轻量的规格层：在写代码前对齐需求，按变更保存 proposal、specs、design、tasks，并通过 `/opsx:propose`、`/opsx:apply`、`/opsx:archive` 完成一个典型闭环：<https://github.com/Fission-AI/OpenSpec>。

当前 OPSX 文档明确说它是“fluid, iterative workflow”，把 `create/implement/update/archive` 当作可随时执行的动作；依赖关系用于说明下一步可做什么，不构成僵化阶段门。默认核心动作是 `propose`、`explore`、`apply`、`update`、`sync`、`archive`，扩展配置后还可使用 `new`、`continue`、`ff`、`verify`、`bulk-archive`、`onboard`：<https://github.com/Fission-AI/OpenSpec/blob/main/docs/opsx.md>。

对本仓库的启示：应定义“需求澄清/规格、设计、任务、实现、验证、归档”的产物和存放位置，同时允许实现中回写规格；不要把“目录存在”当作使用前提，也不要把完整流程强制到每个小改动。

### GitHub Spec Kit

GitHub Spec Kit 的官方 README 明确列出三个独立入口：

- Spec-Driven Development：规格贯穿规划、实现和收敛；
- Bug fixing：评估原因、限定修复范围并记录验证；
- Idea assessment：以证据作出投入、澄清或停止的决定。

它特别说明这三个流程不是必须依次执行的阶段，SDD 在核心包中，另外两个是按需安装的扩展：<https://github.com/github/spec-kit>。

这支持在通用规范中提供“标准 SDD”“缺陷诊断”“方案评估”三种入口，而不是所有任务都先生成完整规格包。

### Skills 与 subagents：工具机制，不等同于产品流程

OpenAI Codex 官方文档说明，skill 是包含指令、资源和可选脚本的可复用工作流；`SKILL.md` 是入口文件，Codex 会按仓库、用户、管理员等作用域发现它们。仓库级技能通常放在 `.agents/skills/`：<https://developers.openai.com/codex/skills>。

OpenAI 的 subagents 文档说明，ChatGPT Work 和 Codex 可以并行启动专门代理并收集结果，适合代码库探索或可拆分的多步骤计划；这是一种并行执行能力，不是 SDD 必经步骤：<https://developers.openai.com/codex/subagents>。

Claude Code 官方文档也把 subagent 定义为有独立上下文、系统提示和工具权限的专门助手，可把搜索、日志等不需要占用主上下文的工作隔离出去；其 skills 采用带 YAML frontmatter 的 `SKILL.md`，用于复用工作流和领域知识：
<https://code.claude.com/docs/en/sub-agents>
<https://code.claude.com/docs/en/skills>

因此，仓库规范应把“项目级 AI 指令/技能”和“是否并行委派”分开：前者是可检查的文件归属，后者是执行策略，应按任务复杂度、风险和成本选择。

### Superpowers（候选解释）

`obra/superpowers` 是社区项目，不是 OpenSpec 或 Codex 的内置流程。其 README 将自身描述为建立在 composable skills 上的完整开发方法论，基本流程包括 brainstorming、worktree、writing-plans、TDD、code review、finishing branch，并提供 `subagent-driven-development` 与 `executing-plans` 两种实现路径：<https://github.com/obra/superpowers>。

该项目明确会为每个工程任务派发新的 subagent 并在任务后复查，或在当前会话内实现后做一次总复查；这会增加上下文切换、模型调用和等待时间。它与“用户发现某流程耗时很高”的描述相符，但不能证明“surpown”一定就是 Superpowers。

## 对“surpown”的识别

截至本研究，没有在上述官方文档或仓库中找到 `surpown` 这个术语。基于拼写和上下文，候选解释按可信度排序如下：

1. **Superpowers**：拼写相近，且其核心流程确实含 `subagent-driven-development`、TDD 和多次审查，最可能导致额外耗时。
2. **subagent / subagents**：可能是把“子代理”听写成了类似的词；OpenAI 和 Claude 官方都使用该术语，指并行或隔离的专门代理机制。
3. 其他第三方插件或内部流程：目前没有足够一手证据确认名称。

在规范中应使用明确名称，例如“Superpowers（如启用）”“subagent 委派”，并把未知输入视为需要澄清的别名，不应凭猜测强制启用某个插件。

## 建议的标准/简单模式

这是面向本仓库的设计建议，属于待实现的政策，不是 OpenSpec 的现有配置字段：

### 标准 SDD 模式

1. 读取项目规范和现状，澄清目标与边界；
2. 创建或更新变更目录中的 proposal/specs/design/tasks（启用 OpenSpec 时使用其目录和命令）；
3. 按任务实现，运行与风险匹配的测试和验证；
4. 更新规格/文档，完成审查后归档。

复杂、跨模块或高风险任务可选用 subagent 并行探索、独立审查或 Superpowers 类工作流。它们是增强手段，不是默认强制步骤。

### 简单 SDD 模式

当用户明确说“使用 SDD 简单模式”或关闭增强委派时：

- 只保留目标、验收标准、最小设计、任务清单和必要验证；
- 由主代理串行完成，默认不启动 subagent，不启用 Superpowers 的 subagent-driven-development；
- 不生成与任务规模不匹配的完整长文档；
- 仍保留必要的测试、风险说明和可追溯记录。

当用户明确开启增强模式，或任务被判定为跨模块/高风险时，再允许并行探索、独立代码审查和更细的 TDD/工作树步骤。模式开关应作为本仓库自己的策略约定实现，不能假装是 OpenSpec、Codex 或 Claude Code 已内置的同名配置项。
