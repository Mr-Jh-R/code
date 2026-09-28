# Changelog

本文件记录规范行为和安装结构的变化。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本遵循 [Semantic Versioning](https://semver.org/)。

## [2.2.0] - 2026-09-28

### Changed

- SDD 未指定模式时默认采用简单模式；用户或项目明确选择标准模式时仍按标准流程执行。

### Compatibility and upgrade

- 这是兼容的 minor 版本：未改变 SDD 产物、必要测试或验证要求；只将未指定模式时的默认执行策略从标准模式改为简单模式。
- 需要完整探索、TDD、审查或可选增强能力的项目，可在项目约定中填写 `standard`，用户本次明确的 `sdd standard` 仍优先。
- 已安装 v2.1.0 的项目更新 `SKILL.md`、项目工作流模板和入口指针后即可采用新默认；不自动修改已有业务代码、分支或工具全局设置。

## [2.1.0] - 2026-09-23

### Added

- 增加按用途、归属和生命周期选择目录的通用项目文件规范。
- 增加通用 AI 项目资产、外部资料和生成物的归类规则。
- 为 SDD Skill 增加标准模式与简单模式，并明确 Superpowers、subagent 等增强能力是可选执行策略。
- 增加通用目录布局与 AI 工作流的研究依据和一手资料索引。
- 增加通用 Git 协作规范，覆盖基线、未提交依赖、并行隔离、提交整合、发布和交付状态。
- 增加项目工作流约定模板，将集成分支、文档入口和发布方式留给使用方配置。
- 增加通用 `api-contract-docs` Skill、调用方文档模板和只读 OpenAPI 核对脚本及测试。

### Changed

- 重写 README，提供人类导航、版本边界、PowerShell/Bash 接入步骤和 AI 工具入口示例。
- SDD 从项目入口读取 Git、文件归类和 API 文档规则，并明确简单模式的开关与完成范围。
- 文件归类规范可独立复制，避免依赖使用方不存在的研究文件。

### Compatibility and upgrade

- 无破坏性变更，保留 v2 的前后端规范入口与 Skill 目录；新增 Git/目录规则、项目工作流模板和 API 文档 Skill 可按需采用。
- 从 v2.0.0 升级时按 README 选择新增文件，合并项目入口指针，保留项目已有分支、文档路径和验证命令；不自动迁移业务文件或修改工具全局设置。
- 已安装 SDD 的项目更新完整 Skill 目录后可使用标准/简单模式；简单模式保留必要的测试与验证。
- 受影响入口：README、VERSION、后端项目画像模板、SDD Skill；新增入口为文件归类规范、Git 规范、项目工作流模板及 API 文档 Skill。

## [2.0.0] - 2026-09-02

### Added

- 增加跨语言、框架和数据库的后端工程核心规范。
- 增加设计模式、数据模式和分布式可靠性模式选型规范。
- 增加项目画像模板，用于选择技术附录、记录命令、边界和例外。
- 增加 Java、Spring Boot、MySQL、PostgreSQL 和 AI/LLM 附录。
- 增加版本策略、v1 到 v2 迁移说明、Apache-2.0 许可证和仓库验证脚本。

### Changed

- 将 SDD 工作流改为通过项目入口发现规范，不再硬编码 Spring、React 或 Vue 路径。
- 将 SDD Skill 改为标准 `skills/sdd-workflow/SKILL.md` 目录结构。
- 将后端旧路径改为规范选择入口，按项目画像渐进加载附录。
- 明确 HTTP 状态与业务错误码承担不同语义，错误不再统一返回 HTTP 200。
- 将 Spring Boot、MyBatis-Plus、MySQL 等实现偏好从通用核心移出。

### Deprecated

- v1 Spring Boot + MyBatis-Plus 模板仅保存在 `conventions/backend/legacy/` 供追溯。

## [1.0.0] - 2026-08-28

### Added

- 提供 SDD 工作流、React/Vue 前端规范和 Spring Boot 后端模板。
