# MyBatis XML 映射与 MyBatis-Plus 通用 Service 评估

> 日期：2026-10-08。状态：研究评估，**不是生效规范**。
> 范围：官方文档及 MyBatis-Plus v3.5.9 源码；jz_code 对照固定为 `4fb642a62e563ec506af42d582618bc32a795e31`。没有启动服务或验证运行 SQL。

本记录的结论已用于编写 [MyBatis/MyBatis-Plus 附录](../../conventions/backend/frameworks/mybatis-plus.md)；采用项目以附录与自身锁定版本为准。

## 结论

建议将这些内容作为 MyBatis/MyBatis-Plus 项目的可选技术约定，重点约束实际映射、业务边界和验证方式。`BaseResultMap`、`Base_Column_List` 是项目可选命名；`IService`、`ServiceImpl` 是 CRUD 复用机制。它们都不是所有后端项目必须采用的架构。人工、AI 或生成器均可按统一格式维护，不以 IDE 插件作为前置条件。[2][3]

| 提议 | 评估 |
| --- | --- |
| 统一实体、Mapper、XML 文件格式 | 可以，编写后应审查并维护；缺少 XML 不代表 MP 内置 CRUD 无法工作。[2][3] |
| 每个 XML 都生成 `BaseResultMap` | 可以作为模板，但只有被语句或框架元数据引用才生效，不能以文件存在证明映射完成。[2][4][5] |
| 复用 `Base_Column_List` | 重复且相同的投影适合复用；每条语句仍需显式 `<include>`，DTO/VO 查询按需求选择字段。[2] |
| 所有 Service 继承 `IService`/`ServiceImpl` | 不宜成为通用硬规则；可在内部 CRUD 组件复用，业务入口应表达用例、权限和一致性边界。[3][6] |
| 继承通用 Service 会绕过插件 | 不成立；是否生效取决于执行的 Mapper 语句、插件注册、参数、实体元数据及自定义 SQL。[7][8][9] |

## XML 定义与执行引用

1. MyBatis `<select>` 使用 `resultType` 或 `resultMap`，两者择一。`resultMap` 的 `id` 是可被引用的标识，名称叫 `BaseResultMap` 并没有自动绑定含义。简单结果可以按列名自动映射；下划线转驼峰取决于 `mapUnderscoreToCamelCase` 配置。显式映射与自动映射还可混用。[2]
2. `<sql id="Base_Column_List">` 只是可复用 SQL 片段，具体 SQL 通过 `<include refid="Base_Column_List"/>` 使用它。片段不决定结果对象的映射，也不会自动替换 MP 注入语句的列清单。[2][5]
3. MP `@TableName(resultMap = "...")` 声明显式结果映射；`autoResultMap = true` 根据实体元数据生成映射，默认是 `false`，已指定 `resultMap` 时不再自动生成。它和 MyBatis 按列名自动映射是不同机制。[4]
4. v3.5.9 `TableInfoHelper` 从 `@TableName.resultMap()`/`autoResultMap()` 设置元数据；`AbstractMethod.addSelectMappedStatementForTable` 有 `table.getResultMap()` 时引用它，否则使用实体类型。`TableInfo.initResultMapIfNeed` 生成的是命名空间下的 `mybatis-plus_实体类名`，不是通过寻找 `BaseResultMap` 自动绑定。[5]
5. 因此仅生成 XML，不会自动使 MP 的 `selectById`/`selectList` 使用其中的 `BaseResultMap`。自定义语句可以显式声明 `resultMap`；MP 注入查询如需它，则配置完整的映射 ID，并验证实际 MappedStatement 和 SQL。[2][4][5]
6. 不宜为了“让 XML 被使用”而无条件添加 `@TableName(resultMap=...)`：v3.5.9 的 `sqlSelectColumns` 在手工 resultMap 且非自动生成时以 `*` 为默认投影；没有手工映射或使用自动映射时才走实体列选择。需要检查实际选列、Wrapper 显式投影以及敏感字段，不能仅凭 `@TableField(select=false)` 推断所有查询安全。[4][5]
7. 联表嵌套对象、列重名、特殊类型处理器等场景适合明确映射；自定义查询也不能假定实体上的 `autoResultMap`、字段过滤或类型处理器会自动覆盖该查询自己的 `resultType`/`resultMap`。投影和映射都应按实际语句核对。[2][4]

## 通用 Service 的边界

- 官方将 `BaseMapper<T>` 定位为通用 Mapper CRUD 接口，将 `IService<T>` 定位为 Service CRUD 接口；基础 Mapper 操作不要求创建对应的 `IService`。使用前仍需正确注册 Mapper、实体映射和 MP 运行配置。[3]
- v3.5.9 `ServiceImpl<M extends BaseMapper<T>, T>` 继承 `CrudRepository<M,T>` 并实现 `IService<T>`；`IService<T>` 继承 `IRepository<T>`。这提供基础数据访问能力，不自动产生用户授权、领域校验、幂等或业务事务编排。[6]
- 可以在内部数据访问组件复用此能力；对外暴露 `addUser(request)`、`changeUserRole(request)` 等用例接口，避免 Controller 将 `save(entity)`、任意 Wrapper 或 `removeById` 当作完整业务流程。管理后台 CRUD 也要在服务边界校验权限、可写字段和影响行数。这是本评估的架构建议，不是 MP 官方禁止 Controller 调用 CRUD 的规则。
- 不应把每次继承方法调用当成一个完整业务事务：v3.5.9 的部分批量方法有 `@Transactional`，但多个 CRUD 调用组成的用例仍需独立设计一致性边界、代理调用路径和回滚测试。[6]
- 模板可以提供 `IService`/`ServiceImpl` 风格，但使用方应选择其适用范围；领域服务、远程适配器和纯计算组件无需为了模板继承数据库 CRUD。[3][6]

## 逻辑删除、乐观锁和自定义 SQL

| 能力 | 生效条件与限制 |
| --- | --- |
| 逻辑删除 | 配置 `@TableLogic` 或全局逻辑删除字段后，MP 生成的查询/更新/删除语句加入相应逻辑。v3.5.9 这主要来自 SQL 注入模板，不是对所有手写 SQL 无条件追加过滤的插件。自定义 SQL 必须显式实现或复用删除条件；审计、恢复、物理清理则明确例外。[5][7] |
| 乐观锁 | 注册 `OptimisticLockerInnerInterceptor`，配置 `@Version`，并提供有效版本值。官方列出 `updateById(entity)`、`update(entity,wrapper)` 等支持路径；`update(entity,wrapper)` 的 Wrapper 不应复用。[8] |
| 自定义更新与乐观锁 | 满足内置参数条件的自定义更新也可能进入乐观锁逻辑。v3.5.9 拦截器按参数中的实体和版本处理，写回新版本并提供旧版本参数；自定义 SQL 仍需正确更新新版本且以旧版本作条件，并检查影响行数。不能断言“自定义方法一律不支持”，也不能只见 `@Version` 就断言并发保护有效。[8][9] |
| 插件链 | MP 拦截器作用于 Executor/StatementHandler，Service 的继承关系不是开关。自定义 Mapper 语句仍可能经过已注册插件；具体行为受插件配置、忽略策略、SQL 形态和版本限制影响。[9] |
| 覆盖内置方法 | v3.5.9 已存在同名 XML/注解 MappedStatement 时，SQL 注入器会跳过该方法的内置注入。此时使用的是自定义 SQL，应重新核对逻辑删除、版本条件和字段策略；不是全部插件自动失效。[5][9] |

## jz_code 的静态对照

- 在固定提交核对：MP 为 3.5.9；四个 Mapper XML（Agent、User、LlmModel、LlmProvider）仅声明 `BaseResultMap` 与 `Base_Column_List`，未定义 CRUD 语句；全仓未见指向它们的 `resultMap`、`refid`、`@ResultMap` 或 `@TableName(resultMap=...)`/`autoResultMap` 使用点。[10]
- `AgentMapper` 继承 `BaseMapper<Agent>`；`Agent` 使用 `@TableName(value="agent")` 和 `@TableLogic`。结合官方注入源码，可以判断这些 XML 映射没有可见的显式绑定，不能把生成文件视为 CRUD 已经使用它们的证据；这不是运行时验证结论。[5][10]
- 静态统计：9 个接口继承 `IService`、9 个实现继承 `ServiceImpl`、10 个 Mapper 继承 `BaseMapper`。`UserController` 存在直接调用 `save/updateById/removeById/page/getQueryWrapper` 的用法；应评估业务边界，而非仅检查模板继承结构。[10]

## 如后续纳入规范，建议约束的内容

1. 仅在项目选择 MyBatis/MyBatis-Plus 时加载；保留生成工具和模板选择，不要求为空用途生成 XML。
2. 明确字段映射及实际引用、投影、分页/联表和敏感字段策略；生成后人工或自动审查，增改字段同步维护。
3. 通用 CRUD 与业务用例分清职责；验证授权、逻辑删除、乐观冲突、影响行数及用例回滚，尤其是自定义 SQL 和覆盖内置语句。
4. 以使用方锁定的依赖版本核对行为；本记录的源码结论限定 v3.5.9，不能直接当成其他版本的实现保证。

## 一手来源

[2]: https://mybatis.org/mybatis-3/sqlmap-xml.html "MyBatis Mapper XML：select、sql、resultMap 与 Auto-mapping"
[3]: https://baomidou.com/en/guides/data-interface/ "MyBatis-Plus：IService 与 BaseMapper 持久化接口"
[4]: https://baomidou.com/en/reference/annotation/ "MyBatis-Plus：TableName.resultMap/autoResultMap 与 TableField.select/typeHandler"
[5]: https://github.com/baomidou/mybatis-plus/blob/v3.5.9/mybatis-plus-core/src/main/java/com/baomidou/mybatisplus/core/injector/AbstractMethod.java "v3.5.9：结果映射、选列、逻辑删除条件及同名语句检查"
[6]: https://github.com/baomidou/mybatis-plus/blob/v3.5.9/mybatis-plus-spring/src/main/java/com/baomidou/mybatisplus/extension/service/IService.java "v3.5.9：IService 与部分批量事务声明"
[7]: https://baomidou.com/en/guides/logic-delete/ "MyBatis-Plus：逻辑删除行为"
[8]: https://baomidou.com/en/plugins/optimistic-locker/ "MyBatis-Plus：乐观锁、自定义更新支持及 Wrapper 限制"
[9]: https://github.com/baomidou/mybatis-plus/blob/v3.5.9/mybatis-plus-extension/src/main/java/com/baomidou/mybatisplus/extension/plugins/inner/OptimisticLockerInnerInterceptor.java "v3.5.9：乐观锁参数处理和版本写回"
[10]: https://github.com/Mr-Jh-R/jz_code/tree/4fb642a62e563ec506af42d582618bc32a795e31/backend "jz_code 固定提交后端源码"

补充源码：[TableInfoHelper](https://github.com/baomidou/mybatis-plus/blob/v3.5.9/mybatis-plus-core/src/main/java/com/baomidou/mybatisplus/core/metadata/TableInfoHelper.java)、[TableInfo](https://github.com/baomidou/mybatis-plus/blob/v3.5.9/mybatis-plus-core/src/main/java/com/baomidou/mybatisplus/core/metadata/TableInfo.java)、[ServiceImpl](https://github.com/baomidou/mybatis-plus/blob/v3.5.9/mybatis-plus-spring/src/main/java/com/baomidou/mybatisplus/extension/service/impl/ServiceImpl.java)、[UpdateById](https://github.com/baomidou/mybatis-plus/blob/v3.5.9/mybatis-plus-core/src/main/java/com/baomidou/mybatisplus/core/injector/methods/UpdateById.java)、[MybatisPlusInterceptor](https://github.com/baomidou/mybatis-plus/blob/v3.5.9/mybatis-plus-extension/src/main/java/com/baomidou/mybatisplus/extension/plugins/MybatisPlusInterceptor.java)。
