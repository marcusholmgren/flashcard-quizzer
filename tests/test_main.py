"""
Unit tests for application entry point (main module).
"""

from unittest.mock import patch

import pytest

from flashcard_quizzer.main import main
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
