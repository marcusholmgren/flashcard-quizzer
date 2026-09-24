"""Unit tests for application entry point (main module)."""

from pathlib import Path
from unittest.mock import patch

import pytest

from flashcard_quizzer.main import main
from flashcard_quizzer.ui import QuizUI
from flashcard_quizzer.utils.file_handler import Flashcard


def test_main_success(capsys: pytest.CaptureFixture[str]) -> None:
    """Test main function prints greeting and loaded card count."""
    fake_cards = [
        Flashcard("Q1", "A1"),
        Flashcard("Q2", "A2"),
    ]
    with (
        patch(
            "flashcard_quizzer.main.load_flashcards", return_value=fake_cards
        ) as mock_load,
        patch("builtins.input", side_effect=["A1", "A2"]),
    ):
        main(["-f", "fake_path.json"])
        mock_load.assert_called_once_with("fake_path.json")

    captured = capsys.readouterr()
    assert "Welcome to Flashcard Quizzer!" in captured.out
    assert "Loaded 2 flashcards in sequential mode." in captured.out


def test_empty_deck_file_exits_with_code_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify clean error message and status code 1 when loading an empty deck file."""
    empty_file = tmp_path / "empty_deck.json"
    empty_file.write_text("[]", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        main(["-f", str(empty_file)])

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "The flashcard deck is empty." in captured.err


def test_whitespace_answer_comparison(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Verify leading and trailing whitespace is stripped from answers prior to comparison."""
    deck_file = tmp_path / "whitespace_deck.json"
    deck_file.write_text(
        '[{"front": "  Question  ", "back": "  Answer  "}]', encoding="utf-8"
    )

    inputs = ["   answer   "]
    with patch("builtins.input", side_effect=inputs):
        main(["-f", str(deck_file)])

    captured = capsys.readouterr()
    assert "Correct!" in captured.out


def test_zero_questions_answered_summary_stats(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify summary display handles 0 answered questions without ZeroDivisionError."""
    ui = QuizUI()
    ui.display_summary(0, 0.0, [])
    captured = capsys.readouterr()
    assert "Total Questions Answered: 0" in captured.out
    assert "Accuracy Percentage: 0.0%" in captured.out
