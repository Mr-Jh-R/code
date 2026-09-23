"""覆盖影响文档审查结论的边界，不连接服务或创建业务数据。"""

import unittest

from audit_openapi import audit


def spec(paths, schemas=None):
    return {"openapi": "3.1.0", "paths": paths, "components": {"schemas": schemas or {}}}


class AuditTests(unittest.TestCase):
    def test_methods_alias_names_and_concrete_examples(self):
        doc = "| `GET` | `/tasks/{taskId}` | 查询 |\nPOST /tasks/12/retry\n"
        result = audit(spec({"/tasks/{id}": {"get": {}, "delete": {}}, "/tasks/{id}/retry": {"post": {}}}), doc)
        self.assertEqual(result["operations_mentioned"], 2)
        self.assertEqual(result["missing_documentation_candidates"], ["DELETE /tasks/{id}"])
        self.assertEqual(result["document_only_candidates"], [])

    def test_explicit_scope_and_context_prefix(self):
        data = spec({"/app/tasks": {"get": {}}, "/health": {"get": {}}})
        result = audit(data, "GET /api/app/tasks?pageNo=1\nGET /health", ["/app"], "/api")
        self.assertEqual(result["operation_count"], 1)
        self.assertEqual(result["operations_mentioned"], 1)
        self.assertEqual(result["document_only_candidates"], [])

    def test_different_methods_and_unpublished_paths_remain_visible(self):
        result = audit(spec({"/tasks": {"get": {}}}), "POST /tasks\nGET /knowledge-document")
        self.assertEqual(result["missing_documentation_candidates"], ["GET /tasks"])
        self.assertEqual(result["document_only_candidates"], ["GET /knowledge-document", "POST /tasks"])

    def test_upload_and_object_response_are_flagged_through_refs(self):
        data = spec({"/upload": {"post": {
            "requestBody": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Upload"}}}},
            "responses": {"200": {"content": {"application/json": {"schema": {"$ref": "#/components/schemas/Result"}}}}}
        }}}, {
            "Upload": {"type": "object", "properties": {"file": {"type": "string", "format": "binary"}}},
            "Result": {"type": "object", "properties": {"data": {"type": "object", "additionalProperties": True}}}
        })
        result = audit(data, "POST /upload")
        self.assertEqual(result["json_binary_request_candidates"], [{"operation": "POST /upload", "content_type": "application/json"}])
        self.assertEqual(result["untyped_success_responses"][0]["untyped_paths"], ["response.data"])

    def test_typed_json_and_binary_download_are_not_marked_untyped(self):
        data = spec({"/tasks": {"get": {"responses": {"200": {"content": {"application/json": {"schema": {"type": "array", "items": {"type": "object", "properties": {"id": {"type": "integer"}}}}}}}}}}, "/download": {"get": {"responses": {"200": {"content": {"application/octet-stream": {"schema": {"type": "string", "format": "binary"}}}}}}}})
        self.assertEqual(audit(data, "GET /tasks\nGET /download")["untyped_success_responses"], [])

    def test_json_fences_and_duplicate_anchors(self):
        text = '<a id="same"></a>\n<a id="same"></a>\n```json\n{"ok":true}\n```\n```json\n{"bad":}\n```\n````text\n```json\ninvalid\n```\n````'
        result = audit(spec({}), text)
        self.assertEqual(result["json_examples"], 2)
        self.assertEqual(len(result["json_errors"]), 1)
        self.assertEqual(result["json_errors"][0]["line"], 7)
        self.assertEqual(result["duplicate_explicit_anchors"], ["same"])

    def test_unclosed_json_is_reported(self):
        result = audit(spec({}), '~~~json\n{"id":1}')
        self.assertEqual(result["json_errors"][0]["line"], 1)

    def test_rejects_non_openapi_input(self):
        for value in ({"code": 0, "data": {}}, [], None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                audit(value, "GET /tasks")


if __name__ == "__main__":
    unittest.main()
