"""MCP Sentinel package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mcp-sentinel")
except PackageNotFoundError:  # pragma: no cover - source tree without installation
    __version__ = "0.1.0"

__all__ = ["__version__"]
