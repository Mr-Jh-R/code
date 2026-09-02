# Backend 代码规范（v1 Legacy）

> 本文件保存 v1 的 Spring Boot + MyBatis-Plus 模板，仅供尚未迁移项目追溯。新项目使用 `../../backend-conventions.md` 选择 v2 通用核心和技术附录。本文件不再接收通用规则更新。

## 使用说明

本规范是 Spring Boot 项目的通用参考模板，不替代项目已经确认的架构、依赖和团队约定。使用时遵循以下优先级：

1. 目标项目中的 `AGENTS.md`、`CLAUDE.md`、README、架构决策记录和现有代码约定；
2. 目标模块已有的分层、命名、异常、日志和测试方式；
3. 本规范提供的默认建议。

新增代码应与现有项目保持一致。只有在旧实现存在明确问题且改动已经过评审时，才调整既有约定；不要为了套用本规范进行无关重构。依赖和工具版本以项目构建文件及锁定机制为准，新项目选择当前稳定、兼容的版本，不在通用规范中永久锁死具体版本。

## 一、文件结构

```text
backend/src/main/java/com/example/app/
├── Application.java              # 启动类（按项目命名）
├── annotation/                    # 自定义注解（如 @AuthCheck）
├── aop/                           # AOP 切面（AuthInterceptor、LogInterceptor）
├── common/                        # 通用基础类
│   ├── BaseResponse.java          # 统一响应体
│   ├── ResultUtils.java           # 响应构建工具
│   ├── PageRequest.java           # 分页请求基类
│   └── DeleteRequest.java         # 通用删除请求
├── config/                        # 配置类（CORS、数据源、JSON、外部服务、ORM 等）
├── constant/                      # 常量类（UserConstant、CommonConstant）
├── controller/                    # Controller 层，接收请求并返回响应
├── exception/                     # 异常体系
│   ├── ErrorCode.java             # 错误码枚举
│   ├── BusinessException.java     # 自定义业务异常
│   ├── GlobalExceptionHandler.java# 全局异常处理器
│   └── ThrowUtils.java            # 条件抛异常工具
├── manager/                       # 第三方集成、复杂能力和业务编排
├── mapper/                        # MyBatis-Plus Mapper 接口
├── model/
│   ├── dto/                       # 请求参数对象，按业务模块分子包
│   │   ├── user/
│   │   ├── order/
│   │   └── product/
│   ├── entity/                    # 数据库实体类（与表一一对应）
│   ├── enums/                     # 枚举类
│   └── vo/                        # 响应视图对象，按业务模块分子包
└── service/                       # Service 接口 + ServiceImpl 实现
```

---

## 二、命名规范

| 类型 | 命名格式 | 示例 |
| ------ | ---------- | ------ |
| DTO（新增请求） | `XxxAddRequest` | `OrderAddRequest` |
| DTO（更新请求） | `XxxUpdateRequest` | `OrderUpdateRequest` |
| DTO（查询请求） | `XxxQueryRequest` | `OrderQueryRequest` |
| DTO（其他请求） | `XxxXxxRequest` | `UserLoginRequest`, `OrderCancelRequest` |
| VO（响应对象） | `XxxVO` | `OrderVO`, `UserVO`, `LoginUserVO` |
| Entity（实体） | 表名大驼峰 | `User`, `Order`, `Product` |
| Mapper | `XxxMapper` | `UserMapper`, `OrderMapper` |
| Service 接口 | `XxxService` | `UserService` |
| Service 实现 | `XxxServiceImpl` | `UserServiceImpl` |
| Controller | `XxxController` | `UserController`, `OrderController` |
| 枚举类 | `XxxEnum` | `UserRoleEnum`, `OrderStatusEnum` |
| 配置类 | `XxxConfig` 或 `XxxConfiguration` | `CorsConfig`, `PaymentConfiguration` |
| 常量类 | `XxxConstant` | `UserConstant`, `CommonConstant` |
| Manager | `XxxManager` 或 `XxxOrchestrator` | `PaymentManager`, `OrderOrchestrator` |
| 注解 | 大驼峰 | `AuthCheck` |

**方法命名**：动词 + 名词，如 `userLogin`、`addOrder`、`listOrderByPage`、`deleteOrder`

**包名**：全小写，优先使用清晰的业务域名称，如 `order`、`product`、`payment`

---

## 三、通用类

### 3.1 统一响应体 `BaseResponse<T>`

```java
public class BaseResponse<T> implements Serializable {
    private int code;
    private T data;
    private String message;
}
```

### 3.2 响应工具 `ResultUtils`

```java
// 成功
ResultUtils.success(data);

// 失败 - 传 ErrorCode 枚举
ResultUtils.error(ErrorCode.PARAMS_ERROR);

// 失败 - 传 ErrorCode + 自定义消息
ResultUtils.error(ErrorCode.PARAMS_ERROR, "用户名不能为空");

// 失败 - 传 code + message
ResultUtils.error(40000, "自定义错误");
```

### 3.3 分页请求基类 `PageRequest`

```java
private int current = 1;      // 当前页，默认 1
private int pageSize = 10;    // 每页大小，默认 10
private String sortField;     // 排序字段
private String sortOrder = "descend";  // 排序方向，默认降序
```

查询 DTO 需要分页时，继承 `PageRequest`。

### 3.4 通用删除请求 `DeleteRequest`

包含 `id` 字段，所有删除接口统一使用此类接收参数。

---

## 四、异常体系

### 4.1 错误码枚举 `ErrorCode`

| 枚举值 | code | 说明 |
| -------- | ------ | ------ |
| `SUCCESS` | 0 | 成功 |
| `PARAMS_ERROR` | 40000 | 请求参数错误 |
| `NOT_LOGIN_ERROR` | 40100 | 未登录 |
| `NO_AUTH_ERROR` | 40101 | 无权限 |
| `CONFLICT_ERROR` | 40900 | 资源状态冲突 |
| `NOT_FOUND_ERROR` | 40400 | 数据不存在 |
| `FORBIDDEN_ERROR` | 40300 | 禁止访问 |
| `SYSTEM_ERROR` | 50000 | 系统内部异常 |
| `OPERATION_ERROR` | 50001 | 操作失败 |
| `EXTERNAL_SERVICE_ERROR` | 50200 | 外部服务调用异常 |

新增错误码时，4xxxx 为客户端错误，5xxxx 为服务端错误；业务域专用错误码应在项目内单独规划并记录。

### 4.2 自定义业务异常 `BusinessException`

```java
// 抛出方式（三选一）
throw new BusinessException(ErrorCode.PARAMS_ERROR);
throw new BusinessException(ErrorCode.PARAMS_ERROR, "自定义消息");
throw new BusinessException(40000, "自定义消息");
```

### 4.3 条件抛异常工具 `ThrowUtils`

```java
// 条件为 true 时抛出异常（推荐写法）
ThrowUtils.throwif(request == null, ErrorCode.PARAMS_ERROR);
ThrowUtils.throwif(request == null, ErrorCode.PARAMS_ERROR, "请求不能为空");
ThrowUtils.throwif(condition, new BusinessException(ErrorCode.SYSTEM_ERROR));
```

### 4.4 全局异常处理 `GlobalExceptionHandler`

- `BusinessException` → 返回 `ResultUtils.error(e.getCode(), e.getMessage())`
- `RuntimeException` → 返回 `ResultUtils.error(ErrorCode.SYSTEM_ERROR, "系统错误")`
- 类上加 `@Hidden` 使其不出现在 Swagger 文档

---

## 五、Entity 规范

```java
@TableName(value = "table_name")   // 指定表名
@Data
public class XxxEntity implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(type = IdType.ASSIGN_ID)  // 雪花算法生成 Long 类型 ID
    private Long id;

    // 业务字段...

    private Date editTime;    // 编辑时间
    private Date createTime;  // 创建时间
    private Date updateTime;  // 更新时间

    @TableLogic                // 逻辑删除
    private Integer isDelete;
}
```

**规范要点：**

- ID 类型为 `Long`，使用雪花算法 `IdType.ASSIGN_ID`
- 逻辑删除字段固定为 `isDelete`（Integer），不做物理删除
- 时间字段类型用 `Date`（非 `LocalDateTime`）
- 每个字段加 Javadoc 注释
- 实现 `Serializable` 并声明 `serialVersionUID`
- **MyBatis-Plus 关闭了下划线转驼峰**（`map-underscore-to-camel-case: false`），字段名与数据库列名保持一致

---

## 六、Controller 层规范

```java
@RestController
@RequestMapping("/module")     // 模块路径
public class XxxController {

    @Resource
    private XxxService xxxService;

    /**
     * 操作说明（中文 Javadoc）
     */
    @PostMapping("/add")
    public BaseResponse<Long> addXxx(@RequestBody XxxAddRequest request) {
        ThrowUtils.throwif(request == null, ErrorCode.PARAMS_ERROR);
        // 调用 service
        long id = xxxService.addXxx(request);
        return ResultUtils.success(id);
    }

    /**
     * 管理员操作加 @AuthCheck 注解
     */
    @AuthCheck(mustRole = "admin")
    @PostMapping("/admin/delete")
    public BaseResponse<Boolean> adminDeleteXxx(@RequestBody DeleteRequest deleteRequest) {
        // ...
    }
}
```

**规范要点：**

- 使用 `@Resource` 注入（不用 `@Autowired`）
- 方法第一行用 `ThrowUtils.throwif` 做空校验
- 返回值统一 `BaseResponse<T>`，用 `ResultUtils.success()` / `ResultUtils.error()` 构建
- 需要管理员权限的接口路径加 `/admin/` 前缀，并加 `@AuthCheck(mustRole = "admin")`

---

## 七、权限注解 `@AuthCheck`

```java
@AuthCheck(mustRole = "admin")   // 必须是管理员
@AuthCheck(mustRole = "user")    // 必须已登录用户
```

在 `AOP/AuthInterceptor` 中拦截并校验，角色字符串参考 `UserConstant` 中的常量。

---

## 八、配置文件规范

### 8.1 多环境配置

- `application.yml`：公共配置，敏感字段用占位符（如 `your-db-password`）
- `application-local.yml`：本地真实配置，**不提交 git**

### 8.2 MyBatis-Plus 配置

```yaml
mybatis-plus:
  configuration:
    map-underscore-to-camel-case: false   # 关闭驼峰转换，字段名与列名一致
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
  global-config:
    db-config:
      logic-delete-field: isDelete
      logic-delete-value: 1
      logic-not-delete-value: 0
```

### 8.3 Swagger / knife4j 配置

```yaml
springdoc:
  api-docs:
    path: /v3/api-docs
  group-configs:
    - group: 'default'
      paths-to-match: '/**'
      packages-to-scan: com.example.app.controller

knife4j:
  enable: true
  setting:
    language: zh_cn
  basic:
    enable: true
    username: admin
    password: ${API_DOC_PASSWORD}   # 通过环境变量提供 Basic Auth 凭证
```

访问地址以项目配置为准：`http://localhost:<server-port>/<context-path>/doc.html`。其中端口和上下文路径分别读取 `server.port`、`server.servlet.context-path`；如果项目调整了 Knife4j 路径，也应使用实际配置。

---

## 九、Enum 规范

```java
@Getter
public enum XxxEnum {

    VALUE_A("描述A", "code_a"),
    VALUE_B("描述B", "code_b");

    private final String text;
    private final String value;

    XxxEnum(String text, String value) {
        this.text = text;
        this.value = value;
    }

    // 可选：提供静态查找方法
    public static XxxEnum getEnumByValue(String value) {
        // ...
    }
}
```

枚举类用 `@Getter`（Lombok），不用 `@Data`。

---

## 十、MySQL 建表规范（仅在项目使用 MySQL 时适用）

> 以下规范适用于 MySQL，其他数据库（如 PostgreSQL）语法不同，不适用。

### 10.1 字段命名

- **一律使用驼峰命名**（camelCase），不使用下划线
- 与 Java Entity 字段名完全一致（MyBatis-Plus 已关闭 `map-underscore-to-camel-case`）
- 示例：`userId`、`userName`、`createTime`、`isDelete`

### 10.2 主键规范

```sql
id  bigint auto_increment comment '主键ID' primary key,
```

- 字段名统一为 `id`，类型 `bigint auto_increment`
- 对应 Java 端使用 `@TableId(type = IdType.ASSIGN_ID)`（雪花 ID，Long 类型，非自增）

> 注意：数据库用 `auto_increment` 只是保留主键能力，实际 ID 由 Java 层雪花算法生成后写入，不依赖数据库自增。

### 10.3 必备标准字段

每个表末尾必须包含以下 4 个字段，顺序固定：

```sql
editTime     datetime     default CURRENT_TIMESTAMP not null comment '编辑时间',
createTime   datetime     default CURRENT_TIMESTAMP not null comment '创建时间',
updateTime   datetime     default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
isDelete     tinyint      default 0                 not null comment '是否删除'
```

| 字段 | 说明 |
| ------ | ------ |
| `editTime` | 最后编辑时间，默认当前时间，由业务层手动更新 |
| `createTime` | 创建时间，默认当前时间，不再变更 |
| `updateTime` | 更新时间，每次 UPDATE 自动刷新 |
| `isDelete` | 逻辑删除（0=未删除，1=已删除） |

### 10.4 字符集

统一使用 `utf8mb4_unicode_ci`，在 `create table` 末尾声明：

```sql
) comment '表说明' collate = utf8mb4_unicode_ci;
```

### 10.5 注释规范

- 每张表必须写 `comment`，说明表的用途
- 每个字段必须写 `comment`，使用中文简洁描述

### 10.6 索引规范

| 类型 | 命名格式 | 示例 |
| ------ | --------- | ------ |
| 普通索引 | `idx_字段名` | `idx_userId` |
| 复合索引 | `idx_字段1_字段2` | `idx_userId_status` |
| 唯一约束 | `uk_字段名` | `uk_userAccount` |

```sql
create index idx_userId on tableName (userId);

-- 唯一约束写在表定义内
constraint uk_userAccount unique (userAccount)
```

### 10.7 状态字段规范

- 命名：`status`，类型 `tinyint`，默认 `1`
- 注释需列出所有状态值：

```sql
status  tinyint  default 1  not null comment '状态（0禁用 1启用）',
```

### 10.8 建表完整示例

```sql
create table exampleTable
(
    id           bigint auto_increment comment '主键ID'
        primary key,
    userId       bigint                             not null comment '用户ID',
    title        varchar(256)                       not null comment '标题',
    content      text                               null comment '内容',
    status       tinyint  default 1                 not null comment '状态（0禁用 1启用）',
    sortOrder    int      default 0                 not null comment '排序权重（越大越靠前）',
    editTime     datetime default CURRENT_TIMESTAMP not null comment '编辑时间',
    createTime   datetime default CURRENT_TIMESTAMP not null comment '创建时间',
    updateTime   datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    isDelete     tinyint  default 0                 not null comment '是否删除'
) comment '示例表' collate = utf8mb4_unicode_ci;

create index idx_userId on exampleTable (userId);
```

### 10.9 常用字段类型参考

| 场景 | 类型 |
| ------ | ------ |
| 主键 / 外键 ID | `bigint` |
| 短字符串（账号、名称、URL） | `varchar(N)` |
| 长文本（内容、JSON 配置） | `text` |
| 时间 | `datetime` |
| 状态 / 逻辑删除标记 | `tinyint` |
| 数值（排序、计数） | `int` |

---

## 十一、代码设计与可读性

### 11.1 基本原则

- 类和方法保持单一职责；一个方法内的语句应处于同一抽象层级。
- 使用准确的业务名称表达意图，避免 `data`、`info`、`process`、`handle` 等缺少上下文的泛化命名。
- 优先使用卫语句处理非法参数和异常分支，减少多层 `if` 嵌套。
- 将复杂条件提取为有业务含义的方法、规则对象或策略；不要用注释弥补难以理解的布尔表达式。
- 方法长度以能够完整表达一个职责为准。既不堆积多个流程，也不为了追求行数而拆成大量无意义的转发方法。
- 仅在形成稳定业务概念、消除有害重复或建立清晰测试边界时抽象；相似但变化原因不同的代码不强行合并。
- 优先使用不可变局部变量和明确的数据流，避免共享可变状态、隐式副作用和跨层修改同一对象。
- 删除无用代码、过期注释和调试输出，不保留注释掉的旧实现；历史由版本控制系统保存。

### 11.2 分层职责

- Controller 负责协议适配、参数校验、身份上下文获取和响应转换，不承载核心业务规则。
- Service 或应用服务负责用例编排、事务边界和业务流程；领域规则应放在对应的领域对象或领域服务中。
- Repository、Mapper 和 Client 分别封装持久化与外部系统访问，上层不依赖其实现细节。
- DTO、Entity 与 VO 的职责分离，不直接把数据库实体作为公开接口的请求或响应模型。
- 外部服务、消息、缓存和数据库访问应建立明确边界，使核心业务逻辑能够独立测试。
- 事务范围应尽量小且清晰。除非业务一致性方案明确要求，否则不要在数据库事务中执行耗时远程调用。

### 11.3 设计模式使用原则

设计模式用于处理真实存在的变化点和复杂性，不是代码质量目标本身。简单分支和一次性流程优先采用直接实现；不要为“可能以后会扩展”预先增加多层接口、抽象类或工厂。

| 场景 | 可选模式 | 使用判断 |
| ------ | ---------- | ---------- |
| 多种可替换的业务规则或算法 | 策略模式 | 新增规则时不需要修改主流程，且每种规则可独立测试 |
| 对象创建过程复杂，具体类型随场景变化 | 工厂模式 | 调用方不应知道构造细节，创建逻辑确实存在变化 |
| 第三方 SDK、旧系统或外部协议接入 | 适配器模式 | 需要隔离外部模型和变化，防止其侵入业务层 |
| 主流程稳定，仅部分步骤允许变化 | 模板方法 | 步骤顺序有明确约束，并且复用收益高于继承成本 |
| 对象行为随有限状态发生明确变化 | 状态模式 | 状态迁移复杂，普通条件分支已经难以维护 |
| 多个处理器按条件依次处理请求 | 责任链模式 | 处理步骤需要独立组合、短路或调整顺序 |

引入设计模式前必须能够说明：当前复杂性是什么、模式消除了哪些分支或耦合、为什么更简单的方案不足。引入后应满足：

- 调用方更简单，职责和依赖方向更清晰；
- 每个策略、适配器或处理器可以独立测试；
- 新增常见变体时主要通过扩展完成，而不是同时修改多个无关模块；
- 类和接口数量的增加与获得的可维护性收益相匹配。

## 十二、中文 Javadoc 规范

### 12.1 必须添加 Javadoc 的位置

- 新增或修改的 Java 接口、类、枚举，以及 `public`、`protected` 方法；
- 接口中的每个方法，用于说明调用契约；
- 包含关键业务规则、非显然算法或重要副作用的私有方法；
- 需要解释单位、取值范围、业务含义或兼容约束的字段和枚举值。

Javadoc 使用中文书写。实现类与接口契约完全一致时，可使用 `{@inheritDoc}` 继承接口说明；实现存在额外约束或副作用时，必须补充说明，不能只复制接口文字。

### 12.2 内容要求

- 第一段说明职责或业务语义，不逐行复述实现。
- 说明调用前置条件、重要约束、副作用、幂等性或线程安全要求（如适用）。
- 根据实际签名完整使用 `@param`、`@return`、`@throws`，参数说明应包含单位、范围或是否可空等必要信息。
- `@throws` 描述可预期的失败条件，不记录实现中不会抛出的异常。
- 不写无维护价值的作者、创建时间、修改历史；这些信息由版本控制系统提供。

```java
/**
 * 订单应用服务，负责订单提交用例的编排。
 */
public interface OrderService {

    /**
     * 提交待确认订单。
     *
     * <p>同一幂等键重复提交时返回首次创建的订单编号，不重复扣减库存。</p>
     *
     * @param command 提交命令，商品明细和幂等键不能为空
     * @return 创建或已存在的订单编号
     * @throws BusinessException 商品不可售、库存不足或命令不合法时抛出
     */
    Long submitOrder(OrderSubmitCommand command);
}
```

行内注释只用于解释不直观的原因、约束或取舍，不解释代码已经清楚表达的操作。代码变化后必须同步更新注释；无法保持准确的注释应重写或删除。

## 十三、格式化与质量门禁

- 代码格式由构建工具统一执行，IDE 格式化只作为本地辅助。优先沿用项目已有的 Spotless、Checkstyle、PMD、Sonar 或等价配置。
- 项目尚无格式化工具时，可评估使用 Spotless 集成 Java formatter；引入前先确认团队格式，避免一次提交重排全部历史文件。
- 格式化和静态检查应接入 Maven `verify`、Gradle `check` 或 CI 的等价阶段，确保本地与流水线规则一致。
- 提交前至少运行目标模块适用的格式检查、编译和测试。修改公共 API、持久化、事务或外部集成时，应补充对应的集成测试或契约测试。
- 只格式化本次修改涉及的文件，除非任务明确要求全量迁移；格式化变更不要与无关业务修改混在同一提交中。
- AI 工具声称完成前必须报告实际执行的检查及结果；无法运行的检查要明确说明原因和剩余风险。

---

## 十四、依赖与框架

| 功能 | 依赖 |
| ------ | ------ |
| ORM | MyBatis-Plus |
| 数据库 | MySQL（业务数据）+ PostgreSQL（向量存储） |
| 日志 | SLF4J + `@Slf4j` |
| 对象简化 | Lombok（`@Data`、`@Getter`、`@Slf4j` 等） |
| 对象拷贝 | `BeanUtils.copyProperties(src, target)` |
| 领域扩展框架 | 按项目需求选型（可选） |
| API 文档 | springdoc-openapi + knife4j |
| 文件存储 | 通过项目统一适配层接入所选服务 |
