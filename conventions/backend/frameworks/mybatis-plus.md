# MyBatis / MyBatis-Plus 持久化附录

> 仅在项目画像选择 MyBatis 或 MyBatis-Plus 时读取。普通 MyBatis 项目使用映射、SQL 和生成维护规则；`BaseMapper`、`IService`、`ServiceImpl` 与插件条款仅适用于 MyBatis-Plus。Java 规则见 [Java 附录](../languages/java.md)，Spring 集成另读 [Spring Boot 附录](spring-boot.md)。

## 一、版本与使用范围

- 从构建文件、依赖解析结果和运行配置确认 MyBatis、MyBatis-Plus、starter、插件与数据库版本，沿用项目已有组合；不为采用本附录更换 ORM 或升级依赖。
- 在项目画像记录 CRUD 风格、映射策略、插件约定和生成文件的维护方式。复杂业务与简单管理表可以在同一项目采用不同实现，不按全仓 Service 数量或继承数量判断合规。
- 人工编写、AI 编写和代码生成采用同一文件契约；模板可以统一命名和减少重复代码，但文件存在不能证明其映射、权限或事务已经生效。不依赖特定 IDE 或插件。

## 二、基础 CRUD 与 Mapper

- MyBatis-Plus 的单表基础操作优先复用 `BaseMapper<Entity>`，不重复手写同等 CRUD SQL。Mapper 的注册、扫描、实体表名、主键和字段映射应与运行配置一致。
- 只用内置 CRUD 且映射满足需求时，可以没有 Mapper XML，也无需同时创建 `IService`、`ServiceImpl` 或 Repository。
- 简单条件可用类型安全的 Lambda Wrapper；联表、聚合、复杂动态 SQL 或专用投影按项目约定放到 Mapper XML 或专用查询中。普通 MyBatis 的注解/Provider 查询仍可沿用，不强制所有 SQL 写入 XML。
- Wrapper 和 Mapper 属于持久化实现细节，业务调用方传入明确的查询条件或命令。前端不能提交任意 Wrapper、SQL 片段或数据库字段名来控制数据访问。

## 三、XML 映射与字段投影

### 文件位置与结构

- Mapper 接口命名为 `<Entity>Mapper.java`，放在项目既有或所属业务模块的 `mapper` 包；使用 XML 时通常同名为 `<Entity>Mapper.xml`，放在 classpath 可加载的资源目录，例如 `src/main/resources/mapper/<module>/`，实际扫描路径由项目配置决定。
- XML 使用 UTF-8，保留 XML 声明与 MyBatis Mapper DTD；缩进遵循项目 formatter，未约定时采用四个空格。
- 根节点为 `<mapper namespace="Mapper接口全名">`。按映射、复用片段、查询/写入语句组织；需要完整实体映射和重复列清单时可统一命名为 `BaseResultMap`、`Base_Column_List`，专用投影使用能表达用途的独立名称。只声明实际需要的节点。
- 映射使用 `<id>` 表达标识列、`<result>` 表达普通列；嵌套结果按需使用 `association`/`collection`。`column` 按真实 SQL 输出列名或别名填写，`property` 按目标 Java 属性填写；增删字段时同步核对映射与调用。

### 映射定义与引用

| 内容 | 作用与采用方式 |
| --- | --- |
| `resultMap` | 显式定义结果列到对象属性的映射；列名差异、联表重名、嵌套结果或特殊类型处理时优先考虑 |
| `BaseResultMap` | 常见映射 ID，不是自动绑定规则；名字可沿用项目约定 |
| `<sql id="Base_Column_List">` | 复用相同的字段投影；由具体 SQL 通过 `<include>` 引用，不会自动替换内置 CRUD 的选列 |
| `resultType` / 自动映射 | 简单结果可按列名或别名映射，驼峰规则以实际配置为准；同一 select 的 `resultType` 与 `resultMap` 二选一 |
| `@TableName(resultMap=...)` | 让适用的 MP 内置查询引用已注册映射；使用完整 ID 并检查加载与实际语句 |
| `@TableName(autoResultMap=true)` | 按 MP 实体元数据构建映射；与 MyBatis 按列名自动映射不同，不会让任意自定义查询自动采用该映射 |

1. XML `namespace` 对应 Mapper 接口全名，语句 ID 与接口方法对应，参数名与 `@Param` 等绑定方式一致；检查资源确实进入构建产物并被加载。
2. 生成的 `resultMap` 要被查询、注解或框架元数据实际引用才有作用；只生成空用途的 XML 不作为完成条件。
3. 投影只包含查询需要的字段；DTO/VO、联表和统计按结果定义选择列，不机械复用完整实体列清单。联表使用表别名和结果别名处理重名列。
4. 列名、Java 属性、主键、null、枚举、JSON、时间及类型处理器逐项核对。XML 结果映射负责读取，不替代 MP 写入所需的实体字段映射或参数类型处理。
5. 不为“让 XML 被使用”而统一添加 `@TableName(resultMap=...)`。例如 MP 3.5.9 的手工映射路径可能把默认选列改为 `*`；按项目实际版本检查生成 SQL、投影与敏感字段，不能推定所有查询都遵循 `@TableField(select=false)`。

以下仅示意一个自定义查询如何引用映射和列片段，不是必建文件模板。假设表为 `catalog_item`，逻辑删除列为 `deleted`；Mapper 声明 `Item findActiveById(@Param("id") Long id)`，类型和路径换成项目实际值：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "https://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.catalog.mapper.ItemMapper">
    <resultMap id="BaseResultMap" type="com.example.catalog.model.entity.Item">
        <id column="id" property="id"/>
        <result column="name" property="name"/>
    </resultMap>
    <sql id="Base_Column_List">id, name</sql>
    <select id="findActiveById" resultMap="BaseResultMap">
        SELECT <include refid="Base_Column_List"/>
        FROM catalog_item
        WHERE id = #{id} AND deleted = 0
    </select>
</mapper>
```

如有租户、对象权限或业务状态限制，按实际用例追加约束；该示例本身不构成完整业务授权。

## 四、Service 复用与业务边界

`IService<T>` 和 `ServiceImpl<M,T>` 是框架提供的 CRUD 复用方式，可以减少分页、批量操作和基础访问的封装。选择依据是业务复杂度和公开能力，而非统一继承形式：

| 场景 | 建议结构 |
| --- | --- |
| 以数据维护为主的管理功能 | 可以用 `XxxService extends IService<Entity>`，实现类 `extends ServiceImpl<Mapper, Entity> implements XxxService`；允许在业务方法中复用 CRUD |
| 已有 Service 直接调用 `BaseMapper` 且足够清晰 | 保持直接调用，不为形式额外增加通用 Service 或 Repository |
| 审核、状态机、多表一致性或复杂权限 | 向 Controller/其他模块暴露 `approve`、`reject` 等用例方法；内部可复用 `BaseMapper` 或 CRUD 组件 |
| 远程调用、调度编排或纯计算 | 不要求继承数据库 CRUD；按能力组织接口 |

- 简单 CRUD 也有授权、字段白名单与校验要求。有业务规则不等于禁止继承；应让调用路径经过这些规则，而不是把继承的 `save`、`updateById`、`removeById` 自动视为完整业务用例。
- 复杂业务可以通过组合一个内部 CRUD 组件，或只向调用方提供窄的用例接口来限制访问；结合模块可见性、依赖检查或代码审查约束使用。按实际需要选一种，不给每张表机械增加多层转发。
- Controller 负责 DTO、身份和协议适配，业务 Service 执行用例。`HttpServletRequest` 等 Web 上下文不传播到核心业务；`getQueryWrapper` 等构建查询的能力留在实现内部，公开查询返回所需 DTO/VO 或稳定模型。
- 多个 CRUD 调用组成的业务事务仍需明确一致性边界、传播和回滚；部分框架批量方法自带事务注解，并不代表整个用例已被覆盖。
- 应用自己声明的依赖按 Spring 附录使用构造器注入；不改写第三方基类内部的注入机制，也不因此禁止复用它。
- Service 继承扩展的是 Java 方法集合，不会自动创建 HTTP 端点，也不是逻辑删除、乐观锁等能力的开关。

## 五、SQL、插件与更新行为

- SQL 值使用 `#{...}` 等参数绑定。动态标识符只接受服务端白名单或映射；使用 Lambda Wrapper 也不能放宽原始 SQL 方法的输入来源。
- 查询和批量操作设置范围与上限。更新明确可修改字段、null 的语义以及全量/局部更新方式；不要把请求对象的全部属性直接当成可写实体字段。
- 配置逻辑删除后，MP 内置语句按实体元数据处理；手写 XML/注解 SQL 不能假设会自动补齐逻辑删除条件。恢复、物理清理等操作另定入口与授权。
- 乐观锁需核对插件注册、`@Version`、旧版本参数、具体更新方法及实际 SQL。自定义更新即使触发了插件的参数处理，SQL 仍需消费旧版本条件并更新新版本；影响行数为零按业务区分冲突、不存在或无权限。
- 租户隔离、数据权限、分页、乐观锁和自动填充按各自配置、参数和版本限制验证。自动填充时间/操作者字段不等于完整业务审计。
- 自定义 XML 或注解覆盖内置同名语句时，重新核对逻辑删除、版本条件、字段策略和插件行为；既不能假定全部自动生效，也不能假定全部失效。
- Wrapper 按调用创建，避免共享可变条件；尤其在 `update(entity, wrapper)` 乐观锁场景，不复用已参与更新的 Wrapper。多数据源时确认 Mapper 与事务管理器对应同一目标。

## 六、编写与生成文件维护

- 开发者、AI 和可选生成器均按本附录的文件格式编写；交付前核对包名、字段类型、实体注解、XML 引用及实际 SQL。无需安装 IDE 插件，也不以某个工具生成的文件头作为合规依据。
- 项目使用生成器时，记录模板、输入 schema、输出位置与覆盖策略；未使用生成器时直接维护源码，不额外建立生成流程。
- 区分两种所有权：持续由生成器重建的文件只改模板/输入；一次生成后交由开发者维护的实体、Mapper、Service 和 XML 按普通源码维护。项目应声明采用哪一种，不能只凭文件曾由插件生成就禁止编辑。
- 重新生成前核对已有差异；输出到临时位置或用不覆盖模式比较，再选择性合并字段变更。保留自定义 SQL、业务方法、校验和注解。
- 新增或修改字段时同步有实际使用关系的映射、投影和类型处理器；不要求所有表都补空 XML，不批量重写已稳定的业务 Service。

## 七、按变更范围验证

1. **映射与加载**：核对 namespace、方法 ID、参数绑定、资源加载和实际 resultMap 引用；覆盖本次涉及的字段别名、null、特殊类型和联表结果。
2. **读取与过滤**：在项目测试环境验证真实 SQL 的选列、逻辑删除、权限/租户范围及分页；文件存在或编译成功不能代替结果核对。
3. **写入与一致性**：涉及更新时覆盖可写字段、冲突与影响行数；涉及多步写入时覆盖中途失败后的业务回滚。使用受控测试数据，不在共享业务数据上试写。
4. **边界与生成**：确认业务调用不绕过用例规则，重新生成没有覆盖自定义内容。纯规范变更只运行文档和示例校验；实际采用项目补相应集成证据。

## 参考

- [MyBatis Mapper XML](https://mybatis.org/mybatis-3/sqlmap-xml.html)
- [MyBatis-Plus 持久层接口](https://baomidou.com/guides/data-interface/)
- [MyBatis-Plus 注解](https://baomidou.com/reference/annotation/)
- [逻辑删除](https://baomidou.com/guides/logic-delete/)
- [乐观锁](https://baomidou.com/plugins/optimistic-locker/)
- [MP v3.5.9 的映射与选列实现](https://github.com/baomidou/mybatis-plus/blob/v3.5.9/mybatis-plus-core/src/main/java/com/baomidou/mybatisplus/core/injector/AbstractMethod.java)
