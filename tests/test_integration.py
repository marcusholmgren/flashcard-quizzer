"""End-to-end integration tests for Flashcard Quizzer CLI application."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from flashcard_quizzer.main import main


@pytest.fixture
def temp_deck_file(tmp_path: Path) -> str:
    """Fixture providing a temporary JSON flashcard deck file."""
    deck_data = [
        {"front": "Python", "back": "Language"},
        {"front": "Pytest", "back": "Framework"},
        {"front": "HTML", "back": "Markup"},
    ]
    file_path = tmp_path / "test_deck.json"
    file_path.write_text(json.dumps(deck_data), encoding="utf-8")
    return str(file_path)


def test_full_session(temp_deck_file: str, capsys: pytest.CaptureFixture[str]) -> None:
    """Simulate a multi-card session, user inputs, and check final output calculation."""
    inputs = ["language", "wrong", "markup"]

    with patch("builtins.input", side_effect=inputs):
        main(["-f", temp_deck_file])

    captured = capsys.readouterr()
    assert "Welcome to Flashcard Quizzer!" in captured.out
    assert "Total Questions Answered: 3" in captured.out
    assert "Accuracy Percentage: 66.7%" in captured.out
    assert "Missed Terms:" in captured.out
    assert "Pytest -> Expected: Framework" in captured.out


def test_graceful_exit_via_command(
    temp_deck_file: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify typing 'exit' terminates gracefully without raising exception."""
    inputs = ["exit"]

    with patch("builtins.input", side_effect=inputs):
        with pytest.raises(SystemExit) as exc_info:
            main(["-f", temp_deck_file])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Session ended. Goodbye!" in captured.out


def test_graceful_exit_via_keyboard_interrupt(
    temp_deck_file: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify Ctrl+C (KeyboardInterrupt) exits gracefully."""
    with patch("builtins.input", side_effect=KeyboardInterrupt):
        with pytest.raises(SystemExit) as exc_info:
            main(["-f", temp_deck_file])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Session ended. Goodbye!" in captured.out


def test_graceful_exit_via_eof_error(
    temp_deck_file: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify EOF (Ctrl+D) exits gracefully."""
    with patch("builtins.input", side_effect=EOFError):
        with pytest.raises(SystemExit) as exc_info:
            main(["-f", temp_deck_file])

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Session ended. Goodbye!" in captured.out


def test_cli_argument_parsing(
    temp_deck_file: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify system exit behavior when CLI arguments are invalid."""
    with pytest.raises(SystemExit) as exc_info:
        main(["-f", temp_deck_file, "-m", "invalid_mode"])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err or "Error:" in captured.out


def test_cli_missing_file_argument(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify missing required --file argument displays error and exits 1."""
    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err


def test_cli_file_not_found(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify proper error output when passing a non-existent file path."""
    with pytest.raises(SystemExit) as exc_info:
        main(["-f", "non_existent_file.json"])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Error: File not found" in captured.err


def test_adaptive_mode_session(
    temp_deck_file: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify adaptive mode re-queuing behavior during an end-to-end run."""
    inputs = ["wrong", "Framework", "Markup", "Language"]

    with patch("builtins.input", side_effect=inputs):
        main(["-f", temp_deck_file, "-m", "adaptive"])

    captured = capsys.readouterr()
    assert "Total Questions Answered: 4" in captured.out
    assert "Accuracy Percentage: 75.0%" in captured.out


def test_no_stats_flag(temp_deck_file: str, capsys: pytest.CaptureFixture[str]) -> None:
    """Verify --no-stats suppresses the final session summary."""
    inputs = ["Language", "Framework", "Markup"]

    with patch("builtins.input", side_effect=inputs):
        main(["-f", temp_deck_file, "--no-stats"])

    captured = capsys.readouterr()
    assert "Welcome to Flashcard Quizzer!" in captured.out
    assert "=== Session Summary ===" not in captured.out
