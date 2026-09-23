"""
End-to-end integration tests for Flashcard Quizzer CLI application.
"""

import json
from unittest.mock import patch

import pytest

from flashcard_quizzer.main import main


@pytest.fixture
def temp_deck_file(tmp_path):
    """Fixture providing a temporary JSON flashcard deck file."""
    deck_data = [
        {"front": "Python", "back": "Language"},
        {"front": "Pytest", "back": "Framework"},
        {"front": "HTML", "back": "Markup"},
    ]
    file_path = tmp_path / "test_deck.json"
    file_path.write_text(json.dumps(deck_data), encoding="utf-8")
    return str(file_path)


def test_full_session(temp_deck_file, capsys):
    """Simulate a multi-card session, user inputs, and check final output calculation."""
    # Answers: "language" (correct), "wrong" (incorrect), "markup" (correct)
    inputs = ["language", "wrong", "markup"]

    with patch("builtins.input", side_effect=inputs):
        sys_args = ["-f", temp_deck_file, "-m", "sequential", "--stats"]
        main(sys_args)

    captured = capsys.readouterr()
    output = captured.out

    assert "Welcome to Flashcard Quizzer!" in output
    assert "Loaded 3 flashcards in sequential mode." in output
    assert "Front: Python" in output
    assert "Front: Pytest" in output
    assert "Front: HTML" in output
    assert "Correct!" in output
    assert "Incorrect! Expected: Framework" in output
    assert "=== Session Summary ===" in output
    assert "Total Questions Answered: 3" in output
    assert "Accuracy Percentage: 66.7%" in output
    assert "Missed Terms:" in output
    assert "Pytest -> Expected: Framework" in output


def test_graceful_exit_via_command(temp_deck_file, capsys):
    """Verify typing 'exit' terminates cleanly with status code 0."""
    inputs = ["exit"]

    with patch("builtins.input", side_effect=inputs):
        sys_args = ["-f", temp_deck_file, "-m", "sequential"]
        with pytest.raises(SystemExit) as exc_info:
            main(sys_args)

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Session ended. Goodbye!" in captured.out


def test_graceful_exit_via_keyboard_interrupt(temp_deck_file, capsys):
    """Verify KeyboardInterrupt terminates cleanly with status code 0."""
    with patch("builtins.input", side_effect=KeyboardInterrupt):
        sys_args = ["-f", temp_deck_file]
        with pytest.raises(SystemExit) as exc_info:
            main(sys_args)

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Session ended. Goodbye!" in captured.out


def test_graceful_exit_via_eof_error(temp_deck_file, capsys):
    """Verify EOFError terminates cleanly with status code 0."""
    with patch("builtins.input", side_effect=EOFError):
        sys_args = ["-f", temp_deck_file]
        with pytest.raises(SystemExit) as exc_info:
            main(sys_args)

    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "Session ended. Goodbye!" in captured.out


def test_cli_argument_parsing(temp_deck_file, capsys):
    """Verify arguments route correctly to file loaders and mode factories."""
    # Test invalid mode argument exit with code 1
    sys_args = ["-f", temp_deck_file, "-m", "invalid_mode"]
    with pytest.raises(SystemExit) as exc_info:
        main(sys_args)
    assert exc_info.value.code == 1

    captured = capsys.readouterr()
    assert (
        "Unsupported quiz mode" in captured.err
        or "Unsupported quiz mode" in captured.out
    )


def test_cli_missing_file_argument(capsys):
    """Verify missing required -f file argument exits with status code 1."""
    sys_args = ["-m", "sequential"]
    with pytest.raises(SystemExit) as exc_info:
        main(sys_args)
    assert exc_info.value.code == 1


def test_cli_file_not_found(capsys):
    """Verify nonexistent file exits with status code 1."""
    sys_args = ["-f", "nonexistent_file.json"]
    with pytest.raises(SystemExit) as exc_info:
        main(sys_args)
    assert exc_info.value.code == 1


def test_adaptive_mode_session(temp_deck_file, capsys):
    """Verify adaptive mode re-queues wrong answers."""
    # First attempt: "wrong" on Python, "Framework" on Pytest, "Markup" on HTML
    # Second attempt (for re-queued Python): "Language"
    inputs = ["wrong", "Framework", "Markup", "Language"]

    with patch("builtins.input", side_effect=inputs):
        sys_args = ["-f", temp_deck_file, "-m", "adaptive", "--stats"]
        main(sys_args)

    captured = capsys.readouterr()
    output = captured.out

    assert "Total Questions Answered: 4" in output
    assert "Accuracy Percentage: 75.0%" in output
    assert "Pytest -> Expected: Framework" not in output
    assert "Python -> Expected: Language" in output


def test_no_stats_flag(temp_deck_file, capsys):
    """Verify --no-stats suppresses the session summary report."""
    inputs = ["language", "framework", "markup"]

    with patch("builtins.input", side_effect=inputs):
        sys_args = ["-f", temp_deck_file, "--no-stats"]
        main(sys_args)

    captured = capsys.readouterr()
    output = captured.out

    assert "=== Session Summary ===" not in output
