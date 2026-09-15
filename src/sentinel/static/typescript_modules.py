"""Resolve declared source aliases and workspace exports inside included files."""

from __future__ import annotations

import json
import posixpath
from pathlib import Path, PureWindowsPath
from typing import Any

from sentinel.errors import ConfigurationError
from sentinel.report.model import ReportWarning
from sentinel.static.traversal import _devcontainer_json


def local_path(directory: str, target: str) -> str | None:
    if "\\" in target or PureWindowsPath(target).drive or target.startswith("/"):
        return None
    path = posixpath.normpath(posixpath.join(directory, target))
    return None if path == ".." or path.startswith("../") else path


def _mapped(mapping: dict[str, Any], name: str) -> tuple[Any, str] | None:
    if name in mapping:
        return mapping[name], ""
    matches = []
    for pattern, value in mapping.items():
        if pattern.count("*") != 1:
            continue
        prefix, suffix = pattern.split("*")
        if (
            name.startswith(prefix)
            and name.endswith(suffix)
            and len(name) >= len(prefix + suffix)
        ):
            matches.append((len(prefix), len(suffix), pattern, value))
    if not matches:
        return None
    _, _, pattern, value = max(matches, key=lambda item: item[:3])
    prefix, suffix = pattern.split("*")
    return value, name[len(prefix) : len(name) - len(suffix) if suffix else None]


class TypeScriptModules:
    def __init__(
        self, root: Path, configs: tuple[Path, ...], members: tuple[str, ...]
    ) -> None:
        self.packages: dict[str, list[tuple[str, dict[str, Any]]]] = {}
        self.warnings: list[ReportWarning] = []
        self.config_paths = {
            path.relative_to(root).as_posix(): path for path in configs
        }
        self.option_cache: dict[str, dict[str, Any] | None] = {}
        for path in configs:
            if path.name not in {"package.json", "tsconfig.json"}:
                continue
            relative = path.relative_to(root).as_posix()
            directory = posixpath.dirname(relative) or "."
            try:
                value = json.loads(_devcontainer_json(path.read_text(encoding="utf-8")))
            except (OSError, ValueError) as error:
                raise ConfigurationError(
                    f"cannot parse configuration {relative}"
                ) from error
            if not isinstance(value, dict):
                raise ConfigurationError(f"configuration {relative} must be an object")
            if (
                path.name == "package.json"
                and directory in members
                and isinstance(value.get("name"), str)
            ):
                self.packages.setdefault(value["name"], []).append((directory, value))

    def _options(
        self, name: str, seen: frozenset[str] = frozenset()
    ) -> dict[str, Any] | None:
        if name in seen or len(seen) >= 64 or name not in self.config_paths:
            return None
        if name in self.option_cache:
            return self.option_cache[name]
        path = self.config_paths[name]
        try:
            config = json.loads(_devcontainer_json(path.read_text(encoding="utf-8")))
        except (OSError, ValueError) as error:
            raise ConfigurationError(f"cannot parse configuration {name}") from error
        if not isinstance(config, dict):
            raise ConfigurationError(f"configuration {name} must be an object")
        directory = posixpath.dirname(name) or "."
        merged: dict[str, Any] = {}
        parents = config.get("extends", [])
        parents = [parents] if isinstance(parents, str) else parents
        if not isinstance(parents, list):
            return None
        for parent in parents:
            if not isinstance(parent, str):
                return None
            target = local_path(directory, parent) if parent.startswith(".") else None
            if (
                target not in self.config_paths
                and target is not None
                and target + ".json" in self.config_paths
            ):
                target += ".json"
            if target not in self.config_paths:
                warning = ReportWarning(
                    code="static_typescript_configuration_unresolved",
                    message=(
                        f"{name}: inherited configuration {parent!r} was not applied "
                        "because it is outside included source; imports use only "
                        "available local settings and declared package names"
                    ),
                )
                if warning not in self.warnings:
                    self.warnings.append(warning)
                continue
            assert target is not None
            options = self._options(target, seen | {name})
            if options is None:
                return None
            merged.update(options)
        options = config.get("compilerOptions", {})
        if not isinstance(options, dict):
            return None
        if "baseUrl" in options:
            base = options["baseUrl"]
            origin = local_path(directory, base) if isinstance(base, str) else None
            if origin is None:
                return None
            merged["baseUrl"] = origin
        if "paths" in options:
            merged.update(paths=options["paths"], paths_origin=directory)
        self.option_cache[name] = merged
        return merged

    def resolve(self, source: str, module: str) -> tuple[bool, tuple[str, ...]]:
        """Return local ownership and candidate paths; an empty local set is unknown."""
        if module.startswith("."):
            path = local_path(posixpath.dirname(source), module)
            return True, (path,) if path is not None else ()
        directory = posixpath.dirname(source) or "."
        while True:
            config_path = posixpath.normpath(posixpath.join(directory, "tsconfig.json"))
            if config_path in self.config_paths:
                options = self._options(config_path)
                if options is None:
                    return True, ()
                mappings = options.get("paths", {})
                if not isinstance(mappings, dict):
                    return True, ()
                mapped = _mapped(mappings, module)
                origin = options.get("baseUrl", options.get("paths_origin", directory))
                if mapped:
                    targets, wildcard = mapped
                    if (
                        origin is None
                        or not isinstance(targets, list)
                        or not all(isinstance(target, str) for target in targets)
                    ):
                        return True, ()
                    paths = [
                        local_path(origin, target.replace("*", wildcard))
                        for target in targets
                    ]
                    if any(path is None for path in paths):
                        return True, ()
                    return True, tuple(path for path in paths if path is not None)
                break
            if directory == ".":
                break
            directory = posixpath.dirname(directory) or "."
        parts = module.split("/")
        count = 2 if module.startswith("@") else 1
        name, subpath = "/".join(parts[:count]), "/".join(parts[count:])
        packages = self.packages.get(name)
        if packages is None:
            return False, ()
        if len(packages) != 1:
            return True, ()
        directory, package = packages[0]
        if "exports" in package:
            exports = package["exports"]
            key = "./" + subpath if subpath else "."
            if isinstance(exports, dict) and any(k.startswith(".") for k in exports):
                mapped = _mapped(exports, key)
                if mapped is None:
                    return True, ()
                exported, wildcard = mapped
            elif not subpath:
                exported, wildcard = exports, ""
            else:
                return True, ()
            targets = self._export_targets(exported)
            if targets is None:
                return True, ()
            targets = [target.replace("*", wildcard) for target in targets]
            if any(
                not target.startswith("./")
                or ".." in target.split("/")
                or "node_modules" in target.split("/")
                for target in targets
            ):
                return True, ()
        elif subpath:
            targets = ["./" + subpath]
        else:
            targets = [package.get("main", "./index")]
            if not all(isinstance(target, str) for target in targets):
                return True, ()
        paths = [local_path(directory, target) for target in targets]
        if any(path is None for path in paths):
            return True, ()
        return True, tuple(dict.fromkeys(path for path in paths if path is not None))

    @staticmethod
    def _export_targets(value: Any) -> list[str] | None:
        if isinstance(value, str):
            return [value]
        if isinstance(value, dict):
            # Do not use declaration-only `types` as executable handler evidence.
            targets = []
            for key, child in value.items():
                if key in {"types", "require"}:
                    continue
                if key not in {"import", "node", "default"}:
                    return None
                resolved = TypeScriptModules._export_targets(child)
                if resolved is None:
                    return None
                targets.extend(resolved)
            return targets or None
        return None
