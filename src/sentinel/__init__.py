"""MCP Sentinel package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("portunusmcp-sentinel")
except PackageNotFoundError:  # pragma: no cover - source tree without installation
    __version__ = "1.2.0"

__all__ = ["__version__"]
