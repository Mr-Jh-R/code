# Changelog

本文件记录规范行为和安装结构的变化。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本遵循 [Semantic Versioning](https://semver.org/)。

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
