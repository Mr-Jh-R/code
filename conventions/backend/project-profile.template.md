# 后端项目画像模板

> 将本文件复制到目标项目并填写。项目画像记录技术选择、权威命令和明确例外，不复制能从构建文件或目录直接查到的易过期信息。

## 采用信息

```yaml
standard:
  source: https://github.com/Mr-Jh-R/code
  version: v2.1.0
  core: docs/conventions/backend/core.md
  design_patterns: docs/conventions/backend/design-patterns.md

project:
  name: ""
  languages: []
  frameworks: []
  modules: []
  databases: []
  external_systems: []

selected_appendices:
  - ""                         # 只列项目实际使用的附录路径

commands:
  format: ""
  lint: ""
  build: ""
  test: ""
  integration_test: ""
  run_local: ""

contracts:
  api_spec: ""
  event_spec: ""
  migrations: ""
  public_endpoints: []
  authentication: ""

quality_gates:
  static_analysis: []
  dependency_scan: ""
  architecture_check: ""
  coverage_policy: ""

deployment:
  instance_model: ""          # 单实例、多实例、分区所有权等
  state_ownership: ""
  rollout: ""
  rollback: ""
```

## 模块边界

| 模块 | 业务职责 | 公开接口 | 数据所有权 | 禁止依赖 |
|---|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待填写 | 待填写 |

## 项目级约定

只记录不能从环境直接推导、且确实影响实现的约定：

- API 错误体和业务码格式：待填写。
- 时间、金额、ID 和枚举约定：待填写。
- 事务、消息和幂等策略：待填写。
- 认证、授权和内部接口策略：待填写。
- 敏感数据、日志和保留期策略：待填写。
- 数据库 schema、迁移和本地集成验证：待填写。

## 例外登记

| 规则 | 范围 | 原因 | 替代保障 | 责任人 | 复审/到期条件 |
|---|---|---|---|---|---|
| 待填写 | 待填写 | 待填写 | 待填写 | 待填写 | 待填写 |

“历史代码如此”不能单独作为例外原因。临时例外必须有到期或收敛条件；安全、协议和数据正确性例外必须包含风险与补偿控制。

## Agent 入口示例

在项目的 `AGENTS.md`、`CLAUDE.md` 或等价入口中使用真实路径：

```text
修改、设计或审查后端代码，以及变更 API、数据库、并发、安全或外部集成前，
必须完整读取 docs/conventions/backend-conventions.md、
docs/conventions/backend/core.md 和 docs/conventions/backend-project-profile.md；
设计新抽象或重构复杂流程时再读取 design-patterns.md；
只读取项目画像 selected_appendices 中列出的技术附录。
```

画像完成的标准：开发者或 Agent 能找到权威命令、契约、边界、附录和例外，不需要猜测技术栈或优先级。
