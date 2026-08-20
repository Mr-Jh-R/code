# SDD 开发工作流 Skill 包

> 规范驱动开发（Specification-Driven Development）完整工具包，开箱即用。

## 📦 包含内容

```
sdd-skill-repo/
├── skills/
│   └── sdd-workflow.md          # 核心 Skill 文件（AI 工作流指令）
├── conventions/
│   ├── frontend-conventions.md  # 前端代码规范
│   └── backend-conventions.md   # 后端代码规范
└── README.md
```

## 🚀 快速安装（5 分钟）

### 第一步：克隆本仓库

```bash
git clone https://github.com/Mr-Jh-R/code.git sdd-skills
```

### 第二步：安装 OpenSpec CLI

```bash
npm install -g @fission-ai/openspec@latest
```

### 第三步：复制 Skill 到你的项目

```bash
# 在你的项目根目录执行
mkdir -p .claude/skills
cp sdd-skills/skills/sdd-workflow.md .claude/skills/
mkdir -p docs/conventions
cp sdd-skills/conventions/frontend-conventions.md docs/conventions/
cp sdd-skills/conventions/backend-conventions.md docs/conventions/
```

### 第四步：初始化 OpenSpec

```bash
cd your-project
openspec init
```

### 第五步：在 CLAUDE.md 中声明工作流

在项目根目录的 `CLAUDE.md` 中添加：

```markdown
## AI 开发工作流

本项目采用 SDD（规范驱动开发）工作流：

- Skill 文件：`.claude/skills/sdd-workflow.md`
- 前端规范：`docs/conventions/frontend-conventions.md`
- 后端规范：`docs/conventions/backend-conventions.md`

### 开发四步原则
1. **需求先探索**：不清晰的需求使用 grill-me 模式澄清
2. **规范先制定**：用 `openspec propose` 生成 proposal/design/tasks
3. **TDD 先写测试**：实现前先写测试，确认后再实现
4. **验证再声称完成**：运行测试和类型检查通过后才能说完成
```

---

## 📋 工作流速查

### 完整开发流程

```
需求探索 → 规范制定 → 工作区隔离 → TDD实现 → 验证 → 归档
```

### 常用命令

```bash
# 需求探索（对话触发）
# "请用 grill-me 模式帮我探索 [功能] 需求"

# 规范制定
openspec propose [change-name]

# 查看变更列表
openspec list

# 验证实现
openspec verify [change-name]

# 继续未完成任务
openspec continue [change-name]

# 归档完成变更
openspec archive [change-name]
```

### 对话触发关键词

| 场景 | 对话指令 |
|------|---------|
| 需求不清晰 | `请用 grill-me 模式帮我探索 [功能] 需求` |
| 开始实现 | `请按 TDD 方式实现 tasks.md 中的任务` |
| 遇到 bug | `遇到这个 bug：[描述]，请系统化分析根因，不要直接给解决方案` |
| 代码审查 | `请审查这段代码，对照 [design.md] 检查是否符合设计规范` |

---

## 🔧 新项目配置

复制 `.claude/skills/sdd-workflow.md` 后，填写顶部配置区：

```
项目名称：___________
技术栈：___________
包管理器：___________
测试框架：___________
数据库迁移工具：___________
```

---

## 📚 规范文件说明

### 前端规范（`conventions/frontend-conventions.md`）

- API 接口自动生成（禁止手写 fetch/axios）
- 组件使用优先级（@ant-design/x > Ant Design 5 > ProComponents）
- 类型命名规范（`API.XxxRequest` / `API.XxxVO`）
- 响应格式统一（`BaseResponse`，用 `res.code === 0` 判断成功）

### 后端规范（`conventions/backend-conventions.md`）

- 分层架构（controller → service → mapper）
- 统一响应体（`BaseResponse<T>` + `ResultUtils`）
- 异常体系（`ErrorCode` 枚举 + `BusinessException` + `ThrowUtils`）
- 权限注解（`@AuthCheck(mustRole="admin")`）
- Entity 规范（雪花 ID、逻辑删除、Javadoc）

---

## 🛠️ 技术栈适配

本 Skill 设计为**技术栈无关**，内置模板支持：

| 层 | 支持 |
|----|------|
| 前端 | React / Vue / Next.js / Umi |
| 后端 | Java / Go / Python / Node.js |
| 数据库迁移 | Drizzle / Flyway / Liquibase / Alembic |
| 测试框架 | vitest / jest / JUnit / pytest / go test |

---

## 🤝 参考资料

- [mattpocock/skills](https://github.com/mattpocock/skills) — 工程师技能库（grill-me、tdd、diagnosing-bugs 等）
- [Superpowers Plugin](https://github.com/obra/superpowers) — Claude Code 执行纪律插件
- OpenSpec CLI：`openspec --help`
