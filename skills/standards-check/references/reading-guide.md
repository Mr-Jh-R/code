# 按技术栈读取实际规则

先按 `local-versions.md` 确认唯一通用规范快照。项目入口是业务上下文与补充规则来源，不能把搜索到的旧克隆作为第二套通用基线。说明本次 Skill 路径、规范 ID、SHA 和 root 后才开始检查。

## 读取顺序

1. 读取目标项目入口与本次模块配置；从 `package.json`、`pyproject.toml`、构建/锁文件及实际代码确认语言、框架、数据库。monorepo 按目标包识别，不因根目录含 Java 就将所有模块视为 Java。
2. 从选定规范 root 中读取相应入口和正文。入口、目录、搜索命中和脚本列出的路径都不是正文阅读的替代；被截断时分段读完选定文件。选定版本的“完整读取”要求仍有效，不能以本指引悄悄放宽旧版本。
3. 按下表增加相关附录；只读取本次适用项。规范提到其他技术并不代表该技术适用，例如跨语言 core 中的 Java 包路径建议不适用于 Python。
4. 特定风险再补事务、权限、并发、外部调用、数据迁移等相关章节；审查调用方时发现范围变化，追加对应规则和证据。

以下路径相对快照的 `conventions/`，必须实际存在才读取：

| 目标 | 正文 |
| --- | --- |
| React / Next.js React | `frontend-conventions.md` + `frontend-conventions-react.md` |
| Vue / Nuxt Vue | `frontend-conventions.md` + `frontend-conventions-vue.md` |
| 其他前端技术 | `frontend-conventions.md` 中跨框架原则 + 项目生态配置；说明无专用附录 |
| 后端（任何语言） | `backend-conventions.md` + `backend/core.md` + 项目补充约定 |
| Java | 追加 `backend/languages/java.md` |
| Python | 选定版本存在时追加 `backend/languages/python.md`，包括数字响应码与 Python 特有约束 |
| FastAPI | 选定版本存在时追加 `backend/frameworks/fastapi.md`；框架示例与测试按需查看 |
| Spring Boot | 追加 `backend/frameworks/spring-boot.md` |
| MyBatis / MyBatis-Plus | 追加 `backend/frameworks/mybatis-plus.md`，按选择版本实际内容使用 |
| MySQL / PostgreSQL | 追加对应 `backend/databases/mysql.md` / `postgresql.md`，与语言独立选择 |
| AI/LLM 集成 | 追加 `backend/extensions/ai-llm.md` |
| 设计新抽象或复杂重构 | 追加 `backend/design-patterns.md` |
| 文件归类 / Git 整合发布 | 按需追加 `repository-layout.md` / `git-workflow.md` |
| 检查流程 | 所选版本有 `quality-gates.md` 时读取；没有时使用 Skill 的检查流程及项目门禁，报告版本缺项 |

可以先运行脚本得到已验证的绝对路径：

```text
python <脚本> read-plan --version <版本ID> --frontend react
python <脚本> read-plan --version <版本ID> --backend --language python --database mysql
```

`read-plan` 验证快照但不会读取业务代码或代替审查；实际框架和风险仍由 Agent 根据项目事实选择。`missing_appendices` 表示所选版本无对应附录，不是业务代码违规，也不能用另一个版本的文件静默补齐。

## 没有专用语言规则时

例如 Python + MySQL：读跨语言后端核心、MySQL 附录及选定版本存在的 Python 附录，再核对项目 `pyproject.toml` 中 Ruff/格式化/测试约定；FastAPI 项目额外读取其框架附录。旧版本没有 Python/FastAPI 附录时明确报告缺项，不混用其他版本的正文；不读 Java、Spring、MyBatis，也不套用它们的包结构、构造器注解或 ServiceImpl 约束。

没有 Python 专用附录不妨碍核对权限、输入输出、错误、资源、数据一致性等共同原则；语言细节使用项目已有约定并说明覆盖范围。规范示例中的 Umi、Ant Design 等只在项目已采用且满足该规则条件时适用。

完成条件：已选文件的正文读完，说明适用规则与未覆盖的技术细节，然后给出代码证据；不能读完 SKILL.md 就宣布缺少规范而停止。
