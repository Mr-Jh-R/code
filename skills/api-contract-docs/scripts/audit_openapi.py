"""只读检查OpenAPI与Markdown；输出核对线索，不判定线上实现是否正确。"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re

METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
ROUTE = re.compile(
    r"\b(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS|TRACE)\b[`| \t]+"
    r"(/[^\s`\"'|<>]+)"
)
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def normalize(path, base_path):
    path = path.split("?", 1)[0].split("#", 1)[0].rstrip(".,;，。；")
    base = base_path.rstrip("/")
    if base and (path == base or path.startswith(base + "/")):
        path = path[len(base):] or "/"
    return path


def canonical(path):
    return re.sub(r"\{[^{}]+\}", "{}", path)


def matches(template, path):
    # 文档中的具体ID示例也能对应路由模板，但不会替代字段核对。
    fragments = re.split(r"(\{[^{}]+\})", template)
    pattern = "".join("[^/]+" if s.startswith("{") else re.escape(s) for s in fragments)
    return canonical(template) == canonical(path) or re.fullmatch(pattern, path) is not None


def resolve(schema, document):
    seen = set()
    while isinstance(schema, dict) and "$ref" in schema:
        ref = schema["$ref"]
        if ref in seen or not ref.startswith("#/"):
            return {}
        seen.add(ref)
        node = document
        for part in ref[2:].split("/"):
            node = node.get(part.replace("~1", "/").replace("~0", "~"), {})
            if not isinstance(node, dict):
                return {}
        schema = node
    return schema if isinstance(schema, dict) else {}


def open_shapes(schema, document, prefix="response", depth=0):
    if depth > 6:
        return []
    schema = resolve(schema, document)
    if not schema:
        return [prefix]
    props = schema.get("properties", {})
    additional = schema.get("additionalProperties", False)
    result = []
    if additional is True or additional == {} or (
        schema.get("type") == "object" and not props and "additionalProperties" not in schema
    ):
        result.append(prefix)
    for name, child in props.items():
        result.extend(open_shapes(child, document, prefix + "." + name, depth + 1))
    if "items" in schema:
        result.extend(open_shapes(schema["items"], document, prefix + "[]", depth + 1))
    return result


def binary_schema(schema, document, depth=0):
    if depth > 12:
        return False
    schema = resolve(schema, document)
    return schema.get("format") == "binary" or any(
        binary_schema(child, document, depth + 1)
        for child in list(schema.get("properties", {}).values()) + [schema.get("items", {})]
        if child
    )


def markdown_checks(markdown):
    examples, errors, anchors, outside = 0, [], [], []
    fence, language, start, content = None, "", 0, []
    for number, line in enumerate(markdown.splitlines(), 1):
        marker = FENCE.match(line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                if language == "json":
                    examples += 1
                    try:
                        json.loads("\n".join(content))
                    except json.JSONDecodeError as error:
                        errors.append({"line": start + error.lineno, "message": error.msg})
                fence, content = None, []
            else:
                content.append(line)
        elif marker:
            fence = marker[1]
            language = marker[2].strip().split(" ", 1)[0].lower()
            start = number
        else:
            outside.append(line)
    if fence and language == "json":
        errors.append({"line": start, "message": "JSON代码块未闭合"})
    for match in re.finditer(r'<a\s+id=["\']([^"\']+)["\']', "\n".join(outside)):
        anchors.append(match[1])
    return {
        "json_examples": examples,
        "json_errors": errors,
        "duplicate_explicit_anchors": sorted(a for a, n in Counter(anchors).items() if n > 1),
    }


def audit(document, markdown, prefixes=(), base_path=""):
    if not isinstance(document, dict) or not str(document.get("openapi", "")).startswith("3.") or not isinstance(document.get("paths"), dict):
        raise ValueError("需要包含paths的OpenAPI 3.x JSON文件")
    in_scope = lambda path: not prefixes or any(path == p.rstrip("/") or path.startswith(p.rstrip("/") + "/") for p in prefixes)
    operations = []
    for path, item in document["paths"].items():
        path = normalize(path, base_path)
        if in_scope(path):
            operations.extend((method.upper(), path, value) for method, value in item.items() if method in METHODS)
    declared = [(m[1], normalize(m[2], base_path)) for m in ROUTE.finditer(markdown)]
    missing, documented = [], 0
    loose, uploads = [], []
    for method, path, operation in operations:
        key = method + " " + path
        if any(method == dm and matches(path, dp) for dm, dp in declared):
            documented += 1
        else:
            missing.append(key)
        uncertain = set()
        for status, response in operation.get("responses", {}).items():
            if not str(status).startswith("2"):
                continue
            response = resolve(response, document)
            for media, body in response.get("content", {}).items():
                if media == "*/*" or "json" in media:
                    uncertain.update(open_shapes(body.get("schema", {}), document))
        if uncertain:
            loose.append({"operation": key, "untyped_paths": sorted(uncertain)})
        request = resolve(operation.get("requestBody", {}), document)
        for media, body in request.get("content", {}).items():
            if "json" in media and binary_schema(body.get("schema", {}), document):
                uploads.append({"operation": key, "content_type": media})
    only_document = sorted({dm + " " + dp for dm, dp in declared if in_scope(dp) and not any(dm == m and matches(p, dp) for m, p, _ in operations)})
    return {
        "note": "以下为机械核对线索；相对路径、否定语句、隐藏路由和版本差异需人工确认。未验证业务约束或字段语义。",
        "scope_prefixes": list(prefixes),
        "operation_count": len(operations),
        "operations_mentioned": documented,
        "missing_documentation_candidates": sorted(missing),
        "document_only_candidates": only_document,
        "untyped_success_responses": loose,
        "json_binary_request_candidates": uploads,
        **markdown_checks(markdown),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--openapi", required=True, type=Path)
    parser.add_argument("--document", required=True, type=Path)
    parser.add_argument("--include-prefix", action="append", default=[])
    parser.add_argument("--base-path", default="")
    args = parser.parse_args()
    try:
        document = json.loads(args.openapi.read_text(encoding="utf-8-sig"))
        markdown = args.document.read_text(encoding="utf-8-sig")
        result = audit(document, markdown, args.include_prefix, args.base_path)
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
