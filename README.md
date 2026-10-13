# 通用项目规范与 AI 开发工作流

这个仓库提供可复制、可固定版本的项目规范和 Skill，供开发者、Codex、Claude Code 及其他 AI 编程工具使用。它规定文件如何归类、任务如何整合、接口文档如何核对，以及如何按风险开展规格驱动开发。

通用规范只定义流程和完成条件。具体分支名、技术栈、文档入口、运行命令和部署位置由使用方记录在项目约定中；目录按需要创建，缺少某个可选目录不代表项目不合规。

## 从这里开始

| 你要做什么 | 阅读入口 | 谁使用 |
| --- | --- | --- |
| 新建文件或选择输出目录 | [文件与目录规范](conventions/repository-layout.md) | 开发者和 AI |
| 开始任务、选择分支、整合或发布 | [Git 协作规范](conventions/git-workflow.md) | 开发者和 AI |
| 实现后的检查、修复复查与放行 | [通用质量门禁](conventions/quality-gates.md) | 开发者和 AI，按风险选择检查 |
| 给具体项目接入这些规则 | [项目工作流模板](conventions/project-workflow.template.md)和下方接入步骤 | 项目维护者和 AI |
| 开发功能或处理复杂变更 | [SDD Skill](skills/sdd-workflow/SKILL.md) | AI 执行，开发者核对产物 |
| 审查或编写 API 调用文档 | [API 文档 Skill](skills/api-contract-docs/SKILL.md) | 开发者可直接阅读，AI 可加载执行 |
| 专项代码规范检查 | [standards-check Skill](skills/standards-check/SKILL.md) | 按需调用，默认只读、单 Agent |
| 后端实现、设计与审查 | [后端入口](conventions/backend-conventions.md) | 按项目画像选择技术附录 |
| Mapper 映射、SQL 与 CRUD 复用 | [MyBatis / MyBatis-Plus 附录](conventions/backend/frameworks/mybatis-plus.md) | 仅采用该技术的项目选读 |
| 前端实现、设计与审查 | [前端入口](conventions/frontend-conventions.md) | 按目标包选择 React 或 Vue |

本仓库的 `conventions/` 是规范源文件，`skills/` 是可复制的完整技能包，`docs/research/` 保存研究依据，`scripts/` 与 `.github/workflows/` 负责自检。使用方无需照搬本仓库的发布方式或目录树。

## 快速接入一个项目

接入分四步：**选版本 → 复制需要的文件 → 填写项目事实 → 在工具入口引用**。已有同用途规范、Skill 或入口时，核对差异后合并，保留项目特有规则；不要直接覆盖。

### 1. 选择来源版本

采用已发布规范包时固定 release tag，当前已发布版本为 v2.4.0：

```bash
git clone --branch v2.4.0 --depth 1 https://github.com/Mr-Jh-R/code.git ../code-standards
```

v2.4.0 包含前后端规范、Git 规范、默认简单模式的 SDD 和 MyBatis/MyBatis-Plus 附录。**本页新增的质量门禁、standards-check Skill 和对应接入示例在 [Unreleased](CHANGELOG.md)，不包含在 v2.4.0 标签中。** 采用这些新增内容时使用包含它们的已审阅提交/工作副本，记录实际 SHA；后续发布后再固定包含它们的标签。下方完整安装命令会在来源缺少文件时停止，不能直接用于旧标签。

在项目约定中记录来源 URL 和实际 tag/SHA；采用未提交草稿时明确注明草稿状态。规则在目标项目保存为本地副本，日常开发不依赖网络或可变的远端 `main`。

### 2. 复制通用规范和所选 Skill

下面命令在**目标项目根目录**运行，仅用于首次安装。`code-standards` 指上一步选好的规范源目录。已安装项目按明确文件清单审查升级，不整目录覆盖。

#### PowerShell

```powershell
$standardsRepo = "..\code-standards"
$skillRoot = ".agents\skills"  # Claude Code 改为 .claude\skills
$ruleNames = @("repository-layout.md", "git-workflow.md", "quality-gates.md", "project-workflow.template.md")
$skillNames = @("sdd-workflow", "api-contract-docs")  # 删除不需要的 Skill
# 需要专项规范检查时，向 $skillNames 追加 "standards-check"

# 在写入前核对整个安装范围。
$copies = @(@{ Source = "$standardsRepo\LICENSE"; Target = "docs\conventions\standards-LICENSE" })
foreach ($name in $ruleNames) {
    $copies += @{ Source = "$standardsRepo\conventions\$name"; Target = "docs\conventions\$name" }
}
foreach ($name in $skillNames) {
    $copies += @{ Source = "$standardsRepo\skills\$name"; Target = "$skillRoot\$name" }
}
foreach ($entry in $copies) {
    if (!(Test-Path -LiteralPath $entry.Source)) { throw "来源版本缺少：$($entry.Source)" }
    if (Test-Path -LiteralPath $entry.Target) { throw "目标已存在，请审查合并：$($entry.Target)" }
}
foreach ($entry in $copies) {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $entry.Target) | Out-Null
    Copy-Item -LiteralPath $entry.Source -Destination $entry.Target -Recurse
}
```

#### Bash

```bash
(
set -eu
standards_repo=../code-standards
skill_root=.agents/skills  # Claude Code 改为 .claude/skills
rule_names=(repository-layout.md git-workflow.md quality-gates.md project-workflow.template.md)
skill_names=(sdd-workflow api-contract-docs)  # 删除不需要的 Skill
# 需要专项规范检查时，向 skill_names 追加 standards-check
sources=("$standards_repo/LICENSE")
targets=(docs/conventions/standards-LICENSE)
for name in "${rule_names[@]}"; do
  sources+=("$standards_repo/conventions/$name")
  targets+=("docs/conventions/$name")
done
for name in "${skill_names[@]}"; do
  sources+=("$standards_repo/skills/$name")
  targets+=("$skill_root/$name")
done
for i in "${!sources[@]}"; do
  [[ -e "${sources[$i]}" ]] || { printf '来源版本缺少：%s\n' "${sources[$i]}"; exit 1; }
  [[ ! -e "${targets[$i]}" ]] || { printf '目标已存在，请审查合并：%s\n' "${targets[$i]}"; exit 1; }
done
for i in "${!sources[@]}"; do
  mkdir -p "$(dirname "${targets[$i]}")"
  cp -R "${sources[$i]}" "${targets[$i]}"
done
)
```

保留 Skill 整个目录，包括 `references/`、`scripts/` 等资源；普通规范 Markdown 不需要改名为 `SKILL.md`。选择工具实际支持的项目技能目录；其他工具没有 Skill 发现机制时，在其项目入口引用这些文档并按步骤执行。

### 3. 填写项目事实并选择技术规范

把复制的模板另存为 `docs/conventions/project-workflow.md` 后填写，或将字段合入已有项目约定。至少明确集成基线、权威验证入口、采用来源，以及已安装的规范/Skill 路径。API 文档入口和发布约定仅在项目需要时填写。模板是可读文档，不是自动生效的工具配置。

在模板的“检查与证据”填写适用范围、实际命令及工作目录、必需项和 CI 入口；已有后端画像或 CI 配置直接引用即可。Git 规则与模板引用通用质量门禁，升级时一起复制 `quality-gates.md`，不需要新的配置文件或万能检查脚本。

技术规范按实际栈补充：

| 需要 | 从本仓库复制到目标 `docs/conventions/` | 如何选择 |
| --- | --- | --- |
| 后端 | `conventions/backend-conventions.md` 和整个 `conventions/backend/` | 从 `backend/project-profile.template.md` 创建项目自己的 `backend-project-profile.md`，选实际附录 |
| 前端 | `conventions/frontend-conventions.md` 和 React/Vue 两份规范 | 为保持相对链接完整一并复制；只读取目标包使用的那一份 |

安装完整关联文档是为了保持本地链接有效，不要求加载无关规则或安装对应技术依赖。后端画像与项目工作流约定互相引用已有命令或入口，不重复维护同一事实。无需后端或前端能力时不复制对应包。

使用 MyBatis/MyBatis-Plus 的项目，在后端画像的 `selected_appendices` 中加入 `docs/conventions/backend/frameworks/mybatis-plus.md`。该附录直接规定 Mapper 命名、资源位置、XML 结构和映射引用，人和 AI 均可编写，不需要特定 IDE 插件；普通 CRUD 可复用 `BaseMapper` 或 `IService/ServiceImpl`，复杂业务保留用例边界。XML 按实际需要创建；采用其他持久化技术的项目无需选择它。

### 4. 在 AI 工具入口加入指针

下例适用于已按上面路径安装两个 Skill 的 Codex 项目。**追加到已有 `AGENTS.md`，按实际安装情况删除未采用项**。项目已有入口优先使用，避免维护两份相同正文。

```text
开始或继续开发、选择工作区、整合、生成接口文档或发布前，
读取 docs/conventions/git-workflow.md 和 docs/conventions/project-workflow.md，
确认本任务的工作区、集成基线、未提交依赖和验证入口。

新建/移动文件或指定输出目录前，读取 docs/conventions/repository-layout.md。
新功能、复杂缺陷和 API/数据库/跨模块变更，使用
.agents/skills/sdd-workflow/SKILL.md；遵循用户选择的标准或简单模式。
审查、编写或更新接口文档，使用 .agents/skills/api-contract-docs/SKILL.md。

实现后按 docs/conventions/quality-gates.md 和项目检查命令单独核对差异，
按风险选择范围；修复后复查受影响项，已有有效结果可复用。

后端任务读取 docs/conventions/backend-conventions.md 和
docs/conventions/backend-project-profile.md，按画像选择附录。
前端任务读取 docs/conventions/frontend-conventions.md，按目标包选择 React/Vue。
```

Claude Code 使用 `.claude/skills/`：把指针中的路径替换为实际位置，在 `CLAUDE.md` 中声明，或通过 `CLAUDE.md` 引用共同维护的 `AGENTS.md`。同时使用多个工具时，声明同一份规范来源；若工具需要不同位置的技能副本，由同一版本同步更新。

仅在已安装可选 `standards-check` 时，再加入以下指针，并按工具替换路径：

```text
用户要求规范专项审查、发布前规范核对或项目明确要求时，使用
.agents/skills/standards-check/SKILL.md。默认只读；任务已授权修复时才修改。
普通 SDD 任务不强制调用此 Skill，不重复执行已有有效的同范围检查。
```

面向 AI 的接入请求示例：

```text
请把这个规范包接入当前项目。先读取它的 README，再核对目标项目现有
AGENTS/CLAUDE、技术栈、分支约定和已安装技能。复用已有权威入口，
只复制需要的规范和完整 Skill 目录，并填好项目工作流约定。
已有文件按差异合并；必要的项目事实无法确认时列出具体待确认项。
最后检查本地引用和技能资源，报告采用的版本、安装范围和验证结果。
```

接入完成的判断：入口指向存在的本地文件；选中的 Skill 资源完整；集成基线、文档归属和验证入口明确；已有项目约定已保留。复制文件不会自动修改工具的全局设置或启用插件。

## 日常工作怎么用

常见闭环是：**确认基线 → 明确需求与验收 → 实现和验证 → 按授权提交与整合 → 有发布任务时发布**。中途发现需求变化就更新规格；调试只在需要时进入。没有复杂变更时不必创建完整 OpenSpec 产物。

| 组成 | 职责 |
| --- | --- |
| Git 规范 | 任务从哪个版本开始，如何隔离、保存、整合和发布 |
| SDD Skill | 根据范围组织探索、规格、任务、实现、验证和归档 |
| OpenSpec | 管理 proposal、specs、design、tasks 及变更状态，不代替代码验证 |
| API 文档 Skill | 依据确认的契约版本维护调用文档，纯文档审查可独立使用 |
| 质量门禁 / standards-check | 通用检查闭环与可选专项审查，共用项目实际检查命令 |
| Superpowers / subagent | 可选的执行方式，不是 SDD 或 OpenSpec 的必需依赖 |

采用 OpenSpec 的项目按其 [官方安装说明](https://github.com/Fission-AI/OpenSpec) 安装、初始化，并通过当前 `openspec --help` 确认命令。只安装 Git/目录规则或只维护接口文档时不需要 OpenSpec。

### SDD 模式

未指定模式时默认使用简单 SDD。项目可以在工作流约定中选择 standard，但用户本次明确选择优先。

- `使用 SDD 简单模式` / `sdd simple`：主 Agent 串行完成，关闭可选 Superpowers 和子代理流程，精简探索和文档；保留适用的 OpenSpec 产物及必要测试、验证。
- `使用 SDD 标准模式` / `sdd standard`：按风险执行完整流程，增强工具是否使用仍遵循用户与项目偏好。
- `Superpowers off/on`：明确关闭或允许该工具；开启不代表自动安装，也不等于授权所有委派。

这些表达是本 Skill 识别的自然语言约定，不是 OpenSpec 或 Codex 的内置 CLI 开关。本次显式选择优先于项目默认；项目长期默认写在项目工作流约定中。

### API 文档

例如：“使用 api-contract-docs 核对当前集成开发版本的接口文档，只读检查”或“按指定提交更新现有接口手册”。Skill 会确认源码、契约与运行证据，必要时使用 [调用方模板](skills/api-contract-docs/references/frontend-api-template.md)。它不把文档任务扩大为接口实现或部署。

可选脚本支持本地 OpenAPI 3.x JSON 与 Markdown，只提供机械核对线索，不判断线上行为；用法和限制见 [Skill](skills/api-contract-docs/SKILL.md)。

### 规范检查：日常轻量，专项按需

日常流程是“读取适用规范 → 实现 → 自动检查 → 单独审查差异 → 必要修复与复查”。[质量门禁](conventions/quality-gates.md) 定义范围与完成条件：文档只做相关检查，普通代码检查受影响模块，权限/事务/数据库等变化增加专项证据。简单 SDD 也执行，默认主 Agent 串行完成，不强制全量构建、多代理或另写报告。

要做专项审查时选择安装 [standards-check](skills/standards-check/SKILL.md)，例如：

```text
使用 standards-check 检查本次改动，默认只读。
```

```text
使用 standards-check 核对我指定的发布提交；检查目标项目约定的必需项，
列出规则依据、文件位置、影响及未验证部分。
```

```text
使用 standards-check 检查并修复本任务范围内的确定违规，复查受影响部分。
```

检查工具不能机械执行所有 Markdown 规则：格式、类型、测试用现有工具；事务边界、授权与组件复用等结合代码证据审查。已有检查需能对应当前源码、配置、依赖和环境才可复用，修改后不能沿用已失效的“通过”。未配置、执行异常或未执行的必需项要报告为缺口。

手动命令与 CI 优先复用项目已有的构建/检查入口；没有 Skill 加载功能的工具也可直接阅读检查规范和 Skill 步骤执行。Git `pre-push` 或 AI hook 仅是可选触发适配，调用同一命令并反馈结果；采用前核对具体工具支持，避免每次编辑都跑重检查和递归触发。本包不自动安装任何 hook。

需要强制阻止不合格版本合并或发布时，使用方还要配置平台必需状态检查、分支保护及发布流水线前置条件。本地 hook 可被跳过，push 后 CI 失败也不会撤销已推送提交或标签；复制本包不等于已开启远端门禁。

## 维护、验证和升级

本仓库使用 Python 标准库自检，无需业务构建工具：

```bash
python scripts/validate_repository.py
python -B -m unittest discover -s skills/api-contract-docs/scripts -p "test_*.py"
git diff --check
```

第一条检查 Markdown 链接、围栏、空白、版本和 Skill frontmatter；第二条验证 API 核对脚本的路由匹配和报告行为。CI 运行同样的文档与脚本检查，机械通过不代替规范内容审查。

这组命令验证的是规范包自身，不能证明使用方的 Java、前端或其他业务代码合规。使用方应按项目工作流约定接入其实际工具和人工/AI 审查。

版本采用 [Semantic Versioning](https://semver.org/)。版本变化记录在 [CHANGELOG](CHANGELOG.md)，后续未发布改动另记为 Unreleased；发布流程见 [VERSIONING](VERSIONING.md)。使用方升级时审查差异、保留本地项目事实、同步入口并运行相关验证。

从旧 Spring Boot/MyBatis-Plus 模板迁移见 [v1 到 v2 迁移说明](MIGRATION-v1-to-v2.md)，同一项目只启用一个规范 major 版本。目录组织和 AI 工作流依据见 [研究记录](docs/research/repository-layout-and-ai-workflows.md)。

MyBatis XML 与通用 Service 的官方文档、版本实现和参考项目核对见 [研究记录](docs/research/mybatis-plus-mapping-service-guidance.md)；项目执行时以所选 [持久化附录](conventions/backend/frameworks/mybatis-plus.md) 为准。

本仓库使用 [Apache License 2.0](LICENSE)。复制规范、Skill 与脚本时保留适用的版权和许可证说明。
