"""Numeric JSON response contract for FastAPI + Pydantic v2, Python 3.10+.

Call install_error_handlers(app) once before serving requests. This module creates
no app, routes, background tasks or external connections at import time.
"""

from collections.abc import Awaitable, Callable
from enum import IntEnum
import logging
import traceback
from typing import Generic, Literal, TypeVar
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, Response

T = TypeVar("T")
logger = logging.getLogger(__name__)


class BaseResponse(BaseModel, Generic[T]):
    """Successful JSON response; false-like data is still a success."""

    code: Literal[0] = 0
    message: str = "ok"
    data: T


class ErrorResponse(BaseModel):
    """Error envelope, with no application data or raw exception details."""

    code: int = Field(gt=0, strict=True)
    message: str
    data: None = None
    request_id: str = Field(alias="requestId")


class ErrorCode(IntEnum):
    INVALID_ARGUMENT = 40000
    UNAUTHENTICATED = 40100
    FORBIDDEN = 40300
    NOT_FOUND = 40400
    METHOD_NOT_ALLOWED = 40500
    CONFLICT = 40900
    PAYLOAD_TOO_LARGE = 41300
    UNSUPPORTED_MEDIA_TYPE = 41500
    VALIDATION_ERROR = 42200
    RATE_LIMITED = 42900
    INTERNAL_ERROR = 50000
    BAD_GATEWAY = 50200
    UNAVAILABLE = 50300
    GATEWAY_TIMEOUT = 50400


# HTTP adapters own this mapping; business code only raises registered errors.
ERRORS: dict[ErrorCode, tuple[int, str]] = {
    ErrorCode.INVALID_ARGUMENT: (400, "请求参数不合法"),
    ErrorCode.UNAUTHENTICATED: (401, "请先认证"),
    ErrorCode.FORBIDDEN: (403, "无权执行此操作"),
    ErrorCode.NOT_FOUND: (404, "资源不存在"),
    ErrorCode.METHOD_NOT_ALLOWED: (405, "请求方法不支持"),
    ErrorCode.CONFLICT: (409, "版本或状态冲突"),
    ErrorCode.PAYLOAD_TOO_LARGE: (413, "请求内容过大"),
    ErrorCode.UNSUPPORTED_MEDIA_TYPE: (415, "请求媒体类型不支持"),
    ErrorCode.VALIDATION_ERROR: (422, "请求参数校验失败"),
    ErrorCode.RATE_LIMITED: (429, "请求过于频繁"),
    ErrorCode.INTERNAL_ERROR: (500, "系统内部错误"),
    ErrorCode.BAD_GATEWAY: (502, "上游服务响应异常"),
    ErrorCode.UNAVAILABLE: (503, "服务暂时不可用"),
    ErrorCode.GATEWAY_TIMEOUT: (504, "上游服务超时"),
}

# Reserve HTTP status * 100 for protocol errors, including uncommon 4xx/5xx.
# Domain-specific codes must use separately registered non-colliding values.
HTTP_ERRORS: dict[int, tuple[int, str]] = {
    status: (status * 100, "请求失败" if status < 500 else "服务暂时不可用")
    for status in range(400, 600)
}
HTTP_ERRORS.update({status: (int(code), message) for code, (status, message) in ERRORS.items()})


class BusinessException(Exception):
    """A registered business failure; arbitrary public messages are not accepted."""

    def __init__(self, error: ErrorCode):
        if not isinstance(error, ErrorCode):
            raise TypeError("BusinessException requires a registered ErrorCode")
        self.error = error
        super().__init__(error.name)


def throw_if(condition: bool, error: ErrorCode) -> None:
    """Raise when the guard is true; callers retain explicit domain validation."""
    if condition:
        raise BusinessException(error)


def success(data: T) -> BaseResponse[T]:
    """Preserve payload; the route's concrete response_model validates its type."""
    return BaseResponse[T](data=data)


def _request_id(request: Request) -> str:
    value = getattr(request.state, "contract_request_id", None)
    if value is None:
        value = uuid4().hex
        request.state.contract_request_id = value
    return value


def _log_failure(request: Request, exc: Exception) -> None:
    # Retain stack locations, but not exception text, request values or locals.
    frames = [(f.filename, f.lineno, f.name) for f in traceback.extract_tb(exc.__traceback__)]
    logger.error("request_id=%s exception=%s frames=%s", _request_id(request), type(exc).__name__, frames)


def _error_response(
    request: Request,
    status: int,
    code: int,
    message: str,
    headers: dict[str, str] | None = None,
) -> Response:
    response_headers = dict(headers or {})
    response_headers["X-Request-ID"] = _request_id(request)
    if request.method == "HEAD":
        return Response(status_code=status, headers=response_headers)
    body = ErrorResponse(code=code, message=message, requestId=_request_id(request))
    return JSONResponse(status_code=status, content=body.model_dump(mode="json", by_alias=True), headers=response_headers)


def install_error_handlers(app: FastAPI) -> None:
    """Register the production error contract; no business endpoints are added."""
    if app.debug:
        raise ValueError("The safe error contract requires debug=False")

    @app.middleware("http")
    async def correlate_request(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        request.state.contract_request_id = uuid4().hex  # Never trust a raw client header.
        response = await call_next(request)
        response.headers["X-Request-ID"] = _request_id(request)
        return response

    @app.exception_handler(BusinessException)
    async def business_error(request: Request, exc: BusinessException) -> Response:
        status, message = ERRORS[exc.error]
        if status >= 500:
            _log_failure(request, exc)
        return _error_response(request, status, int(exc.error), message)

    @app.exception_handler(RequestValidationError)
    async def request_error(request: Request, exc: RequestValidationError) -> Response:
        # exc.body and exc.errors() can include passwords, input and validator ctx.
        status, message = ERRORS[ErrorCode.VALIDATION_ERROR]
        return _error_response(request, status, int(ErrorCode.VALIDATION_ERROR), message)

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> Response:
        if 100 <= exc.status_code < 400:
            return Response(status_code=exc.status_code, headers=exc.headers)
        code, message = HTTP_ERRORS.get(exc.status_code, HTTP_ERRORS[500])
        status = exc.status_code if exc.status_code in HTTP_ERRORS else 500
        headers = {k: v for k, v in (exc.headers or {}).items()
                   if k.lower() in {"allow", "www-authenticate", "retry-after"}}
        if status >= 500:
            _log_failure(request, exc)
        return _error_response(request, status, code, message, headers)

    async def server_error(request: Request, exc: Exception) -> Response:
        _log_failure(request, exc)
        status, message = ERRORS[ErrorCode.INTERNAL_ERROR]
        return _error_response(request, status, int(ErrorCode.INTERNAL_ERROR), message)

    app.add_exception_handler(ResponseValidationError, server_error)
    app.add_exception_handler(Exception, server_error)
