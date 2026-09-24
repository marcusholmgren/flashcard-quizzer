"""Interactive deck creation module for Flashcard Quizzer."""

import json
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Union

from flashcard_quizzer.ui import QuizUI
from flashcard_quizzer.utils.file_handler import Flashcard, load_flashcards


def save_deck(filepath: Union[str, Path], flashcards: List[Flashcard]) -> None:
    """Save flashcards to a JSON file matching the supported wrapped schema.

    Uses atomic file writing to prevent data loss or corruption.

    Args:
        filepath: Destination file path.
        flashcards: List of Flashcard objects to save.
    """
    target_path = Path(filepath).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    deck_data = {
        "cards": [{"front": card.front, "back": card.back} for card in flashcards]
    }

    temp_fd, temp_path = tempfile.mkstemp(dir=target_path.parent, prefix=".deck_tmp_")

    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as file_handle:
            json.dump(deck_data, file_handle, indent=2, ensure_ascii=False)
            file_handle.write("\n")
        os.replace(temp_path, target_path)
    except Exception:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise


def handle_existing_file(filepath: Path, ui: QuizUI) -> Optional[List[Flashcard]]:
    """Prompt the user when the target file already exists.

    Args:
        filepath: Path to the existing file.
        ui: QuizUI instance for rendering output.

    Returns:
        Optional[List[Flashcard]]: Existing cards for append, empty list for overwrite,
        or None if creation was cancelled.
    """
    while True:
        try:
            choice = input("[O]verwrite, [A]ppend, or [C]ancel? ").strip().lower()
        except KeyboardInterrupt, EOFError:
            ui.console.print("\nOperation cancelled.")
            return None

        if choice in ("o", "overwrite"):
            return []
        if choice in ("a", "append"):
            return load_flashcards(filepath)
        if choice in ("c", "cancel"):
            ui.console.print("Deck creation cancelled.")
            return None

        ui.console.print("Invalid choice. Please enter 'O', 'A', or 'C'.")


def _prompt_exit_save(
    target_path: Path, flashcards: List[Flashcard], ui: QuizUI
) -> bool:
    """Prompt user whether to save cards created so far upon exit signal/command.

    Args:
        target_path: Path where deck file should be saved.
        flashcards: List of Flashcard objects created so far.
        ui: QuizUI instance for rendering output.

    Returns:
        bool: True if deck was saved, False otherwise.
    """
    if not flashcards:
        ui.console.print("No cards created. Creation cancelled.")
        return False

    try:
        response = input("Save cards created so far? (y/n): ").strip().lower()
    except KeyboardInterrupt, EOFError:
        ui.console.print("\nCancelled without saving.")
        return False

    if response in ("y", "yes"):
        try:
            save_deck(target_path, flashcards)
            ui.console.print(
                f"[bold green]Success![/bold green] Saved {len(flashcards)} card(s) to '{target_path}'."
            )
            return True
        except Exception as save_error:
            ui.display_error(f"Failed to save deck: {save_error}")
            return False

    ui.console.print("Discarded unsaved changes. Creation cancelled.")
    return False


def _get_card_back_interactive(
    ui: QuizUI, target_path: Path, flashcards: List[Flashcard]
) -> Optional[str]:
    """Interactively prompt user for back side of a card.

    Args:
        ui: QuizUI instance.
        target_path: Path to target save file.
        flashcards: List of cards created so far.

    Returns:
        Optional[str]: Back text string, or None if input was interrupted.
    """
    while True:
        try:
            back_input = input("Back: ").strip()
        except KeyboardInterrupt, EOFError:
            ui.console.print("\nInput interrupted.")
            _prompt_exit_save(target_path, flashcards, ui)
            return None

        if back_input:
            return back_input

        ui.console.print(
            "[bold red]Warning:[/bold red] Back side cannot be empty. Please enter back text."
        )


def create_deck_interactive(
    destination_path: Union[str, Path], ui: Optional[QuizUI] = None
) -> bool:
    """Run interactive CLI loop to create or modify a flashcard deck.

    Args:
        destination_path: Path where the deck JSON file will be saved.
        ui: Optional QuizUI instance.

    Returns:
        bool: True if deck was saved/updated, False if cancelled or no changes saved.
    """
    if ui is None:
        ui = QuizUI()

    target_path = Path(destination_path)
    flashcards: List[Flashcard] = []

    try:
        if target_path.exists():
            ui.console.print(f"Target file '{target_path}' already exists.")
            existing_cards = handle_existing_file(target_path, ui)
            if existing_cards is None:
                return False
            flashcards.extend(existing_cards)
    except OSError as err:
        ui.display_error(f"Cannot access destination path '{target_path}': {err}")
        return False

    ui.console.print("\n[bold cyan]=== Flashcard Deck Creator ===[/bold cyan]")
    ui.console.print("Instructions:")
    ui.console.print(
        " - Press [Enter] with an empty Front or type '[yellow]done[/yellow]' to save and finish."
    )
    ui.console.print(
        " - Type '[yellow]exit[/yellow]' at Front prompt to cancel (prompts to save or discard).\n"
    )

    while True:
        card_num = len(flashcards) + 1
        ui.console.print(f"[bold cyan][Card {card_num}][/bold cyan]")

        try:
            front_input = input("Front: ").strip()
        except KeyboardInterrupt, EOFError:
            ui.console.print("\nInput interrupted.")
            return _prompt_exit_save(target_path, flashcards, ui)

        front_lower = front_input.lower()
        if front_lower in ("", "done"):
            break

        if front_lower == "exit":
            return _prompt_exit_save(target_path, flashcards, ui)

        back_input = _get_card_back_interactive(ui, target_path, flashcards)
        if back_input is None:
            return False

        flashcards.append(Flashcard(front=front_input, back=back_input))

    if flashcards:
        try:
            save_deck(target_path, flashcards)
            ui.console.print(
                f"\n[bold green]Success![/bold green] Saved {len(flashcards)} card(s) to '{target_path}'."
            )
            return True
        except Exception as save_error:
            ui.display_error(f"Failed to save deck: {save_error}")
            return False

    ui.console.print("\nNo cards added. Deck was not saved.")
    return False
