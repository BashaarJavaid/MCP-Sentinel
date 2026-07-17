"""Sentinel domain error taxonomy and exit-code ownership."""


class SentinelError(Exception):
    """Base class for expected Sentinel failures."""


class UsageError(SentinelError):
    """Invalid user input, target, or configuration (exit code 2)."""


class InfrastructureError(SentinelError):
    """Sentinel infrastructure or internal failure (exit code 3)."""
