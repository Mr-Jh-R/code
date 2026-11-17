# FastAPI 后端附录

> 仅在项目采用 FastAPI 时读取，先读 [Python 附录](../languages/python.md)。本文示例基于 Python 3.10+、Pydantic v2；版本以项目依赖为准，不自动迁移已有 Pydantic v1 项目。

## 一、请求、成功响应与错误契约

- 请求 DTO 使用明确的 Pydantic 模型与字段约束，按业务决定严格类型、额外字段策略及部分更新语义；`TypedDict` 或 Python 注解不能替代校验。
- 普通 JSON 业务接口声明具体 `response_model=BaseResponse[UserVO]`，成功由 `success(data)` 构建，整数 `code=0`。不同用途的请求/响应模型分离，限制公开字段。
- 创建接口同时声明 201 和需要的 `Location`；异步受理声明 202 及查询入口。JSON success helper 不负责选择 HTTP 状态。
- 使用路由/应用级异常处理器转换失败，业务调用 `throw_if(...)` 或抛出自定义异常；路由不复制 try/catch 包装错误。
- Pydantic v2 使用 `BaseModel` + `Generic[T]`，JSON 编码使用框架序列化或 `model_dump(mode="json")`；不能把仍含 datetime、Decimal 等对象的普通 dump 直接交给 JSONResponse。
- OpenAPI 的错误响应模型与实际处理器一致，不能保留默认 422 的 `detail` 文档却返回另一种错误体。字段校验、成功模型和错误模型需要实际请求测试。

## 二、全局异常处理

接入示例（假定参考模块已放入项目可导入的包中；实际导入路径遵循项目布局）：

```python
from fastapi import FastAPI
from pydantic import BaseModel

from fastapi_contract import (
    BaseResponse, ErrorCode, ErrorResponse, install_error_handlers, success, throw_if,
)

app = FastAPI(debug=False)
install_error_handlers(app)


class NumberVO(BaseModel):
    value: int


@app.get(
    "/numbers/{value}",
    response_model=BaseResponse[NumberVO],
    responses={400: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def read_number(value: int) -> BaseResponse[NumberVO]:
    throw_if(value < 0, ErrorCode.INVALID_ARGUMENT)
    return success(NumberVO(value=value))
```

应用还应通过共享 `responses` 配置或路由声明补齐实际可能出现的认证、授权、500 等错误；注册异常处理器不会自动修正所有 OpenAPI 响应声明。

| 异常 | 转换责任 |
| --- | --- |
| `BusinessException` | 按登记业务码映射真实 4xx/5xx 和安全消息，失败 `data=null` |
| `RequestValidationError` | 按项目约定返回 422 或明确声明的 400；参考实现为 422/42200，不返回原始 body、input 或校验 ctx |
| Starlette `HTTPException` | 覆盖路由 404/405 与 FastAPI HTTPException，保留 HTTP 状态和必要的 Allow、WWW-Authenticate、Retry-After 等响应头 |
| `ResponseValidationError` | 当作服务端契约错误返回 500/50000，原始响应内容不暴露给调用方 |
| 其他 `Exception` | 返回 500/50000 与固定消息，记录请求标识和受控堆栈，不以 `str(exc)` 生成客户端消息 |

- 业务错误消息来自枚举/登记模板；HTTPException 的任意 `detail` 不直接原样透传。需要字段错误详情时只暴露允许的字段路径、错误类型和安全文案，不序列化整个 `errors()`。
- 关联标识由服务端生成或校验可信上游标识，错误响应与日志一致；不能把任意请求头直接回显到日志/响应。
- 生产 `debug=False`，否则调试页可能绕过安全的 500 输出。异常处理器自身也须保持简单、可序列化，不能在错误路径引入远程依赖。
- 异常处理并非覆盖所有失败：HTTP middleware 的拒绝按该 middleware 的响应契约处理；进程启动、WebSocket、后台任务和已发送的流不能依赖普通 HTTP 异常处理器补救。
- HTTPException 的非错误状态按实际协议处理，HEAD/204 保持空 body。文件/流不强制套响应体。

## 三、依赖、生命周期与事务

- `Depends` 用于协议入口组合配置、身份、客户端和 Session；核心业务接收明确参数或依赖对象，避免依赖 `Request`、全局容器查找或运行中的 HTTP 会话。
- 使用 lifespan/依赖清理管理连接池和共享客户端，按框架版本确认 yield 依赖的退出时机；流式响应期间的资源生命周期需单独验证。
- 写入事务在用例返回成功前完成 commit/rollback，不把关键 commit 放在响应可能已经发出后的清理阶段；捕获异常后不能继续提交部分失败数据。
- 采用 SQLAlchemy 时，`Session` 按线程、`AsyncSession` 按任务隔离，不在 `gather` 并行任务中共享同一个 Session；这不要求未使用 SQLAlchemy 的项目安装它。
- 数据库事务内不等待外部 API/模型调用，使用已确认的超时、幂等与跨系统一致性策略。

## 四、同步、异步与验证

- 框架调用的普通 `def` 路由/依赖可以被调度到线程池；在 `async def` 中直接调用的同步辅助函数不会自动卸载。按调用链选择异步库或受控卸载。
- 异常处理器若没有阻塞操作可使用 async；处理器里不发送消息、写业务数据或无限重试。
- 测试生产式 HTTP 响应时使用 `TestClient(..., raise_server_exceptions=False)`；其他测试可保留异常直接抛出来定位根因。使用上下文管理器运行 lifespan。
- 用 [参考实现](../examples/python/fastapi_contract.py) 和 [契约测试](../examples/python/test_fastapi_contract.py) 了解行为。示例不连接数据库或网络，也不自动注册业务路由；项目必须补自己的权限、事务与接口测试。

示例依赖位于 [requirements.txt](../examples/python/requirements.txt)，仅用于独立示例环境；目标项目依赖以已有 lockfile 和版本策略为准。先在隔离环境安装依赖，再在本规范仓库根运行：

```bash
python -m pip install -r conventions/backend/examples/python/requirements.txt
python -B -m unittest discover -s conventions/backend/examples/python -p "test_*.py"
```

## 参考

- [FastAPI 错误处理](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [FastAPI 响应模型](https://fastapi.tiangolo.com/tutorial/response-model/)
- [FastAPI 异步](https://fastapi.tiangolo.com/async/)
- [FastAPI lifespan](https://fastapi.tiangolo.com/advanced/events/)
- [Pydantic 泛型模型](https://docs.pydantic.dev/latest/concepts/models/#generic-models)
- [Starlette 异常](https://www.starlette.io/exceptions/)
- [SQLAlchemy Session](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
