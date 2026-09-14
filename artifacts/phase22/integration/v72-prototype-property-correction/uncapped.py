"""Explicit experiment-only deadline overrides; finite cleanup waits are unchanged."""
from contextlib import ExitStack, contextmanager
import math
import subprocess
from unittest.mock import patch


@contextmanager
def unlimited_waits():
    original_run, original_wait = subprocess.run, subprocess.Popen.wait

    def run(*args, **kwargs):
        if kwargs.get('timeout') == math.inf:
            kwargs['timeout'] = None
        return original_run(*args, **kwargs)

    def wait(process, timeout=None):
        return original_wait(process, timeout=None if timeout == math.inf else timeout)

    with patch.object(subprocess, 'run', run), patch.object(subprocess.Popen, 'wait', wait):
        yield


@contextmanager
def policy():
    from sentinel import orchestrator
    from sentinel.static import engine, semgrep_adapter

    assert engine.STATIC_TIMEOUT_SECONDS == orchestrator.STATIC_TIMEOUT_SECONDS == 1800
    assert semgrep_adapter.SEMGREP_TIMEOUT_SECONDS == 10
    with ExitStack() as stack:
        stack.enter_context(unlimited_waits())
        stack.enter_context(patch.object(engine, 'STATIC_TIMEOUT_SECONDS', math.inf))
        stack.enter_context(patch.object(orchestrator, 'STATIC_TIMEOUT_SECONDS', math.inf))
        stack.enter_context(patch.object(semgrep_adapter, 'SEMGREP_TIMEOUT_SECONDS', 0))
        yield
