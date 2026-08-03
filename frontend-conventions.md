# 前端代码规范

## 一、API 接口更新流程（重点）

本项目使用 `@umijs/openapi` 自动从后端 Swagger 文档生成前端 API 函数，**禁止手写 fetch/axios 请求**。

### 1.1 完整更新步骤

**第一步：确保后端已启动**

后端服务正常运行，Swagger 文档可正常访问。

**第二步：在前端项目根目录执行生成命令**

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

**第三步：在页面中使用生成的 API**

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

```
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

**前端需要实现功能或样式时，优先使用现成组件，不要手动开发。**

| 优先级 | 库 | 适用场景 |
|--------|-----|---------|
| 1（最高） | `@ant-design/x` | AI 对话专用：`Bubble`、`Sender`、`Conversations`、`ThoughtChain` 等 |
| 2 | `Ant Design 5` | 通用 UI：`Button`、`Table`、`Form`、`Modal`、`Select`、`Upload` 等 |
| 3 | `@ant-design/pro-components` | 高级业务组件：`ProTable`、`ProForm`、`ProLayout`、`ProDescriptions` 等 |
| 4 | 社区成熟库 | `react-markdown`（Markdown）、`@monaco-editor/react`（代码编辑器）等 |
| 5（最低） | 手写自定义 | 以上均无法满足时才手动实现 |

### 典型场景对应

| 场景 | 推荐方案 | 禁止做法 |
|------|---------|---------|
| Markdown 渲染 | `react-markdown` | 手写解析器 |
| 流式 AI 回复 | `Bubble`（`streaming` prop） | 手写光标动画 |
| 思维链展示 | `ThoughtChain` | 手写步骤时间轴 |
| 代码高亮 | `CodeHighlighter` 或 `@monaco-editor/react` | 手写高亮 |
| 数据表格（含分页/搜索） | `ProTable` | 手写 Table + 分页组合 |
| 复杂表单 | `ProForm` | 手写 Form + 校验逻辑 |
| 页面布局 | `ProLayout` | 手写导航+侧边栏 |

---

## 五、请求封装规范

所有 API 请求经过 `@/request` 统一封装，生成的函数直接调用即可：

```ts
// 生成的函数签名（自动生成，勿手写）
export async function addItem(
  body: API.ItemAddRequest,
  options?: { [key: string]: any }
): Promise<API.BaseResponseLong>
```

响应结构统一为 `BaseResponse`：

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
|------|------|------|
| 页面组件 | `PascalCase` | `UserList.tsx`, `AgentDetail.tsx` |
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
