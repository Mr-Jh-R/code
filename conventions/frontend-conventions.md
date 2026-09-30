# 前端规范选择入口

本文件只负责选择适用的前端规范，不包含 React 或 Vue 的具体实现约束。

## 选择规则

1. 先查看目标包或项目的 `package.json`、lockfile 和 workspace 配置。
2. 使用 React、Next.js（React）或 React + Vite 时，阅读 [`frontend-conventions-react.md`](./frontend-conventions-react.md)。
3. 使用 Vue 3、Vue Router、Pinia、Nuxt（Vue）或 Vue + Vite 时，阅读 [`frontend-conventions-vue.md`](./frontend-conventions-vue.md)。
4. 同一个 monorepo 同时包含 React 和 Vue 时，按包或页面所在目录分别引用，不能混用两份规范。

## 组件库与复用原则

- 先检查目标包已有的 UI 组件库、设计系统和主题 token；标准按钮、表单、表格、弹窗、分页、反馈、布局和空状态优先复用已有组件。
- 组件库无法满足产品语义、交互、可访问性或视觉约束时，才实现自定义组件。不得为了套用某个库而替换项目已有技术栈。
- 自定义模式在两个或多个独立页面/模块中重复出现，或已经形成稳定的 props、events/handlers 和状态契约时，抽取为公共组件；只出现一次且语义尚未稳定时保留在页面或业务模块内。
- 公共组件保持单一职责，明确输入、输出、状态和可访问性；避免创建承载多个业务流程的万能组件。
- 组件抽取同时检查 loading、empty、error、disabled、keyboard 和 responsive 状态，不能只复用视觉外壳。

## 版本策略

规范描述的是工程原则，不永久锁定框架或库的具体版本。开发时应：

- 优先遵守项目已经存在的依赖、lockfile、workspace 和 peer dependency 约束；
- 新项目使用当前稳定、兼容、社区推荐的主版本；
- 升级前同时核对框架、路由、状态管理、构建工具和 UI 库的兼容性；
- 需要可复现构建时提交 lockfile，并通过项目的包管理器更新依赖；
- 只有在项目明确要求时，才在项目文档或配置中固定具体版本。

## AI 引用模板

```text
请先读取 docs/conventions/frontend-conventions.md。
根据目标包的 package.json 判断使用 React 还是 Vue，
然后只读取对应的 frontend-conventions-react.md 或 frontend-conventions-vue.md，
不要混用两份规范；版本以项目现有约束为准，否则采用当前稳定兼容版本。
```
