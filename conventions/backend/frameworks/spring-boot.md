# Spring Boot 后端附录

> 仅在项目画像声明使用 Spring Boot 时读取。Java 项目同时读取 `../languages/java.md`。

## 一、结构与依赖注入

- 启动类位于根包，不使用 default package；业务包优先按能力组织。
- Spring Bean 使用构造器注入，依赖字段为 `final`；不使用字段注入。
- 单构造器通常不需要 `@Autowired`；多个实现使用 `@Qualifier`、`@Primary` 或明确 Bean 名称。`@Resource` 默认按名称解析，只在项目需要按名选择 Bean 时使用。
- 只有真实替换实现、跨模块端口或外部适配价值时定义接口，不机械创建 `Service` + `ServiceImpl`。
- 配置、适配器和持久化实现保持在模块内部，公开包只放稳定接口和共享契约。
- 可以使用 Spring Modulith 或 ArchUnit 验证模块无环、公开 API 和允许依赖。

## 二、Controller 与校验

- Controller 只适配 HTTP、读取可信身份、触发声明式校验并转换响应。
- 请求 DTO 使用 Jakarta Bean Validation；`@RequestBody` 配合 `@Valid` 或项目等价入口。
- 跨字段、持久化状态和权限校验由应用服务或领域策略完成。
- 稳定 API 使用明确 DTO，不以 `Map<String, Object>` 代替契约。
- 文件下载、流式响应和 WebSocket 使用框架原生响应，不包装普通 JSON。

## 三、异常与 HTTP 状态

- 使用 `@RestControllerAdvice` 建立统一错误边界，并返回真实 HTTP 状态。
- 业务错误定义同时持有稳定业务码、安全默认消息和 HTTP 状态，避免裸 `int code` 与状态脱节。
- 使用 `ResponseEntity`、`ProblemDetail`、`ResponseStatusException` 或项目统一映射明确状态。
- 分别处理参数校验、消息不可读、方法不支持、媒体类型、上传超限和业务冲突。
- 未知异常对外返回固定安全消息，在全局边界记录一次堆栈。
- OpenAPI 和 MockMvc/WebTestClient 契约测试同时断言 HTTP 状态和业务码。

参考错误定义：

```java
public enum ErrorCode {
    INVALID_ARGUMENT("INVALID_ARGUMENT", HttpStatus.BAD_REQUEST),
    UNAUTHENTICATED("UNAUTHENTICATED", HttpStatus.UNAUTHORIZED),
    PERMISSION_DENIED("PERMISSION_DENIED", HttpStatus.FORBIDDEN),
    NOT_FOUND("NOT_FOUND", HttpStatus.NOT_FOUND),
    CONFLICT("CONFLICT", HttpStatus.CONFLICT),
    INTERNAL_ERROR("INTERNAL_ERROR", HttpStatus.INTERNAL_SERVER_ERROR);

    private final String code;
    private final HttpStatus httpStatus;
}
```

业务码格式由项目画像决定；示例不要求项目必须使用字符串。

## 四、事务

- `@Transactional` 放在具体用例的公共入口，明确 readOnly、timeout 和需要的隔离/传播语义；不要给所有方法或整个类机械添加事务。
- 默认代理模式只拦截从代理外部进入的调用；同类自调用不会应用被调用方法上的事务配置。
- private 方法、异步方法和新线程不自动继承调用方事务。
- 默认只对 `RuntimeException` 和 `Error` 回滚；checked exception 需要明确 `rollbackFor` 或项目统一策略。
- 事务代码捕获异常后不得静默继续；需要回滚时重新抛出、标记回滚或使用明确的编程式边界。
- 事务中不执行耗时 HTTP、模型调用、文件解析、消息等待或 WebSocket 关闭。
- 默认优先声明式事务；只有动态边界、独立提交、特殊传播/隔离/超时、显式事务命名、补偿或分段处理时才使用 `TransactionTemplate`、`TransactionalOperator` 或事务管理器，并记录理由。
- 事务涉及缓存、搜索、消息或统计时，设计对应的 outbox、补偿、重试或修正路径，不能把数据库回滚当成跨系统回滚。
- 需要独立记录失败状态时，拆分 Bean、使用 `TransactionTemplate` 或明确的新事务边界。
- 乐观更新检查影响行数，并转换为冲突错误。

## 五、安全

- 使用 Spring Security 的统一配置建立默认拒绝规则，公开路径显式列入白名单。
- 方法级安全需要显式启用并测试，不能只靠自定义注解名称推断其生效。
- 对象级授权在业务查询或策略中执行，角色校验不能替代资源归属校验。
- 生产环境如果鉴权关闭、密钥为空或使用占位值，启动校验必须失败。
- CSRF 是否启用取决于认证载体和威胁模型，不能模板化关闭。
- Actuator、Swagger/OpenAPI UI、错误页和诊断端点按生产暴露策略独立保护。

## 六、配置

- 使用 `@ConfigurationProperties` 绑定一组配置，并配合 Jakarta Validation 在启动时校验。
- 配置项名称表达单位，或使用 `Duration`、`DataSize` 等类型。
- 业务代码不散落字符串形式的 `@Value`；配置默认值必须在各环境安全。
- secret 通过外部 secret source 提供，不进入配置仓库和日志。
- 多数据源分别配置连接池、事务管理器、迁移所有权和健康指标。

## 七、外部调用与任务

- HTTP Client 统一配置 connect、response、overall deadline、连接池、最大响应和观测拦截器。
- 重试、熔断和限流集中在适配器边界，避免 Controller、Service、Client 多层叠加。
- `@Async` 使用命名且有界的 Executor，并显式传播安全与追踪上下文。
- `@Scheduled` 任务幂等；多实例执行需要共享 lease/锁和 fencing token。
- Executor、Scheduler 和连接客户端由 Spring 生命周期管理，并配置有界关闭等待。

## 八、数据访问与测试

- JDBC、JPA、MyBatis 等持久化选择写入项目画像，只读取对应项目附录或约定。
- 动态 SQL 标识符来自服务端白名单，值始终参数化。
- `@SpringBootTest` 用于需要完整容器的集成行为，不替代快速单元和 slice 测试。
- Controller 测试覆盖校验、认证、授权、状态码、业务码和内容类型。
- 事务测试不能依赖测试框架自动回滚掩盖真实提交、异步或多线程行为。
- 应用上下文关闭测试检查未释放线程、调度器和客户端。

## 九、可观测性

- 使用 Micrometer/Observation 和 OpenTelemetry 兼容方式记录入口、外部调用和关键任务。
- 指标覆盖请求、连接池、线程池、队列、调度任务和下游依赖，不使用高基数标签。
- liveness 与 readiness 分离；自定义 HealthIndicator 不执行无界或高成本调用。
- trace/request ID 通过过滤器写入 MDC 和响应头，并传播到异步任务。

## 参考

- [Spring Boot - Structuring Your Code](https://docs.spring.io/spring-boot/reference/using/structuring-your-code.html)
- [Spring Framework - Declarative Transactions](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)
- [Spring Security - Authorization](https://docs.spring.io/spring-security/reference/servlet/authorization/index.html)
- [Spring Boot - Observability](https://docs.spring.io/spring-boot/reference/actuator/observability.html)
- [Spring Modulith - Verification](https://docs.spring.io/spring-modulith/reference/verification.html)
