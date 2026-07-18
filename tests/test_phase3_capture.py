"""Offline guardrails for the paid Phase 3 integrated checkpoint."""

from __future__ import annotations

import sys

import pytest

from scripts import capture_gpt_reviews


def test_phase3_capture_dry_run_does_not_launch_docker_or_read_live_key(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def reject_docker() -> None:
        raise AssertionError("dry-run capture must not launch Docker")

    monkeypatch.setattr(capture_gpt_reviews, "reap_orphans", reject_docker)
    monkeypatch.setattr(
        sys,
        "argv",
        ["capture_gpt_reviews.py", "phase3-integrated"],
    )

    assert capture_gpt_reviews.main() == 0
    output = capsys.readouterr().out
    assert "static request count: 1" in output
    assert "no API key read, Docker launch, or network call made" in output
