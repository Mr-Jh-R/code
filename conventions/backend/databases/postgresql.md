# PostgreSQL 数据库附录

> 仅在项目画像声明使用 PostgreSQL 时读取。版本、扩展、schema 和隔离级别以目标环境为准。

## 一、Schema

- 主键使用 identity、UUID 或项目明确策略；不把 `SERIAL` 当成所有新项目的唯一选择。
- 时间点使用 `TIMESTAMPTZ` 并统一以 UTC 处理；本地日历时间使用 `TIMESTAMP` 时说明语义。
- 结构化扩展数据可以使用 `JSONB`，频繁过滤、关联和约束字段仍应正规化。
- 业务不变量使用 `NOT NULL`、`CHECK`、`UNIQUE`、`FOREIGN KEY` 和 exclusion constraint 等能力表达。
- 需要把多个 `NULL` 视为相同时，评估 `NULLS NOT DISTINCT`。
- 跨租户归属使用复合唯一键与复合外键，使数据库不能建立错误关联。
- 外键不会自动为引用列建索引，根据 join 和父记录更新/删除路径显式评估。

## 二、事务与并发

- 默认 `READ COMMITTED` 下，同一事务的不同语句可以看到不同已提交快照；业务不能假设天然可重复读。
- 丢失更新使用原子 SQL、版本列、行锁或可重试的更高隔离级别解决。
- `SERIALIZABLE` 和 serialization failure 要求整个事务可安全重试，并有次数与总预算。
- 多对象加锁保持稳定顺序；对死锁、锁超时和 serialization failure 分类处理。
- 使用 `INSERT ... ON CONFLICT` 时由唯一约束定义冲突目标，并确认更新条件和返回语义。
- 长事务会阻碍 vacuum 和版本清理，事务中不等待用户或远程系统。

## 三、索引与查询

- B-tree 复合索引对最左列约束通常最有效，列顺序匹配过滤、范围和排序。
- 部分索引只有在规划期能推出查询条件蕴含其谓词时生效，参数化查询尤其需要验证。
- `INCLUDE` 能支持 index-only scan，但收益取决于可见性映射和表更新频率。
- GIN、GiST、BRIN、trigram、全文、空间和向量索引根据数据分布与目标查询选型。
- 使用 `EXPLAIN (ANALYZE, BUFFERS)` 在接近真实的数据量验证；`ANALYZE` 会实际执行语句。
- 避免机械创建超过三列的宽索引，除非访问模式稳定且执行计划证明收益。

## 四、迁移

- 所有 schema 变更通过版本化迁移交付，已执行迁移不可修改。
- `CREATE INDEX CONCURRENTLY` 等不能运行在普通事务块中的语句使用迁移工具的正确事务配置。
- 新增非空列、大表类型转换和约束验证采用降低锁风险的分阶段方案。
- 可以先创建 `NOT VALID` 约束并在后续验证，但必须跟踪到最终有效状态。
- migration 默认 fail fast，`IF NOT EXISTS` 不能掩盖对象定义漂移。

## 五、运行配置

- 配置 `statement_timeout`、`lock_timeout`、`idle_in_transaction_session_timeout` 和连接获取时限。
- 连接池总量结合数据库预算、实例数和事务时长；大量轻量应用实例可以评估外部连接池。
- 监控连接、锁等待、死锁、慢查询、vacuum、表膨胀、复制延迟和磁盘增长。
- 扩展版本和备份恢复纳入发布与灾难恢复演练。

## 参考

- [PostgreSQL Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html)
- [PostgreSQL Transaction Isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [PostgreSQL Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [PostgreSQL EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [PostgreSQL Client Timeouts](https://www.postgresql.org/docs/current/runtime-config-client.html)
