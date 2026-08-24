# Vue 前端代码规范

本规范适用于 Vue 3、Vue Router、Pinia、Nuxt（Vue）和 Vue + Vite 项目。它与 [`frontend-conventions-react.md`](./frontend-conventions-react.md) 分开维护；请根据目标包的 `package.json` 选择，不要混用。

## 一、技术栈与版本策略

- 先读取项目的 `package.json`、lockfile、workspace 配置和现有脚手架。
- 优先遵守项目已有依赖及 peer dependency 约束。
- 新项目使用当前稳定、兼容、社区推荐的 Vue 生态版本；本规范不把 Vue、Vue Router、Pinia 或构建工具永久固定为某个版本号。
- 升级依赖前，确认 Vue、Vue Router、Pinia、Nuxt/Vite、TypeScript 和 UI 库的兼容性，并运行项目验证命令。
- 需要可复现构建时提交 lockfile；不要为了“格式统一”擅自替换项目的包管理器或升级整套依赖。

## 二、项目结构

推荐按业务边界组织目录，实际命名以项目现有约定为准：

```text
src/
├── api/                 # API 客户端和 DTO 类型
├── assets/              # 静态资源
├── components/          # 跨页面复用组件
├── composables/         # 可复用的组合式逻辑（useXxx）
├── layouts/             # 布局组件（如项目使用）
├── pages/               # 路由页面（如文件路由方案使用）
├── router/              # Vue Router 实例、路由表和守卫
├── stores/              # Pinia stores
├── types/               # 共享类型
├── utils/               # 无状态工具函数
├── App.vue
└── main.ts
```

不要为了追求目录模板而移动已有模块；新增代码应放在最接近其业务边界的位置。

## 三、组件与组合式 API

- 新项目优先使用 `<script setup lang="ts">`；已有项目先确认 Vue 版本和现有组件风格，继续使用兼容的 Composition API 或 Options API，不为统一写法强制升级。
- 组件名使用 `PascalCase`，文件名与组件名保持一致，例如 `UserTable.vue`。
- 组合式函数使用 `useXxx` 命名，并保持单一职责；不要把页面生命周期、请求、缓存和表单校验无边界地塞进一个 composable。
- `ref`、`computed`、`reactive` 和 `watch` 应按最小必要范围使用。能用 `computed` 表达的派生值不要复制成可变状态。
- 组件通过明确的 `props`、`emits` 和 slots 通信；不要依赖跨层级隐式修改父组件状态。
- 对复杂 props 和 emits 使用 TypeScript 类型，避免 `any` 和无类型的事件透传。

```vue
<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  userId: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  (event: 'saved', userId: string): void
}>()

const displayId = computed(() => props.userId.trim())
</script>

<template>
  <button type="button" @click="emit('saved', displayId)">
    保存
  </button>
</template>
```

## 四、路由

- 路由集中维护在 `router/` 或项目既有路由目录，页面组件不直接创建全局 router 实例。
- 路由名称、参数和元信息使用稳定、可读的命名；权限、登录和页面标题等横切逻辑通过路由守卫或统一插件处理。
- 导航优先使用 `RouterLink`、`router.push`、`router.replace`，不要手写 `window.location` 破坏 SPA 状态。
- 路由懒加载按页面或业务边界拆分，并在需要时设置清晰的 loading、错误和未找到页面。

## 五、Pinia 状态管理

- 只有跨组件、跨页面或需要持久化的状态才放入 Pinia；局部交互状态留在组件或 composable 内。
- Store 使用 `defineStore`，按业务域命名，例如 `useAuthStore`、`useCartStore`。
- 将服务端数据缓存和 UI 状态区分开；请求、错误、加载状态应有明确字段，不用“空数组”同时表示未加载和加载失败。
- Store action 负责业务操作和状态更新，组件只编排交互，不复制 store 内部规则。
- 持久化前评估敏感信息、过期策略、跨标签页同步和 SSR 安全性；不要默认把 token 或个人数据写入 localStorage。

## 六、API 与异步请求

- 优先使用项目已有的 API 客户端、OpenAPI 生成代码或 request 封装，不在页面里重复创建 fetch/axios 实例。
- API 类型从生成模块或共享类型导入，避免手写与后端不一致的响应结构。
- 为请求定义 loading、成功、空数据、失败和取消/竞态状态；组件卸载后不要提交过期结果。
- 统一处理认证失效、网络错误和业务错误；用户可见提示与日志记录分离。
- 不要在模板中直接发起副作用请求；在 composable、store 或生命周期中管理，并确保依赖明确。

## 七、表单、列表与性能

- 表单校验规则与提交逻辑集中管理，提交按钮在请求期间应有明确的禁用或 loading 状态。
- 列表必须处理加载中、空状态、错误、分页/无限滚动和重复提交等情况。
- 长列表使用虚拟化或分页；避免在模板中重复执行昂贵计算。
- 只有在有测量依据时使用 `v-memo`、组件缓存或手动优化；先保持组件边界清晰，再处理性能瓶颈。

## 八、样式与可访问性

- 遵循项目已有 CSS 方案（Scoped CSS、CSS Modules、Tailwind 或 UI 库），不要在同一模块混用多个体系。
- 组件样式默认局部化，公共 token 和主题变量集中维护。
- 交互控件使用语义化 HTML、可见焦点、键盘操作和合适的 aria 属性；图标按钮提供可访问名称。
- 响应式布局覆盖项目支持的最小和最大视口，文本、表单和错误提示不得溢出或互相遮挡。

## 九、验证清单

提交前至少运行项目已有的格式化、类型检查、lint、单元测试和构建命令。针对 Vue 代码重点确认：

- 组件 props/emits、composable 和 store 的类型检查通过；
- 路由守卫、刷新直达、权限失败和 404 行为符合预期；
- API 加载、空数据、失败、重复提交和组件卸载竞态已验证；
- 关键页面在桌面和移动视口没有布局溢出；
- 依赖版本与 lockfile、peer dependency 和项目运行时保持兼容。
