"""Exercise actual ASGI routing/validation; no listening server or external services."""

import unittest

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, StreamingResponse
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field, ValidationError

from fastapi_contract import (
    BaseResponse,
    BusinessException,
    ErrorCode,
    ErrorResponse,
    install_error_handlers,
    success,
    throw_if,
)


class UserVO(BaseModel):
    id: int
    name: str


class CreateRequest(BaseModel):
    name: str = Field(min_length=1)
    secret_number: int


class ResponseContractTests(unittest.TestCase):
    def setUp(self):
        self.app = FastAPI(debug=False)
        install_error_handlers(self.app)

        @self.app.get("/users/{user_id}", response_model=BaseResponse[UserVO],
                      responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}})
        def get_user(user_id: int):
            throw_if(user_id == 99, ErrorCode.NOT_FOUND)
            return success(UserVO(id=user_id, name="示例用户"))

        @self.app.post("/users", status_code=201, response_model=BaseResponse[UserVO],
                       responses={422: {"model": ErrorResponse}})
        def create_user(body: CreateRequest, response: Response):
            response.headers["Location"] = "/users/1"
            return success(UserVO(id=1, name=body.name))

        @self.app.get("/false", response_model=BaseResponse[bool])
        def false_result():
            return success(False)

        @self.app.get("/zero", response_model=BaseResponse[int])
        def zero_result():
            return success(0)

        @self.app.get("/empty", response_model=BaseResponse[list[int]])
        def empty_result():
            return success([])

        @self.app.get("/none", response_model=BaseResponse[None])
        def none_result():
            return success(None)

        @self.app.get("/business/{name}")
        def business_error(name: str):
            raise BusinessException(ErrorCode[name])

        @self.app.get("/http/{status}")
        def protocol_error(status: int):
            raise HTTPException(status, detail="secret-token", headers={
                "WWW-Authenticate": "Bearer", "Retry-After": "30", "Allow": "GET",
                "Content-Length": "9999", "Content-Type": "text/plain", "Location": "/users/1",
            })

        @self.app.get("/crash")
        def crash():
            raise RuntimeError("password=secret-token")

        @self.app.get("/bad-response", response_model=BaseResponse[UserVO])
        def bad_response():
            return {"code": 0, "message": "ok", "data": {"id": "secret-token", "name": "x"}}

        @self.app.delete("/no-content", status_code=204)
        def no_content():
            return Response(status_code=204)

        @self.app.get("/download")
        def download():
            return StreamingResponse(iter([b"example file"]), media_type="application/octet-stream")

        self.client = TestClient(self.app, raise_server_exceptions=False)
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)

    def assert_error(self, response, status, code):
        self.assertEqual(response.status_code, status)
        body = response.json()
        self.assertEqual(body["code"], code)
        self.assertIs(type(body["code"]), int)
        self.assertIsNone(body["data"])
        self.assertRegex(body["requestId"], r"^[0-9a-f]{32}$")
        self.assertEqual(body["requestId"], response.headers["X-Request-ID"])
        self.assertNotIn("secret-token", response.text)
        self.assertNotIn("traceback", response.text.lower())

    def test_typed_success_and_created_status(self):
        response = self.client.get("/users/2")
        self.assertEqual(response.json(), {"code": 0, "message": "ok", "data": {"id": 2, "name": "示例用户"}})
        created = self.client.post("/users", json={"name": "new", "secret_number": 1})
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.headers["Location"], "/users/1")
        self.assertEqual(created.json()["code"], 0)

    def test_false_like_values_are_success(self):
        for path, value in (("false", False), ("zero", 0), ("empty", []), ("none", None)):
            with self.subTest(path=path):
                response = self.client.get("/" + path)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["code"], 0)
                self.assertEqual(response.json()["data"], value)

    def test_throw_if_and_business_registration(self):
        self.assertIsNone(throw_if(False, ErrorCode.CONFLICT))
        with self.assertRaises(BusinessException) as caught:
            throw_if(True, ErrorCode.CONFLICT)
        self.assertEqual(caught.exception.error, ErrorCode.CONFLICT)
        with self.assertRaises(TypeError):
            BusinessException(0)
        self.assert_error(self.client.get("/users/99"), 404, 40400)

    def test_business_errors_preserve_http_semantics(self):
        for name, status, code in (("INVALID_ARGUMENT", 400, 40000), ("UNAUTHENTICATED", 401, 40100),
                                   ("FORBIDDEN", 403, 40300), ("CONFLICT", 409, 40900)):
            with self.subTest(name=name):
                self.assert_error(self.client.get("/business/" + name), status, code)

    def test_input_errors_do_not_echo_body_or_value(self):
        response = self.client.post("/users", json={"name": "user", "secret_number": "secret-token"})
        self.assert_error(response, 422, 42200)
        self.assertNotIn("secret_number", response.text)
        self.assert_error(self.client.get("/users/secret-token"), 422, 42200)

    def test_malformed_json_is_validation_failure(self):
        self.assert_error(self.client.post("/users", content='{"secret-token":',
                                           headers={"Content-Type": "application/json"}), 422, 42200)

    def test_router_errors_and_allow_header(self):
        self.assert_error(self.client.get("/missing"), 404, 40400)
        response = self.client.put("/users/2")
        self.assert_error(response, 405, 40500)
        self.assertIn("GET", response.headers["Allow"])

    def test_http_exception_headers_and_unknown_error_status(self):
        for status in (401, 429, 410):
            with self.subTest(status=status):
                response = self.client.get(f"/http/{status}")
                self.assert_error(response, status, status * 100)
                self.assertEqual(response.headers["WWW-Authenticate"], "Bearer")
                self.assertEqual(response.headers["Retry-After"], "30")
                self.assertEqual(response.headers["Content-Type"], "application/json")
                self.assertNotEqual(response.headers["Content-Length"], "9999")

    def test_unknown_error_is_safe_and_correlated_in_log(self):
        with self.assertLogs("fastapi_contract", level="ERROR") as logs:
            response = self.client.get("/crash", headers={"X-Request-ID": "secret-token"})
        self.assert_error(response, 500, 50000)
        joined = "\n".join(logs.output)
        self.assertIn(response.json()["requestId"], joined)
        self.assertIn("RuntimeError", joined)
        self.assertNotIn("secret-token", joined)

    def test_invalid_output_is_server_error_not_request_error(self):
        with self.assertLogs("fastapi_contract", level="ERROR"):
            response = self.client.get("/bad-response")
        self.assert_error(response, 500, 50000)

    def test_server_business_error_and_http_error_are_not_success(self):
        with self.assertLogs("fastapi_contract", level="ERROR"):
            self.assert_error(self.client.get("/business/UNAVAILABLE"), 503, 50300)
            self.assert_error(self.client.get("/http/502"), 502, 50200)

    def test_non_json_and_bodyless_responses_are_not_wrapped(self):
        response = self.client.delete("/no-content")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.content, b"")
        head = self.client.head("/missing")
        self.assertEqual(head.status_code, 404)
        self.assertEqual(head.content, b"")
        self.assertEqual(self.client.get("/download").content, b"example file")

    def test_redirect_protocol_is_preserved(self):
        # Test a normal framework redirect without irrelevant entity headers.
        @self.app.get("/redirect")
        def redirect():
            raise HTTPException(307, headers={"Location": "/users/1"})

        response = self.client.get("/redirect", follow_redirects=False)
        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["Location"], "/users/1")
        self.assertEqual(response.content, b"")

    def test_openapi_describes_actual_success_and_validation_envelopes(self):
        schema = self.client.get("/openapi.json").json()
        responses = schema["paths"]["/users"]["post"]["responses"]
        error_ref = responses["422"]["content"]["application/json"]["schema"]["$ref"]
        self.assertTrue(error_ref.endswith("/ErrorResponse"))
        success_ref = responses["201"]["content"]["application/json"]["schema"]["$ref"]
        model = schema["components"]["schemas"][success_ref.rsplit("/", 1)[-1]]
        self.assertEqual(model["properties"]["code"]["const"], 0)
        self.assertEqual(model["properties"]["data"]["$ref"], "#/components/schemas/UserVO")

    def test_error_response_rejects_zero_and_debug_is_rejected(self):
        for code in (0, -1, "40000", True):
            with self.subTest(code=code), self.assertRaises(ValidationError):
                ErrorResponse(code=code, message="error", requestId="request-id")
        with self.assertRaises(ValueError):
            install_error_handlers(FastAPI(debug=True))


if __name__ == "__main__":
    unittest.main()
