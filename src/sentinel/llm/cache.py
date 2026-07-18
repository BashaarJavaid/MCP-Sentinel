"""Persistent whole-batch semantic-review cache."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from platformdirs import user_cache_path


class ReviewCache:
    def __init__(self, *, enabled: bool, root: Path | None = None) -> None:
        self.enabled = enabled
        self.root = root or user_cache_path("mcp-sentinel") / "gpt-review-v1"
        self.errors = 0

    def read(self, key: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None
        try:
            payload = json.loads(
                (self.root / f"{key}.json").read_text(encoding="utf-8")
            )
        except FileNotFoundError:
            return None
        except (OSError, json.JSONDecodeError):
            self.errors += 1
            return None
        if not isinstance(payload, dict) or payload.get("key") != key:
            self.errors += 1
            return None
        return payload

    def mark_error(self) -> None:
        self.errors += 1

    def write(self, key: str, payload: dict[str, Any]) -> bool:
        if not self.enabled:
            return False
        try:
            self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
            os.chmod(self.root, 0o700)
            descriptor, name = tempfile.mkstemp(
                prefix=f".{key}.", suffix=".tmp", dir=self.root
            )
            temporary = Path(name)
            try:
                with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                    os.chmod(temporary, 0o600)
                    json.dump(
                        {"key": key, **payload},
                        handle,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, self.root / f"{key}.json")
            finally:
                temporary.unlink(missing_ok=True)
            return True
        except OSError:
            return False
