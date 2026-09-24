"""
Unit tests for the interactive deck creator module.
"""

from pathlib import Path

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
    assert loaded[0] == Flashcard("What is 1+1?", "2")
    assert loaded[1] == Flashcard("What is 2+2?", "4")


def test_append_existing_deck(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify appending new cards preserves previous cards."""
    deck_path = tmp_path / "deck.json"
    initial_cards = [Flashcard("Existing Front", "Existing Back")]
    save_deck(deck_path, initial_cards)

    # Input: 'a' for append, then new card, then 'done'
    inputs = iter(["a", "New Front", "New Back", "done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    success = create_deck_interactive(deck_path)
    assert success is True

    loaded = load_flashcards(deck_path)
    assert len(loaded) == 2
    assert loaded[0] == Flashcard("Existing Front", "Existing Back")
    assert loaded[1] == Flashcard("New Front", "New Back")


def test_overwrite_existing_deck(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify overwrite replaces prior content."""
    deck_path = tmp_path / "deck.json"
    initial_cards = [Flashcard("Old Front", "Old Back")]
    save_deck(deck_path, initial_cards)

    # Input: 'o' for overwrite, then new card, then '' (empty string)
    inputs = iter(["o", "Replacement Front", "Replacement Back", ""])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    success = create_deck_interactive(deck_path)
    assert success is True

    loaded = load_flashcards(deck_path)
    assert len(loaded) == 1
    assert loaded[0] == Flashcard("Replacement Front", "Replacement Back")


def test_exit_conditions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify loop termination on 'done', empty string, and 'exit'."""
    deck_path_done = tmp_path / "done.json"
    inputs_done = iter(["Card 1", "Back 1", "done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs_done))
    assert create_deck_interactive(deck_path_done) is True
    assert len(load_flashcards(deck_path_done)) == 1

    deck_path_empty = tmp_path / "empty.json"
    inputs_empty = iter(["Card 1", "Back 1", ""])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs_empty))
    assert create_deck_interactive(deck_path_empty) is True
    assert len(load_flashcards(deck_path_empty)) == 1

    # Exit with 'y' (save)
    deck_path_exit_save = tmp_path / "exit_save.json"
    inputs_exit_save = iter(["Card 1", "Back 1", "exit", "y"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs_exit_save))
    assert create_deck_interactive(deck_path_exit_save) is True
    assert len(load_flashcards(deck_path_exit_save)) == 1

    # Exit with 'n' (discard)
    deck_path_exit_discard = tmp_path / "exit_discard.json"
    inputs_exit_discard = iter(["Card 1", "Back 1", "exit", "n"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs_exit_discard))
    assert create_deck_interactive(deck_path_exit_discard) is False
    assert not deck_path_exit_discard.exists()


def test_handle_existing_file_cancel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify cancelling existing file action aborts cleanly."""
    deck_path = tmp_path / "deck.json"
    save_deck(deck_path, [Flashcard("A", "B")])

    inputs = iter(["c"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    ui = QuizUI()
    res = handle_existing_file(deck_path, ui)
    assert res is None

    # Test via create_deck_interactive
    inputs_create = iter(["c"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs_create))
    assert create_deck_interactive(deck_path) is False


def test_handle_existing_file_invalid_then_valid(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify retry on invalid choice in existing file prompt."""
    deck_path = tmp_path / "deck.json"
    save_deck(deck_path, [Flashcard("A", "B")])

    inputs = iter(["invalid_choice", "o"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))
    ui = QuizUI()
    res = handle_existing_file(deck_path, ui)
    assert res == []


def test_empty_back_validation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify warning and re-prompt when Back side is empty."""
    deck_path = tmp_path / "deck.json"
    # Front is "Front 1", Back is "" then "  " then "Valid Back", then "done"
    inputs = iter(["Front 1", "", "   ", "Valid Back", "done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    success = create_deck_interactive(deck_path)
    assert success is True
    loaded = load_flashcards(deck_path)
    assert len(loaded) == 1
    assert loaded[0] == Flashcard("Front 1", "Valid Back")


def test_keyboard_interrupt_during_input(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify graceful handling of KeyboardInterrupt during Front/Back input."""
    deck_path = tmp_path / "interrupt.json"

    def mock_input(prompt=""):
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", mock_input)
    success = create_deck_interactive(deck_path)
    assert success is False


def test_keyboard_interrupt_in_overwrite_prompt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify KeyboardInterrupt during existing file prompt cancels cleanly."""
    deck_path = tmp_path / "deck.json"
    save_deck(deck_path, [Flashcard("A", "B")])

    def mock_input(prompt=""):
        raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", mock_input)
    success = create_deck_interactive(deck_path)
    assert success is False


def test_no_cards_created_returns_false(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify returning False when user immediately finishes without adding cards."""
    deck_path = tmp_path / "empty_deck.json"
    inputs = iter(["done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    success = create_deck_interactive(deck_path)
    assert success is False
    assert not deck_path.exists()


def test_cli_integration_create_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify --create flag integration with main()."""
    deck_path = tmp_path / "cli_deck.json"
    inputs = iter(["Term 1", "Def 1", "done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    sys_args = ["-f", str(deck_path), "--create"]
    with pytest.raises(SystemExit) as exc_info:
        main(sys_args)
    assert exc_info.value.code == 0
    assert deck_path.exists()
    assert len(load_flashcards(deck_path)) == 1


def test_cli_integration_create_subcommand(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify create subcommand integration with main()."""
    deck_path = tmp_path / "subcommand_deck.json"
    inputs = iter(["Term 2", "Def 2", "done"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    sys_args = ["create", "-f", str(deck_path)]
    with pytest.raises(SystemExit) as exc_info:
        main(sys_args)
    assert exc_info.value.code == 0
    assert deck_path.exists()
    assert len(load_flashcards(deck_path)) == 1


def test_save_deck_exception_handling(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify temp file cleanup when saving deck encounters an exception."""
    deck_path = tmp_path / "read_only" / "deck.json"
    cards = [Flashcard("Front", "Back")]

    # Mock tempfile.mkstemp to succeed, but json.dump to raise RuntimeError
    def mock_dump(*args, **kwargs):
        raise RuntimeError("Disk error")

    monkeypatch.setattr("json.dump", mock_dump)

    with pytest.raises(RuntimeError, match="Disk error"):
        save_deck(deck_path, cards)


def test_prompt_exit_save_interrupt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify exit prompt handling when KeyboardInterrupt occurs during save prompt."""
    deck_path = tmp_path / "deck.json"
    inputs = iter(["Front 1", "Back 1", "exit"])

    def mock_input(prompt=""):
        try:
            val = next(inputs)
            return val
        except StopIteration:
            raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", mock_input)
    assert create_deck_interactive(deck_path) is False


def test_back_input_interrupt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify exit prompt handling when KeyboardInterrupt occurs during Back input."""
    deck_path = tmp_path / "deck.json"
    inputs = iter(["Front 1"])

    def mock_input(prompt=""):
        try:
            val = next(inputs)
            return val
        except StopIteration:
            raise KeyboardInterrupt()

    monkeypatch.setattr("builtins.input", mock_input)
    # Front 1 entered, then Back raises KeyboardInterrupt, then save prompt raises KeyboardInterrupt -> False
    assert create_deck_interactive(deck_path) is False
