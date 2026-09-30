# React 前端代码规范

本规范适用于 React、Next.js（React）和 React + Vite 项目。Vue 项目请阅读 [`frontend-conventions-vue.md`](./frontend-conventions-vue.md)，不要混用两份规范。文中的 Umi、Ant Design 和响应体示例只在项目已经采用对应工具时生效；不要为了套用规范而新增或替换项目技术栈。

## 版本策略

- 先读取目标项目的 `package.json`、lockfile、workspace 配置和 peer dependency 约束。
- 已有项目优先遵守当前依赖；新项目使用当前稳定、兼容、社区推荐的 React 生态版本。
- 本规范不永久固定 React、路由、状态管理或构建工具的具体版本号。
- 升级前核对 React、路由、状态管理、构建工具、TypeScript 和 UI 库之间的兼容性，并运行项目验证命令。

## 一、API 接口更新流程（重点）

如果项目已配置 `@umijs/openapi` 从后端 Swagger 文档生成 API 函数，应使用生成客户端，**禁止绕过生成层重复手写 fetch/axios 请求**。未使用该生成器的项目应遵循已有 API 客户端和请求封装，不需要为了本规范安装 `@umijs/openapi`。

### 1.1 完整更新步骤

#### 第一步：确保后端已启动

后端服务正常运行，Swagger 文档可正常访问。

#### 第二步：在前端项目根目录执行生成命令

```bash
npm run openapi_dev
```

等价于直接运行：

```bash
node openapi.config.js
```

此命令会自动：

1. 从后端下载最新 OpenAPI spec（Swagger JSON）
2. 将 spec 缓存到本地（通常为 `openapi-spec.json`，不提交 git）
3. 在 `src/api/` 下生成所有接口的 TypeScript 函数和类型定义

#### 第三步：在页面中使用生成的 API

```ts
// 正确：从生成的模块导入
import { addItem, listItemByPage, deleteItem } from '@/api/itemController';

// 禁止：手写 fetch/axios 请求
// const res = await fetch('/api/item/add', { method: 'POST', body: JSON.stringify(data) });
```

### 1.2 何时需要重新生成

以下情况必须重新执行生成命令：

- 后端新增了接口
- 后端修改了接口路径
- 后端修改了请求参数或返回值
- 后端修改了 DTO / VO 字段

### 1.3 openapi.config.js 结构说明

```js
import { generateService } from '@umijs/openapi';

generateService({
  requestLibPath: "import request from '@/request'",  // 使用项目自定义 request 封装
  schemaPath: specPath,                                // 本地缓存的 spec 文件路径
  serversPath: './src',                                // 生成到 src/api/
});
```

> 生成的文件头部含 `// @ts-ignore` 和 `/* eslint-disable */`，**不要手动编辑**，下次生成会覆盖。

---

## 二、文件结构

```text
src/
├── api/                   # 自动生成的 API 层（禁止手动修改）
│   ├── typings.d.ts       # 所有类型定义（API.XxxRequest / API.XxxVO）
│   ├── xxxController.ts   # 每个后端 Controller 对应一个文件
│   └── index.ts           # 统一导出入口
├── pages/                 # 页面组件（按路由/模块划分目录）
├── components/            # 公共/可复用组件
├── request.ts             # HTTP 请求封装（全局拦截器、错误处理）
├── constants/             # 常量定义
└── utils/                 # 工具函数
```

---

## 三、类型使用规范

所有请求参数和响应类型均来自 `@/api/typings.d.ts`，通过 `API.` 命名空间访问：

```ts
// 请求 DTO 类型
API.XxxAddRequest
API.XxxUpdateRequest
API.XxxQueryRequest

// 响应 VO 类型
API.XxxVO
API.LoginUserVO

// 分页响应
API.PageResultXxxVO

// 通用响应包装
API.BaseResponseLong
API.BaseResponseBoolean
API.BaseResponseXxxVO
```

### 示例：在页面中使用

```tsx
import { addItem, listItemByPage } from '@/api/itemController';

// 新增
const handleAdd = async (values: API.ItemAddRequest) => {
  const res = await addItem(values);
  if (res.code === 0) {
    message.success('新增成功');
  }
};

// 分页查询
const fetchList = async (params: API.ItemQueryRequest) => {
  const res = await listItemByPage(params);
  return {
    data: res.data?.records ?? [],
    total: res.data?.total ?? 0,
  };
};
```

---

## 四、组件使用优先级

如果项目使用 Ant Design 生态，前端实现功能或样式时按下表优先复用现成组件。使用其他设计系统的项目应保持现有组件库，不要为了本规范迁移到 Ant Design。

| 优先级 | 库 | 适用场景 |
| -------- | ----- | --------- |
| 1（最高） | `@ant-design/x` | AI 对话专用：`Bubble`、`Sender`、`Conversations`、`ThoughtChain` 等 |
| 2 | `Ant Design` | 通用 UI：使用项目当前兼容版本的 `Button`、`Table`、`Form`、`Modal`、`Select`、`Upload` 等 |
| 3 | `@ant-design/pro-components` | 高级业务组件：`ProTable`、`ProForm`、`ProLayout`、`ProDescriptions` 等 |
| 4 | 社区成熟库 | `react-markdown`（Markdown）、`@monaco-editor/react`（代码编辑器）等 |
| 5（最低） | 手写自定义 | 以上均无法满足时才手动实现 |

### 典型场景对应

| 场景 | 推荐方案 | 禁止做法 |
| ------ | --------- | --------- |
| Markdown 渲染 | `react-markdown` | 手写解析器 |
| 流式 AI 回复 | `Bubble`（`streaming` prop） | 手写光标动画 |
| 思维链展示 | `ThoughtChain` | 手写步骤时间轴 |
| 代码高亮 | `CodeHighlighter` 或 `@monaco-editor/react` | 手写高亮 |
| 数据表格（含分页/搜索） | `ProTable` | 手写 Table + 分页组合 |
| 复杂表单 | `ProForm` | 手写 Form + 校验逻辑 |
| 页面布局 | `ProLayout` | 手写导航+侧边栏 |

---

组件库优先不等于所有页面都必须使用同一套组件。保留项目现有设计系统；当自定义模式在两个或多个独立页面/模块中重复，或已经形成稳定 props、回调和状态契约时，抽取到 `components/` 或业务模块的共享目录。一次性且语义未稳定的页面结构先就地实现，避免抽象出带大量分支的万能组件。

## 五、请求封装规范

使用 `@umijs/openapi` 的项目应让所有 API 请求经过项目统一的 `@/request` 封装，生成的函数直接调用即可：

```ts
// 生成的函数签名（自动生成，勿手写）
export async function addItem(
  body: API.ItemAddRequest,
  options?: { [key: string]: any }
): Promise<API.BaseResponseLong>
```

如果后端契约使用 `BaseResponse`，按生成类型处理以下结构；其他项目应遵循其 OpenAPI 契约，不要套用本示例：

```ts
{
  code: 0,         // 0 = 成功，非 0 = 失败
  data: ...,       // 业务数据
  message: 'ok'   // 消息描述
}
```

**判断成功**统一用 `res.code === 0`，不要用 `res.data`是否存在来判断。

---

## 六、命名规范

| 类型 | 格式 | 示例 |
| ------ | ------ | ------ |
| 页面组件 | `PascalCase` | `UserList.tsx`, `OrderDetail.tsx` |
| 公共组件 | `PascalCase` | `SearchBar.tsx`, `ConfirmModal.tsx` |
| 工具函数 | `camelCase` | `formatDate.ts`, `parseJson.ts` |
| 常量 | `SCREAMING_SNAKE_CASE` | `MAX_PAGE_SIZE`, `DEFAULT_TIMEOUT` |
| CSS 类名 | `kebab-case` | `user-card`, `action-button` |
| 接口函数（生成） | `camelCase` 动词+名词 | `addItem`, `listItemByPage`, `deleteItem` |

---

## 七、常见问题

### Q：生成命令报错"无法从后端下载 spec"

原因：后端未启动。确保后端服务正常运行后重试。

### Q：生成后出现类型报错

原因：`typings.d.ts` 未正确生成。检查生成命令是否成功执行，查看本地 spec 缓存文件是否为最新内容。

### Q：需要调用的接口没有生成对应函数

原因：后端 Controller 方法未添加 Swagger 注解，或未被 `packages-to-scan` 扫描到。联系后端补充注解后重新生成。

### Q：能否手动修改生成的 API 文件？

不能。生成的 `src/api/` 下所有文件每次执行生成命令都会被覆盖。如需扩展，在其他模块中二次封装。
