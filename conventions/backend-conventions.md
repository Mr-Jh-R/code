# 后端规范选择入口

本文件是后端规范包的稳定入口。它负责选择需要读取的规则，不承载具体技术栈实现。

## 读取顺序

修改、设计或审查后端代码时，按顺序执行：

1. 完整读取 [`backend/core.md`](backend/core.md)。这是所有后端项目共同遵守的工程基线。
2. 读取目标项目填写的项目画像。新项目从 [`backend/project-profile.template.md`](backend/project-profile.template.md) 创建项目自己的画像，不直接修改模板。
3. 设计新模块、引入抽象或重构复杂流程时，读取 [`backend/design-patterns.md`](backend/design-patterns.md)。
4. 只读取项目画像选中的技术附录：
   - Java：[`backend/languages/java.md`](backend/languages/java.md)
   - Spring Boot：[`backend/frameworks/spring-boot.md`](backend/frameworks/spring-boot.md)
   - MySQL：[`backend/databases/mysql.md`](backend/databases/mysql.md)
   - PostgreSQL：[`backend/databases/postgresql.md`](backend/databases/postgresql.md)
   - AI/LLM：[`backend/extensions/ai-llm.md`](backend/extensions/ai-llm.md)

项目未使用的技术附录不读取、不安装，也不引入对应依赖。

## 规则优先级

发生冲突时，按以下顺序裁决：

1. 法律、隐私、安全和组织级强制要求。
2. 已发布的外部协议、数据兼容承诺和明确的架构决策。
3. `core.md` 中标记为“必须”的安全、协议和正确性规则。
4. 项目画像选中的技术附录和项目级约定。
5. 通用风格建议。

项目不能用“历史代码如此”覆盖安全、协议或数据正确性要求。存量项目可以渐进迁移，但必须记录差异、风险、责任人和收敛条件。

## 推荐项目指针

在项目的 `AGENTS.md`、`CLAUDE.md` 或等价入口中写明真实路径：

```text
修改、设计或审查后端代码，以及变更 API、数据库、并发、安全或外部集成前，
必须完整读取并遵守 {后端规范入口路径} 和 {项目画像路径}；
只读取项目画像选中的技术附录。
```

SDD 工作流通过项目入口发现规范，不在 Skill 中硬编码某个框架或数据库路径。

## 旧版说明

v1 的 Spring Boot + MyBatis-Plus 模板保存在 [`backend/legacy/spring-mybatis-plus-v1.md`](backend/legacy/spring-mybatis-plus-v1.md)，仅用于存量项目追溯。新项目和已完成 v2 迁移的项目不得把它作为活动规范。
