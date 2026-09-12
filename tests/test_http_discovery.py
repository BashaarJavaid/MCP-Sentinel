"""HTTP inventory uses actual registrations and rejects replaced bindings."""

import ast

import pytest

from sentinel.static.http_discovery import handlers
from tests.test_python_discovery import program


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "from fastapi import FastAPI\napp = FastAPI()\n"
            "@app.get('/data')\ndef fetch(request): return request\n",
            1,
        ),
        (
            "from fastapi import FastAPI\nFastAPI = custom\napp = FastAPI()\n"
            "@app.get('/data')\ndef fetch(request): return request\n",
            0,
        ),
        (
            "from fastapi import FastAPI\napp = FastAPI()\n"
            "def configure(app):\n"
            "    @app.get('/data')\n    def fetch(request): return request\n",
            0,
        ),
        (
            "from fastapi import FastAPI\napp = FastAPI()\napp = custom\n"
            "@app.get('/data')\ndef fetch(request): return request\n",
            0,
        ),
    ],
)
def test_source_establishes_http_application(source: str, expected: int) -> None:
    assert len(handlers(program({"server.py": source}))) == expected


def test_registered_imported_callback_and_middleware_parameters() -> None:
    index = program(
        {
            "server.py": (
                "from starlette.routing import Route\n"
                "from starlette.middleware import Middleware\n"
                "from helpers import fetch, Headers\n"
                "routes = [Route('/data', endpoint=fetch)]\n"
                "middleware = [Middleware(Headers)]\n"
            ),
            "helpers.py": (
                "from starlette.middleware.base import BaseHTTPMiddleware\n"
                "def fetch(request): return request\n"
                "class Headers(BaseHTTPMiddleware):\n"
                "    async def dispatch(self, request, call_next):\n"
                "        return await call_next(request)\n"
            ),
        }
    )
    bindings = handlers(index)
    assert [
        (
            binding.handler.name,
            tuple(p.arg for p in binding.caller_parameters),
            binding.continuation,
        )
        for binding in bindings
    ] == [
        ("fetch", ("request",), None),
        ("Headers.dispatch", ("request",), "call_next"),
    ]


@pytest.mark.parametrize(
    "parameter",
    [
        "token: str = Depends(operator_token)",
        'token: Annotated[str, Depends(operator_token)] = ""',
    ],
)
def test_dependency_injection_is_not_a_caller_parameter(parameter: str) -> None:
    index = program(
        {
            "server.py": "from fastapi import FastAPI, Depends\n"
            "from typing import Annotated\n"
            'app=FastAPI()\ndef operator_token(): return "operator"\n'
            f'@app.get("/fetch")\ndef fetch(url: str, {parameter}): return url\n'
        }
    )
    assert [[p.arg for p in entry.caller_parameters] for entry in handlers(index)] == [
        ["url"]
    ]


def test_unrelated_calls_do_not_repeat_scope_discovery() -> None:
    from unittest.mock import patch

    from sentinel.static import http_discovery

    index = program(
        {
            "server.py": "from fastapi import FastAPI\napp=FastAPI()\n"
            '@app.get("/data")\ndef fetch(request):\n'
            "    result = transform(request)\n    log(result)\n    return result\n"
        }
    )
    with patch.object(
        http_discovery, "shadowed", wraps=http_discovery.shadowed
    ) as shadow:
        assert len(handlers(index)) == 1
        assert shadow.call_count == 1


def test_shadow_lookup_keeps_source_and_deadline_boundaries() -> None:
    from sentinel.errors import InfrastructureError
    from sentinel.static.http_discovery import shadowed

    for parameters, expected in (("app", True), ("", False)):
        index = program({"server.py": f"def serve({parameters}):\n    app.run()\n"})
        call = next(
            node for node in ast.walk(index.files[0].tree) if isinstance(node, ast.Call)
        )
        assert shadowed(index, call, "app") is expected
        assert shadowed(index, call, "app") is expected
        index.deadline = 0
        with pytest.raises(InfrastructureError, match="timeout"):
            shadowed(index, call, "app")
