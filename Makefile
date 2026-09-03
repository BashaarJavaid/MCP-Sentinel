.PHONY: install lint format-check typecheck test audit schema-generate schema-check sarif-check notices notices-check artifacts artifacts-live artifacts-check check demo build

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
	uv export --locked --no-dev --no-editable --no-emit-project --format requirements-txt | uv run pip-audit --no-deps --disable-pip -r /dev/stdin

schema-generate:
	uv run python -m sentinel.schema generate

schema-check:
	uv run python -m sentinel.schema check

sarif-check:
	uv run pytest tests/test_sarif.py

notices:
	uv run python scripts/generate_third_party_notices.py

notices-check:
	uv run python scripts/generate_third_party_notices.py --check

artifacts:
	uv run python -m scripts.generate_phase5_artifacts

artifacts-live:
	uv run python -m scripts.generate_phase5_artifacts --live --max-usd $${MAX_USD:-0.50}

artifacts-check:
	uv run python -m scripts.generate_phase5_artifacts --check

check: lint format-check typecheck schema-check test audit notices-check

demo:
	uv run sentinel demo

build:
	uv build
