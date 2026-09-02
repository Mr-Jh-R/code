# Java 后端附录

> 仅在项目画像声明使用 Java 时读取。本附录补充 Java 语言规则，不规定 Web 框架、ORM 或数据库。

## 一、版本与构建

- Java 版本以构建文件、工具链和运行环境为准，源码与测试使用同一目标版本。
- 构建必须可在命令行复现，优先使用项目提交的 Maven/Gradle Wrapper。
- 编译器警告和静态分析纳入标准验证；忽略项局部声明并说明原因。
- 发布产物记录 JDK、依赖和构建版本，不依赖开发者机器上的隐式全局配置。

## 二、源码与命名

- 选择一套 formatter 和 import 规则自动执行，不同时强制两套冲突风格。
- 包名全小写并表达业务边界；类型使用大驼峰；方法、字段和局部变量使用小驼峰；常量使用大写下划线。
- 禁止 wildcard import；重写方法使用 `@Override`。
- `equals` 与 `hashCode` 必须成对实现，并保持对称、传递、一致和空值语义。
- 不使用可变对象作为 Map key，除非其相等性字段在生命周期内不可变。
- 金额使用 `BigDecimal` 或明确的最小货币单位整数，不能使用二进制浮点表示精确金额。
- 时间点优先使用 `Instant` 或具有明确时区语义的类型；持续时间使用 `Duration`，不以无单位数字传递。

## 三、类型和数据模型

- 不可变 DTO、查询投影和值对象可以使用 `record`；实体生命周期或框架确实要求可变时使用普通类。
- `Optional` 适合表达可能缺失的查询返回值，不用于字段、序列化 DTO 或方法参数。
- 集合返回空集合而不是 `null`；公开契约明确元素是否可空。
- 枚举值持久化或对外传输时使用稳定 code，不依赖 `ordinal()`。
- 泛型保留具体类型信息，避免裸类型和无约束的 `Map<String, Object>`。
- Lombok 等代码生成工具只减少机械代码，不隐藏关键构造、相等性、不变量和副作用。

## 四、依赖与可见性

- 依赖通过构造器或方法参数显式传入，依赖字段尽可能为 `final`。
- 使用最小可见性；模块内部类型不因测试方便而无条件公开。
- 静态全局可变状态只用于经过证明的进程级缓存或注册表，并有并发与清理策略。
- 反射访问、动态代理和运行时扫描需要测试失败模式，并说明 native image/AOT 等运行约束（如适用）。

## 五、异常与资源

- 异常类型表达失败语义，不能只用消息文本区分。
- 捕获异常时完成恢复、翻译或补充边界上下文；否则保留 cause 继续抛出。
- 不吞异常，不使用异常控制正常分支，不向客户端返回 `Throwable.getMessage()`。
- checked/unchecked 的选择与调用方是否能合理恢复一致，项目画像记录统一策略。
- 文件、流、连接和锁使用 try-with-resources 或等价结构释放。
- 中断必须恢复中断标记或继续抛出 `InterruptedException`，不能静默吞掉。

## 六、并发

- 优先使用不可变数据、消息传递和结构化任务所有权，减少共享可变状态。
- `ConcurrentHashMap`、原子变量只保证其单次操作，不自动保证跨字段或检查后执行的原子性。
- 锁对象私有且稳定，锁内不执行远程调用、阻塞关闭或不可控回调。
- Executor 和 Scheduler 由容器或统一组件管理，线程命名并在关闭时回收。
- 平台线程池使用有界队列和明确拒绝策略。
- 虚拟线程提升阻塞型吞吐，不提升稀缺下游容量；不要池化虚拟线程，使用 semaphore/连接池限制稀缺资源。
- `CompletableFuture`、响应式流和异步回调显式处理异常、取消、上下文传播和超时。

## 七、日志与测试

- 使用 SLF4J 参数化日志，避免提前字符串拼接；异常只在责任边界打印一次完整堆栈。
- 日志参数中的对象应有安全、有限且不含敏感信息的字符串表示。
- 单元测试使用确定性时钟、受控执行器和明确断言，不依赖长时间 `sleep`。
- Mockito 等测试工具按其官方方式配置 agent，避免依赖未来 JDK 将禁止的动态自加载。
- 数据库、序列化、并发和框架代理语义由集成测试覆盖，不能只靠 mock 证明。

## 八、质量门禁

项目应从以下能力中选择并自动化：

- formatter/import：Spotless、google-java-format 或等价工具；
- 静态分析：Error Prone、SpotBugs、PMD、Sonar 或等价工具；
- 架构验证：ArchUnit 或框架提供的模块验证；
- 覆盖率：JaCoCo 或等价工具，关注变更和关键分支；
- 依赖分析：OWASP Dependency-Check、Dependabot 或等价 SCA。

工具选择和命令写入项目画像，规范不永久锁定插件版本。

## 参考

- [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)
- [Java API Design Guidelines](https://openjdk.org/guide/)
- [JEP 444 - Virtual Threads](https://openjdk.org/jeps/444)
- [Java SE API](https://docs.oracle.com/en/java/javase/)
