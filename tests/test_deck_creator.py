"""Unit tests for the interactive deck creator module."""

from pathlib import Path
from typing import Any

import pytest

from flashcard_quizzer.main import main
from flashcard_quizzer.ui import QuizUI
from flashcard_quizzer.utils.deck_creator import (
    create_deck_interactive,
    handle_existing_file,
    save_deck,
)
from flashcard_quizzer.utils.file_handler import Flashcard, load_flashcards


def test_create_new_deck(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify writing new cards to a non-existent path including parent directories."""
    deck_path = tmp_path / "sub_dir" / "new_deck.json"
    inputs = iter(["What is 1+1?", "2", "What is 2+2?", "4", "done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    success = create_deck_interactive(deck_path)
    assert success is True
    assert deck_path.exists()

    loaded = load_flashcards(deck_path)
    assert len(loaded) == 2


def test_append_existing_deck(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify loading existing cards and adding new cards to the deck in append mode."""
    deck_path = tmp_path / "existing_deck.json"
    initial_cards = [Flashcard("Card 1", "Ans 1")]
    save_deck(deck_path, initial_cards)

    inputs = iter(["a", "Card 2", "Ans 2", "done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    success = create_deck_interactive(deck_path)
    assert success is True

    loaded = load_flashcards(deck_path)
    assert len(loaded) == 2
    assert loaded[0].front == "Card 1"
    assert loaded[1].front == "Card 2"


def test_overwrite_existing_deck(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify discarding existing cards in overwrite mode."""
    deck_path = tmp_path / "existing_deck.json"
    initial_cards = [Flashcard("Card 1", "Ans 1")]
    save_deck(deck_path, initial_cards)

    inputs = iter(["o", "New Card", "New Ans", "done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    success = create_deck_interactive(deck_path)
    assert success is True

    loaded = load_flashcards(deck_path)
    assert len(loaded) == 1
    assert loaded[0].front == "New Card"


def test_exit_conditions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify exit keyword at Front prompt and prompt to save unsaved changes."""
    deck_path = tmp_path / "exit_deck.json"

    # Scenario 1: Exit with save ('y')
    inputs_save = iter(["Card 1", "Ans 1", "exit", "y"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs_save))
    assert create_deck_interactive(deck_path) is True
    assert len(load_flashcards(deck_path)) == 1

    # Scenario 2: Exit without save ('n')
    deck_path_2 = tmp_path / "exit_deck_2.json"
    inputs_nosave = iter(["Card 1", "Ans 1", "exit", "n"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs_nosave))
    assert create_deck_interactive(deck_path_2) is False
    assert not deck_path_2.exists()


def test_handle_existing_file_cancel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify cancel option when destination file already exists."""
    deck_path = tmp_path / "existing.json"
    save_deck(deck_path, [Flashcard("Q", "A")])

    inputs = iter(["c"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    ui = QuizUI()

    result = handle_existing_file(deck_path, ui)
    assert result is None


def test_handle_existing_file_invalid_then_valid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify invalid option prompts again until a valid selection is provided."""
    deck_path = tmp_path / "existing.json"
    save_deck(deck_path, [Flashcard("Q", "A")])

    inputs = iter(["invalid", "o"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    ui = QuizUI()

    result = handle_existing_file(deck_path, ui)
    assert result == []


def test_empty_back_validation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify empty string on Back prompt shows warning and reprompts user."""
    deck_path = tmp_path / "reprompt_deck.json"
    inputs = iter(["Front", "", "Back", "done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    success = create_deck_interactive(deck_path)
    assert success is True
    loaded = load_flashcards(deck_path)
    assert loaded[0].back == "Back"


def test_keyboard_interrupt_during_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify KeyboardInterrupt during Front prompt triggers exit/save flow."""
    deck_path = tmp_path / "interrupt_deck.json"

    def mock_input(prompt: str = "") -> str:
        if "Front" in prompt:
            raise KeyboardInterrupt()
        return "n"

    monkeypatch.setattr("builtins.input", mock_input)
    assert create_deck_interactive(deck_path) is False


def test_keyboard_interrupt_in_overwrite_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify Ctrl+C during file conflict prompt cancels gracefully."""
    deck_path = tmp_path / "existing.json"
    save_deck(deck_path, [Flashcard("Q", "A")])

    def mock_input(prompt: str = "") -> str:
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", mock_input)
    ui = QuizUI()
    assert handle_existing_file(deck_path, ui) is None


def test_no_cards_created_returns_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify pressing enter on first card returns False and creates no file."""
    deck_path = tmp_path / "empty.json"
    inputs = iter([""])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    success = create_deck_interactive(deck_path)
    assert success is False
    assert not deck_path.exists()


def test_cli_integration_create_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify launching deck creator via --create flag."""
    deck_path = tmp_path / "cli_created.json"
    inputs = iter(["Front 1", "Back 1", "done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main(["-f", str(deck_path), "--create"])

    assert exc_info.value.code == 0
    assert deck_path.exists()


def test_cli_integration_create_subcommand(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify launching deck creator via 'create' subcommand."""
    deck_path = tmp_path / "cli_subcommand.json"
    inputs = iter(["Front 1", "Back 1", "done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    with pytest.raises(SystemExit) as exc_info:
        main(["create", "-f", str(deck_path)])

    assert exc_info.value.code == 0
    assert deck_path.exists()


def test_save_deck_exception_handling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify temp file cleanup when saving deck encounters an exception."""
    deck_path = tmp_path / "read_only" / "deck.json"
    cards = [Flashcard("Front", "Back")]

    def mock_dump(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("Disk error")

    monkeypatch.setattr("json.dump", mock_dump)

    with pytest.raises(RuntimeError, match="Disk error"):
        save_deck(deck_path, cards)


def test_prompt_exit_save_interrupt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify handling of KeyboardInterrupt inside _prompt_exit_save."""
    deck_path = tmp_path / "exit_interrupt.json"

    def mock_input(prompt: str = "") -> str:
        if "Front" in prompt:
            return "exit"
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", mock_input)
    assert create_deck_interactive(deck_path) is False


def test_back_input_interrupt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify handling of KeyboardInterrupt at Back prompt."""
    deck_path = tmp_path / "back_interrupt.json"

    def mock_input(prompt: str = "") -> str:
        if "Front" in prompt:
            return "Front 1"
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", mock_input)
    assert create_deck_interactive(deck_path) is False
