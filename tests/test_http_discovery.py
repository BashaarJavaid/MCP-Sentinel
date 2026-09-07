"""HTTP inventory uses actual registrations and rejects replaced bindings."""

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
