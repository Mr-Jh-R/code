# Alibaba P3C 与当前后端规范的对照研究

> 研究日期：2026-09-30
> P3C 核对提交：`6c59c8c36ecd8722c712d5685b8c3822c1c8b030`
> 对照文件：`conventions/backend/core.md`、`conventions/backend/languages/java.md`、`conventions/backend/frameworks/spring-boot.md`、`conventions/backend/databases/mysql.md`
> 目的：判断当前通用规范已经覆盖哪些 P3C 主题、哪些内容可以补充，以及哪些 P3C 规则不应直接升级为所有项目的强制规则。本文只记录研究结论，不修改规范正文。

## 总结

当前规范已经覆盖 P3C 的大部分高风险主题，而且在事务、并发、SQL 注入、数据约束、测试和生产可观测性方面比旧版 P3C 更强调边界条件和运行证据。主要缺口集中在 Java 语言级的小型陷阱（集合 API、包装类型比较、弃用 API、`switch` 默认分支）以及公共 Java API 的 Javadoc 约定。

不建议把 P3C 中带有旧技术栈假设或固定阈值的规则直接写成通用强制项。典型例子包括“禁止所有外键”“超过三个表禁止 JOIN”“单表 500 万行才分库分表”“所有事务必须编程式”“所有类必须写作者和创建日期”“所有场景强制 CSRF”以及 MySQL 专用的 `ISNULL()`、`utf8`、固定索引命名等。它们可以作为某个项目的画像决策，但不能代表所有 Java、数据库或部署环境。

## 分类别对照

### 1. 命名

**P3C 来源**：[`编程规约/命名风格.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/编程规约/命名风格.md)第 1 至 16 条，涉及 `$`/下划线边界、禁止拼音混用、CamelCase、异常/测试类后缀、包名、缩写、Service/DAO 接口等。

**当前已覆盖**：`java.md` 第二节规定包名、类型、方法、字段和常量命名；`core.md` 3.1 要求名称表达业务含义、方向和单位，避免含糊的 `data/info/flag/process`；模型职责和 DTO/VO 分离也已有约定。

**当前缺口**：没有明确禁止以 `$` 或下划线开头/结尾、拼音英文混写和不清晰缩写；没有 Java 项目级的异常类和测试类后缀建议；没有 Service/DAO 命名的具体项目画像模板。数组括号、枚举 `Enum` 后缀等属于较低优先级格式选择。

**不宜照搬**：P3C 要求 Service/DAO 一律接口加 `Impl`，与当前“仅在多实现、跨模块端口、外部适配或替身有价值时定义接口”的设计原则冲突。`Impl` 不应成为通用强制命名；如果项目选择该风格，应放入项目画像。

### 2. OOP 与设计

**P3C 来源**：[`编程规约/OOP规范.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/编程规约/OOP规范.md)第 1 至 20 条，涉及静态成员访问、`@Override`、可变参数、接口兼容、弃用 API、`equals`、基本/包装类型、POJO 默认值、序列化、构造器、`toString`、访问控制和方法顺序。

**当前已覆盖**：`java.md` 已覆盖 `equals`/`hashCode` 配对、不可变 Map key、Optional 使用边界、集合空值、泛型具体类型、金额和时间类型、依赖显式传入及最小可见性；`core.md` 强调深模块、边界隔离、业务不变量和副作用隔离；`spring-boot.md` 要求构造器注入和 `final` 依赖。

**当前缺口**：没有单独写出“静态成员用类名访问”“避免过时 API”“包装类值比较用 `equals`”“构造器不做业务逻辑”“接口兼容/弃用迁移”等 Java 小规则。`@Override` 虽是通用编译器可检查项，也没有在 `java.md` 明确列出。

**不宜照搬**：P3C 的“所有 POJO 属性使用包装类型”“所有 POJO 不设默认值”“所有 POJO 必须手写 `toString`”“所有 RPC 参数和返回值使用包装类型”会与 `record`、ORM、配置绑定、序列化默认值和框架要求冲突；应根据边界语义和框架约束选择。方法顺序、`final` 使用、是否给枚举加 `Enum` 后缀可以作为 formatter/项目风格，不应冒充行为安全规则。

### 3. 集合

**P3C 来源**：[`编程规约/集合处理.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/编程规约/集合处理.md)第 1 至 13 条，覆盖 `equals`/`hashCode`、`subList`、`toArray`、`Arrays.asList`、通配符、遍历修改、Comparator、初始容量和 Map 遍历。

**当前已覆盖**：`java.md` 要求集合返回空集合、不使用裸泛型、避免无约束 `Map<String,Object>`；`core.md` 对分页上限、稳定排序、批处理和游标分页有更强的接口层约束。

**当前缺口**：没有明确记录 `subList` 与原集合生命周期、`Arrays.asList` 不可增删、foreach 中修改集合、Map `entrySet` 遍历等容易被静态检查发现的陷阱。

**建议**：可以新增一段“常见 Java 集合 API 陷阱”作为推荐或检查清单，优先由 Error Prone、PMD、SpotBugs 或测试验证。不要把某个集合实现的初始容量、所有 Comparator 细节或 `Iterator` 加锁写成跨语言的后端硬规则。

### 4. 并发

**P3C 来源**：[`编程规约/并发处理.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/编程规约/并发处理.md)第 1 至 15 条，涉及线程安全单例、线程命名、禁止直接创建线程、线程池、锁范围、锁顺序、乐观锁、`Timer`、`volatile`、`ThreadLocal` 和 `HashMap`。

**当前已覆盖**：`core.md` 8 节和 `java.md` 第六节要求任务由运行时统一管理、队列有界、锁范围最小、锁顺序稳定、共享状态有所有者、Executor/Scheduler 生命周期可关闭、异步上下文和超时显式传播；还补充多实例 lease/fencing、虚拟线程与下游容量无关等现代约束。

**当前缺口**：没有逐条写出禁止 `Executors` 工厂、线程名称必须有意义、不要用 `Timer`、`volatile` 不能替代复合原子性等 P3C 提示。不过这些通常更适合作为 Java 静态分析或代码审查检查项。

**不宜照搬**：P3C 中“冲突概率低于 20% 用乐观锁”“乐观锁重试不得少于 3 次”是经验阈值；当前规范正确地要求依据冲突、预算和幂等性选择，不应固定为所有系统的数字。现代 Java 也不应把 `SimpleDateFormat` 作为主要并发规则，优先禁止无时区旧日期 API 并使用 `java.time`。

### 5. 异常

**P3C 来源**：[`异常日志/异常处理.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/异常日志/异常处理.md)第 1 至 13 条，覆盖预检查 RuntimeException、异常不作流程控制、区分稳定/非稳定代码、捕获后处理、事务回滚、资源关闭、finally 返回、异常类型匹配和自定义异常。

**当前已覆盖**：`core.md` 5 节和 `java.md` 第五节已要求错误边界、异常翻译、保留 cause、不吞异常、不以异常作正常分支、结构化错误码、安全消息和 try-with-resources；`spring-boot.md` 还明确 checked exception 的回滚策略。

**当前缺口**：没有明确说可通过预检查避免的 NPE/越界不应依靠 catch 处理；也没有单独强调 catch 的类型应与抛出类型匹配或避免 finally 中 return。

**建议**：补充为 Java 附录的低歧义规则即可。不要照搬 P3C 分层文档中“DAO catch `Exception`、Service 必须打印”的固定层级，因为当前规范已经要求按责任边界记录一次并保留 cause，更适合模块化和异步系统。

### 6. 日志

**P3C 来源**：[`异常日志/日志规约.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/异常日志/日志规约.md)第 1 至 8 条，涉及 SLF4J 门面、日志保留天数、日志文件名、占位符、`additivity=false`、案发现场和堆栈、生产级别及输入错误级别。

**当前已覆盖**：`java.md` 第七节要求 SLF4J 参数化日志、有限安全字符串、责任边界单次堆栈；`core.md` 11 节要求结构化日志、关联 ID、敏感信息不入日志、指标低基数、审计和可执行告警。

**当前缺口**：没有规定文件至少保留 15 天、Logback 的 `additivity=false` 或 `appName_logType_logName.log` 命名。它们属于部署和日志后端配置，当前仓库有意将其留给项目画像。

**不宜照搬**：日志保留时间必须由合规、容量和故障窗口决定；`additivity` 只适用于特定日志实现；所有用户输入错误都用 warn 也可能造成噪声。当前规范的“可诊断、低噪声、脱敏、单次堆栈”更适合作为通用基线。

### 7. MySQL、SQL 与 ORM

**P3C 来源**：[`MySQL数据库/建表规约.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/MySQL数据库/建表规约.md)、[`索引规约.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/MySQL数据库/索引规约.md)、[`SQL语句.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/MySQL数据库/SQL语句.md)和[`ORM映射.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/MySQL数据库/ORM映射.md)。

**当前已覆盖**：`mysql.md` 已覆盖 InnoDB/utf8mb4、主键、金额、时间、JSON、软删除、索引与执行计划、keyset 分页、连接池、锁等待、死锁、迁移和备份；`core.md` 要求参数化查询、动态标识符白名单、持久化约束、事务/锁/冲突/容量和恢复；`spring-boot.md` 要求 ORM 选择、动态 SQL 白名单和事务测试。

**当前缺口**：没有 P3C 风格的固定索引前缀、三字段（`id/gmt_create/gmt_modified`）、表名必须单数、布尔列必须 `is_xxx`、`varchar` 5000 阈值、更新必改时间字段、禁止存储过程、分页 count 为零提前返回等项目级细节。

**不宜照搬**：

- “禁止外键与级联”与当前使用数据库原生约束的规则冲突；应基于服务边界、迁移能力和删除语义选择。
- “超过三个表禁止 JOIN”“左模糊一律禁止”“性能目标固定为 range/ref/const”无法适用于所有查询、索引和数据分布。
- “500 万行/2GB 才分库分表”是历史经验阈值；当前规范按工作集、延迟、写入和运维预算决策。
- `ISNULL()` 是 MySQL 函数，不应替代跨数据库可读的 `IS NULL` 语义；`utf8` 也不是现代 MySQL 通用字符集基线。
- 固定索引命名和 `gmt_*` 字段可以纳入使用方的数据库画像，但不能要求 PostgreSQL、NoSQL 或不采用该审计字段的项目照搬。

### 8. 事务

**P3C 来源**：ORM 映射规约第 9 条仅标为“参考”，提醒不要滥用 `@Transactional`，并评估跨缓存、搜索、消息和统计的回滚；异常处理规约第 5 条要求捕获异常后需要回滚时明确回滚。P3C PMD 的 [`TransactionMustHaveRollbackRule`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-pmd/src/main/resources/rulesets/java/ali-exception.xml) 示例接受 `rollbackFor = Exception.class` 或显式 `TransactionManager.rollback`。

**当前已覆盖**：`spring-boot.md` 第四节已把 `@Transactional` 放在用例入口，说明代理、自调用、异步线程、默认回滚、checked exception、耗时 I/O 和独立失败状态；`core.md` 第七节补充 outbox、幂等、补偿、锁等待和分布式事务边界。

**结论**：没有实质缺口。通用规范应默认声明式事务，编程式事务仅用于动态边界、传播/隔离/超时、显式事务名或补偿流程等有证据的需求。不能把“控制粒度更细”变成所有事务都使用编程式的规则。

### 9. 注释

**P3C 来源**：[`编程规约/注释规约.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/编程规约/注释规约.md)第 1 至 11 条，要求类、字段和方法 Javadoc、抽象方法说明、作者/日期、枚举字段注释、变更同步和 TODO 处理。

**当前已覆盖**：`core.md` 3.3 要求稳定公共契约、跨模块接口和幂等/线程安全/单位/副作用等边界有说明；注释解释原因、约束和风险，权威 API/事件/数据契约采用机器可验证格式；Java 代码使用版本控制保留历史。

**当前缺口**：没有把公共 Java 类型、接口方法和枚举字段的 Javadoc 形式写成明确规则。

**不宜照搬**：所有类必须写作者和创建日期会与版本控制重复，且在复制/生成代码时迅速过时；所有属性和简单方法都写注释也会降低信噪比。建议只为公共 API、跨模块接口和非显然约束要求 Javadoc/契约注释，并禁止过期注释和无责任人的 TODO。

### 10. 测试与安全

**P3C 来源**：[`单元测试.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/单元测试.md)第 1 至 16 条要求 AIR（自动、独立、可重复）、`src/test/java`、核心代码增量测试、BCDE 边界/正确/设计/错误测试、数据库测试数据准备和回滚。P3C [`安全规约.md`](https://github.com/alibaba/p3c/blob/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook/安全规约.md)第 1 至 8 条覆盖权限、敏感数据脱敏、SQL 参数化、输入校验、HTML 转义、CSRF 和防刷。

**当前已覆盖**：`core.md` 第六节覆盖默认拒绝、认证授权、对象级权限、凭证、日志脱敏、SSRF、限流、上传和数据生命周期；第十三节覆盖单元/集成/契约/迁移/并发/安全测试、变更覆盖、扫描和缺陷复现。`java.md` 第七节要求确定性时钟、受控执行器、集成测试验证数据库/序列化/并发/代理；`repository-layout.md` 允许测试目录按技术栈约定放置。`spring-boot.md` 覆盖 `@Valid`、安全边界、MockMvc/WebTestClient 和测试上下文关闭。

**当前缺口**：没有使用 AIR/BCDE 作为术语，也没有强制所有项目采用 `src/test/java`，这是因为仓库规范同时服务 Java、Python、Node 等技术栈。

**不宜照搬**：70% 语句覆盖率、核心模块 100% 分支覆盖率可以作为某个项目门禁，不应成为所有项目的单一质量指标；覆盖率不能替代契约、并发和故障测试。CSRF 需要根据浏览器 Cookie/会话认证模型启用，纯 Bearer token API 不应机械套用。`src/test/java` 应由 Java/Maven/Gradle 项目画像决定，而不是写入跨语言核心规范。

## 建议的补充优先级（不修改正文）

如果后续决定完善规范，建议按以下顺序评估：

1. **低争议 Java 规则**：补充 `@Override`、弃用 API、包装类 `equals`、预检查代替 NPE/越界 catch、集合遍历修改和 `Arrays.asList`/`subList` 陷阱。
2. **公共 API 注释**：在 Java 附录中说明公共类型/方法/枚举字段需要 Javadoc 或等价契约说明，但不要求作者日期和机械 getter 注释。
3. **项目画像模板**：将索引命名、审计字段、测试目录、日志保留、覆盖率门禁、CSRF 模式等放入项目级配置。
4. **静态分析映射**：把 P3C、SpotBugs、Error Prone、Checkstyle 等工具作为可选门禁，记录启用规则和误报豁免，而不是复制全部 P3C 条目。

## 来源

- [Alibaba P3C 仓库](https://github.com/alibaba/p3c)
- [P3C GitBook 目录](https://github.com/alibaba/p3c/tree/6c59c8c36ecd8722c712d5685b8c3822c1c8b030/p3c-gitbook)
- [Spring Framework：声明式事务](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative.html)
- [Spring Framework：编程式事务](https://docs.spring.io/spring-framework/reference/data-access/transaction/programmatic.html)
- [Spring Framework：声明式与编程式事务选择](https://docs.spring.io/spring-framework/reference/data-access/transaction/tx-decl-vs-prog.html)
- [Spring Framework：依赖注入](https://docs.spring.io/spring-framework/reference/core/beans/dependencies/factory-collaborators.html)
- [Spring Framework：`@Autowired`](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/autowired.html)
- [Spring Framework：`@Resource`](https://docs.spring.io/spring-framework/reference/core/beans/annotation-config/resource.html)
