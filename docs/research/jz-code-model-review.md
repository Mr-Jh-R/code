# jz_code 后端模型目录与公共请求类研究

> 研究日期：2026-09-30
> 研究对象：<https://github.com/Mr-Jh-R/jz_code>
> 核对提交：`4fb642a62e563ec506af42d582618bc32a795e31`（`main`，浅克隆）
> 目的：记录一个真实项目如何组织实体、请求 DTO、响应 VO 和公共请求/响应类，为通用 Java 项目规范提供参考。本文是研究记录，不把该项目的具体包名或命名当成所有项目的硬性要求。

## 1. 实际目录

后端源码位于 `backend/src/main/java/com/jz/jzbancked/`。模型相关目录如下：

```text
model/
├── dto/
│   ├── agent/
│   ├── ai/
│   ├── conversation/
│   ├── kb/
│   ├── llmmodel/
│   ├── llmprovider/
│   ├── user/
│   └── workflow/
├── entity/
├── enums/
└── vo/
    ├── conversation/
    ├── llmmodel/
    ├── llmprovider/
    └── user/
```

对应源码入口：

- `model/entity/`：`User`、`Agent`、`Conversation`、`KnowledgeBase`、`KbDocument`、`Message`、`Workflow`、`WorkflowExecution`、`LlmProvider`、`LlmModel` 等持久化实体。
- `model/enums/`：`UserRoleEnum`、`FileUploadBizEnum`、`LlmProviderTypeEnum`、`LlmModelTypeEnum`。
- `model/dto/`：按业务领域分子包；例如 `user/UserAddRequest`、`user/UserUpdateRequest`、`user/UserQueryRequest`，以及 `agent/AgentAddRequest`、`conversation/MessageSaveRequest`、`workflow/WorkflowExecuteRequest`。
- `model/vo/`：用于输出或脱敏的视图对象；部分领域使用子包（如 `vo/user/UserVO`），部分类型仍放在 `vo` 根目录（如 `vo/AgentVO`、`vo/KnowledgeBaseVO`）。

这个项目的 `dto` 比 `vo` 更一致地按业务领域分包；`entity` 和 `enums` 是平铺目录。目录按职责分层，同时在 DTO/VO 内按领域细分，是可复用的结构思想。具体子包名称与领域数量属于项目事实，不能直接写进通用规范。

## 2. 请求 DTO 的命名和继承

常见命名是“领域 + 操作 + `Request`”：

| 目的 | 实际示例 | 观察 |
| --- | --- | --- |
| 新增 | `UserAddRequest`、`AgentAddRequest`、`LlmModelAddRequest` | 新增请求通常不携带数据库生成字段 |
| 修改 | `UserUpdateRequest`、`AgentUpdateRequest`、`WorkflowUpdateRequest` | 通常包含 `id` 和允许修改的字段 |
| 查询/分页 | `UserQueryRequest`、`AgentQueryRequest`、`WorkflowQueryRequest` | 查询 DTO 继承公共 `PageRequest` |
| 登录/注册 | `UserLoginRequest`、`UserRegisterRequest`、`WxMpUserLoginRequest` | 按业务动作命名，不强行套 CRUD 名称 |
| 领域动作 | `ConversationRenameRequest`、`MessageVoteRequest`、`WorkflowExecuteRequest`、`MessageSaveRequest` | 动词体现业务意图 |
| AI 输入 | `AiChatRequest`、`AgentChatRequest`、`AiMessageDTO` | DTO 后缀与 Request 并存，表示内部消息模型和 HTTP 请求的不同语义 |

`UserQueryRequest`、`AgentQueryRequest`、`LlmModelQueryRequest`、`LlmProviderQueryRequest`、`WorkflowQueryRequest` 都扩展 `PageRequest`，通过继承复用分页和排序字段。该做法适合项目已经统一分页契约的场景；如果不同接口的分页/排序语义或安全策略不同，应改用组合或独立请求类型，避免把不必要字段暴露给所有查询。

项目没有把所有删除请求都命名为领域专属类：

- 按单个通用 `id` 删除时，控制器使用 `common/DeleteRequest`。
- 文档删除使用 `model/dto/kb/KbDocDeleteRequest`，字段为 `docId`，因为它是知识库文档领域动作，且请求字段不再是通用 `id`。

因此，“公共 `DeleteRequest` + 领域特定删除 DTO”是可兼容的组合。通用规范应按字段语义和安全边界决定是否复用，而不是强制所有删除都使用一个类。

## 3. 实体和 VO 的职责

`model/entity/User` 使用 MyBatis-Plus 的 `@TableName`、`@TableId`、`@TableLogic`，包含数据库字段和持久化行为所需的元数据；它不是面向前端的稳定输出契约。`model/vo/user/UserVO` 只保留允许展示的字段，不包含 `userPassword`、`isDelete` 等内部字段。`UserServiceImpl#getUserVO` 通过 `BeanUtils.copyProperties` 完成实体到 VO 的转换。

控制器同时存在两类接口：

- `getUserById` 返回 `BaseResponse<User>`（管理员接口）；
- `getUserVOById` 返回脱敏的 `BaseResponse<UserVO>`。

这说明项目已经有“实体用于内部/管理场景、VO 用于对外展示”的意图，但仍有实体直接出现在 API 返回值中的例外。通用规范建议默认禁止把持久化实体直接作为公共 API 响应；确需内部管理接口返回实体时，应记录范围和敏感字段审查。

VO 的放置尚未完全统一：`UserVO`、`LoginUserVO` 在 `vo/user/`，`AgentVO`、`WorkflowVO`、`KnowledgeBaseVO` 等有些在 `vo/` 根目录。可复用的目标是“按领域归档并保持同一领域的 DTO、VO 命名一致”，不是复制这种混合状态。

## 4. `common` 公共类

源码位置：`backend/src/main/java/com/jz/jzbancked/common/`。

### `DeleteRequest`

`DeleteRequest` 是一个实现 `Serializable` 的 Lombok `@Data` 类，只有 `Long id`。控制器在多个删除接口中接收它，然后传给 `removeById` 或服务层。它适合“请求只表达一个实体 ID”的简单接口；批量删除、复合主键、领域动作或需要资源归属校验时，应定义明确的请求类型。

### `PageRequest`

`PageRequest` 使用 `current = 1`、`pageSize = 10`、`sortField` 和默认 `sortOrder = "descend"`。各领域的 `*QueryRequest` 继承它，服务层再将字段转换为 MyBatis-Plus 分页和排序条件。排序字段会经过 `SqlUtils.validSortField` 检查，避免直接把任意字段拼入 SQL；通用规范应保留“允许排序字段白名单/映射”的安全要求，而不要固化这个项目的字段名或默认值。

### `BaseResponse<T>` 和 `ResultUtils`

`BaseResponse<T>` 是泛型响应包装，字段为 `int code`、`T data`、`String message`，并提供错误码构造器。`ResultUtils` 提供 `success` 和多个 `error` 工厂方法，控制器统一返回 `BaseResponse<具体类型>`。这是项目级 API 契约，不能假定所有项目都采用相同的 `code=0` 或消息文本；通用规范只应要求响应模型在项目内统一、泛型类型明确、错误码文档化。

## 5. 与事务、注入和方法入参相关的观察

这次核对到的提交中，后端源码没有 `@Transactional` 注解；持久化主要通过 MyBatis-Plus `ServiceImpl` 的 `save`、`updateById`、`removeById` 等调用完成。不能据此得出“所有方法都不需要事务”的结论。涉及多个写操作、跨资源一致性或需要回滚的应用服务，应在服务边界使用声明式事务；只有需要编程式控制传播、分段提交、重试或补偿等明确理由时再使用 `TransactionTemplate`/`PlatformTransactionManager`。事务类型应由一致性需求决定，而不是按项目口号统一为编程式。

该提交中未搜索到 `@Autowired`，依赖注入主要使用 `jakarta.annotation.Resource`（共 51 处匹配）。这是该项目既有风格，不代表 `@Autowired` 更好或更差。通用规范应优先构造器注入（可用 Lombok `@RequiredArgsConstructor` 或显式构造器），需要按名称选择 Bean 时使用 `@Qualifier`；字段注入（无论 `@Resource` 还是 `@Autowired`）应作为兼容旧代码的例外。

控制器和服务大多把 HTTP 请求映射到领域 DTO，例如 `addUser(UserAddRequest)`、`listUserVOByPage(UserQueryRequest)`、`createConversation(ConversationCreateRequest)`。但也存在 `long id`、`Long providerId`、`Map<String, Object>`、`MultipartFile`、`HttpServletRequest` 等直接入参，尤其是文件上传、基础设施上下文和简单资源定位场景。通用规则应要求复杂或稳定的请求契约使用 DTO，允许简单路径参数、文件、框架上下文作为独立参数，并避免用 `Map` 代替可文档化的 DTO，除非字段本身是动态结构。

## 6. 对通用项目规范的建议

从该项目可以抽象出以下可选约定：

1. 在技术栈允许时，将持久化实体、输入 DTO、输出 VO、枚举分开；目录缺失时按需创建。
2. DTO/VO 先按领域归档，再按动作命名；CRUD 只是常见动作，不能限制领域动作命名。
3. 查询 DTO 可以复用公共分页类型，但需检查继承是否引入过多字段；排序字段必须有白名单或安全映射。
4. 单 ID 删除可复用通用请求类；领域字段或批量/复合删除应使用专用请求类。
5. 默认不把实体作为公共 API 响应；输出 VO 应显式处理敏感字段、稳定性和版本兼容。
6. 事务、注入方式和 DTO 入参属于行为/实现规范，应写成“默认推荐 + 例外条件”，不要从一个项目的现状升级成强制单一方案。

## 7. 来源与核对方法

- GitHub 仓库：<https://github.com/Mr-Jh-R/jz_code>
- 本次核对的固定提交：<https://github.com/Mr-Jh-R/jz_code/tree/4fb642a62e563ec506af42d582618bc32a795e31>
- 目录入口：<https://github.com/Mr-Jh-R/jz_code/tree/4fb642a62e563ec506af42d582618bc32a795e31/backend/src/main/java/com/jz/jzbancked/model>
- 公共类目录：<https://github.com/Mr-Jh-R/jz_code/tree/4fb642a62e563ec506af42d582618bc32a795e31/backend/src/main/java/com/jz/jzbancked/common>
- 代表性源码：[`User.java`](https://github.com/Mr-Jh-R/jz_code/blob/4fb642a62e563ec506af42d582618bc32a795e31/backend/src/main/java/com/jz/jzbancked/model/entity/User.java)、[`UserAddRequest.java`](https://github.com/Mr-Jh-R/jz_code/blob/4fb642a62e563ec506af42d582618bc32a795e31/backend/src/main/java/com/jz/jzbancked/model/dto/user/UserAddRequest.java)、[`UserQueryRequest.java`](https://github.com/Mr-Jh-R/jz_code/blob/4fb642a62e563ec506af42d582618bc32a795e31/backend/src/main/java/com/jz/jzbancked/model/dto/user/UserQueryRequest.java)、[`UserVO.java`](https://github.com/Mr-Jh-R/jz_code/blob/4fb642a62e563ec506af42d582618bc32a795e31/backend/src/main/java/com/jz/jzbancked/model/vo/user/UserVO.java)、[`DeleteRequest.java`](https://github.com/Mr-Jh-R/jz_code/blob/4fb642a62e563ec506af42d582618bc32a795e31/backend/src/main/java/com/jz/jzbancked/common/DeleteRequest.java)、[`PageRequest.java`](https://github.com/Mr-Jh-R/jz_code/blob/4fb642a62e563ec506af42d582618bc32a795e31/backend/src/main/java/com/jz/jzbancked/common/PageRequest.java)、[`BaseResponse.java`](https://github.com/Mr-Jh-R/jz_code/blob/4fb642a62e563ec506af42d582618bc32a795e31/backend/src/main/java/com/jz/jzbancked/common/BaseResponse.java)。

核对方式：固定提交的浅克隆、`rg --files` 目录盘点、代表性 Java 源码阅读，以及对 `@Transactional`、`@Autowired`、`@Resource` 的只读搜索。

## 8. 官方规则核对：事务和依赖注入

本节补充 Alibaba P3C 与 Spring Framework 官方文档的核对结果，用来避免把单个项目的习惯误写成通用强制规则。

### Alibaba P3C 的事务相关规则

本次固定核对的 P3C 提交为 `6c59c8c36ecd8722c712d5685b8c3822c1c8b030`：

- [P3C ORM 映射规约](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/MySQL数据库/ORM映射.md)第 9 条写明：`@Transactional` 事务不要滥用；事务会影响数据库 QPS，使用事务时还要考虑缓存、搜索引擎、消息补偿和统计修正等回滚方案。该条标记为“参考”，不是“所有方法必须加事务”或“必须使用编程式事务”。
- [P3C 异常处理规约](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/异常日志/异常处理.md)第 5 条写明：事务代码中使用 `try` 并捕获异常后，如果需要回滚，必须注意手动回滚事务。
- P3C PMD 的 [TransactionMustHaveRollbackRule](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-pmd/src/main/resources/messages.xml) 会提示 `@Transactional` 应指定 `rollbackFor`，或者在方法中显式回滚。这是静态检查器的团队约束，不能简单解释为 Spring 的默认事务语义；引入时仍需根据项目异常类型和回滚边界决定 `rollbackFor`，并避免捕获异常后吞掉异常或丢失回滚信号。

因此，通用 Java/Spring 规范可以写成：事务放在有一致性边界的应用服务上；默认优先声明式 `@Transactional`；编程式事务用于少量操作、需要动态边界/传播/隔离/超时、显式事务命名或补偿流程等明确场景；捕获异常后要明确提交、回滚或重新抛出。不能从 P3C 规则推出“事务一个都必须使用编程式事务”。

### Spring 对声明式和编程式事务的建议

Spring 官方文档给出的选择依据更直接：

- [声明式事务管理](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative.html)说明大多数 Spring 用户选择声明式事务，因为它对业务代码影响最小。
- [编程式事务管理](https://docs.spring.io/spring-framework/reference/data-access/transaction/programmatic.html)说明编程式方式包括 `TransactionTemplate`/`TransactionalOperator` 或直接使用 `TransactionManager`；Spring 团队对命令式流程一般推荐 `TransactionTemplate`，对响应式流程推荐 `TransactionalOperator`。同时，`TransactionTemplate` 会让应用代码直接耦合 Spring 事务基础设施。
- [两者选择](https://docs.spring.io/spring-framework/reference/data-access/transaction/tx-decl-vs-prog.html)指出：编程式事务通常只适合少量事务操作，或者需要显式设置事务名称的场景；当事务操作较多时，声明式事务更合适，因为它能把事务管理从业务逻辑中移开。

这支持“按边界和控制需求选择”的通用规则。编程式事务的控制粒度更细，但每次都手写边界会增加基础设施耦合、异常处理和审查成本；细粒度本身不是对所有业务的充分理由。

### Spring 对构造器注入、`@Autowired` 和 `@Resource` 的说明

- [Spring 依赖注入](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)明确写道：必需依赖适合放在构造器，可选依赖可使用 setter 或配置方法；Spring 团队通常提倡构造器注入，因为它有利于不可变组件、保证必需依赖非空，并让对象以完全初始化状态交付。构造器参数过多则是职责过多的信号。
- [使用 `@Autowired`](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired.html)说明：如果类只有一个构造器，即使不标注 `@Autowired` 也会使用该构造器；多个候选构造器时才需要标注或配置选择。因此，`@Autowired` 不是构造器注入成立的必要条件。
- [使用 `@Resource`](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/resource.html)说明：`jakarta.annotation.Resource` 默认按名称解析，显式 `name` 按 Bean 名称注入；没有显式名称时使用字段名或 setter 属性名，并在特定情况下回退到主类型匹配。它适合项目需要 JSR-250/按名称选择 Bean 的场景。

P3C 没有要求“必须使用 `@Autowired` 而不能使用 `@Resource`”的通用条款。与依赖注入最接近的是 [单元测试规约](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/单元测试.md)第 4 条：为了让测试不依赖外部环境，应把 SUT 的依赖设计为可注入，并在测试时注入本地实现或 Mock。它约束的是可替换性和可测试性，不是某个注解名称。

所以，通用规则应推荐“构造器注入”，而不是把 `@Autowired` 或 `@Resource` 其中一个写成唯一正确答案。使用构造器时可以不加 `@Autowired`（单构造器），需要多个实现时用 `@Qualifier`、`@Primary` 或明确的 Bean 名称；旧代码中的字段注入可以逐步迁移，但不应为了统一注解而进行无行为收益的机械改写。

### 对当前 jz_code 观察的校准

jz_code 固定提交中没有 `@Transactional` 或 `@Autowired`，主要使用字段 `@Resource`。这只能说明该提交的现状：它没有覆盖事务边界的需求样例，也不能证明“事务全部编程式”或“`@Autowired` 更好”。若把这些结论写入项目规范，应改写为上述基于一致性、可测试性、Bean 选择和异常回滚语义的条件规则。
