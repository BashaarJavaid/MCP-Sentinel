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


def test_phase12_capture_dry_run_plans_two_calls_under_cap(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "argv", ["capture_gpt_reviews.py", "phase12-smoke"])
    assert capture_gpt_reviews.main() == 0
    output = capsys.readouterr().out
    assert "request count: 2" in output
    assert "aggregate worst-case cost: $0.130736" in output
    assert "no API key read and no network call made" in output
