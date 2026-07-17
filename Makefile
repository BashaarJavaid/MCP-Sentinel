.PHONY: install lint format-check typecheck test audit schema-generate schema-check sarif-check check demo build

# Semgrep 1.170.0 hard-pins the affected transitive versions. See SECURITY.md.
PIP_AUDIT_EXCEPTIONS = --ignore-vuln PYSEC-2026-2132 --ignore-vuln CVE-2026-52870 --ignore-vuln CVE-2026-52869 --ignore-vuln CVE-2026-59950

install:
	uv sync --extra dev

lint:
	uv run ruff check .

format-check:
	uv run ruff format --check .

typecheck:
	uv run mypy

test:
	uv run pytest

audit:
	uv export --locked --no-dev --no-editable --no-emit-project --format requirements-txt | uv run pip-audit --no-deps --disable-pip $(PIP_AUDIT_EXCEPTIONS) -r /dev/stdin

schema-generate:
	uv run python -m sentinel.schema generate

schema-check:
	uv run python -m sentinel.schema check

sarif-check:
	uv run pytest tests/test_sarif.py

check: lint format-check typecheck schema-check test audit

demo:
	uv run sentinel demo

build:
	uv build
