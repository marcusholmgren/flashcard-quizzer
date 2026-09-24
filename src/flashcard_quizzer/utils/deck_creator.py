"""
Interactive deck creation module for Flashcard Quizzer.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Union

from flashcard_quizzer.ui import QuizUI
from flashcard_quizzer.utils.file_handler import Flashcard, load_flashcards


def save_deck(filepath: Union[str, Path], cards: List[Flashcard]) -> None:
    """Save flashcards to a JSON file matching the supported wrapped schema.

    Uses atomic file writing to prevent data loss or corruption.

    Args:
        filepath: Destination file path.
        cards: List of Flashcard objects to save.
    """
    path = Path(filepath).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    data = {"cards": [{"front": card.front, "back": card.back} for card in cards]}

    temp_fd, temp_path = tempfile.mkstemp(dir=path.parent, prefix=".deck_tmp_")
    try:
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(temp_path, path)
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
        A list of existing Flashcard objects for append, an empty list for overwrite,
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
        elif choice in ("a", "append"):
            return load_flashcards(filepath)
        elif choice in ("c", "cancel"):
            ui.console.print("Deck creation cancelled.")
            return None
        else:
            ui.console.print("Invalid choice. Please enter 'O', 'A', or 'C'.")


def _prompt_exit_save(path: Path, cards: List[Flashcard], ui: QuizUI) -> bool:
    """Prompt user whether to save cards created so far upon exit signal/command.

    Args:
        path: Path where deck file should be saved.
        cards: List of Flashcard objects created so far.
        ui: QuizUI instance for rendering output.

    Returns:
        True if deck was saved, False otherwise.
    """
    if not cards:
        ui.console.print("No cards created. Creation cancelled.")
        return False

    try:
        response = input("Save cards created so far? (y/n): ").strip().lower()
    except KeyboardInterrupt, EOFError:
        ui.console.print("\nCancelled without saving.")
        return False

    if response in ("y", "yes"):
        save_deck(path, cards)
        ui.console.print(
            f"[bold green]Success![/bold green] Saved {len(cards)} card(s) to '{path}'."
        )
        return True

    ui.console.print("Discarded unsaved changes. Creation cancelled.")
    return False


def create_deck_interactive(
    destination_path: Union[str, Path], ui: Optional[QuizUI] = None
) -> bool:
    """Run interactive CLI loop to create or modify a flashcard deck.

    Args:
        destination_path: Path where the deck JSON file will be saved.
        ui: Optional QuizUI instance.

    Returns:
        True if deck was saved/updated, False if cancelled or no changes saved.
    """
    if ui is None:
        ui = QuizUI()

    path = Path(destination_path)
    cards: List[Flashcard] = []

    if path.exists():
        ui.console.print(f"Target file '{path}' already exists.")
        existing_cards = handle_existing_file(path, ui)
        if existing_cards is None:
            return False
        cards.extend(existing_cards)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)

    ui.console.print("\n[bold cyan]=== Flashcard Deck Creator ===[/bold cyan]")
    ui.console.print("Instructions:")
    ui.console.print(
        " - Press [Enter] with an empty Front or type '[yellow]done[/yellow]' to save and finish."
    )
    ui.console.print(
        " - Type '[yellow]exit[/yellow]' at Front prompt to cancel (prompts to save or discard)."
    )
    ui.console.print("")

    while True:
        card_num = len(cards) + 1
        ui.console.print(f"[bold cyan][Card {card_num}][/bold cyan]")

        try:
            front_input = input("Front: ").strip()
        except KeyboardInterrupt, EOFError:
            ui.console.print("\nInput interrupted.")
            return _prompt_exit_save(path, cards, ui)

        front_lower = front_input.lower()
        if front_lower in ("", "done"):
            break

        if front_lower == "exit":
            return _prompt_exit_save(path, cards, ui)

        while True:
            try:
                back_input = input("Back: ").strip()
            except KeyboardInterrupt, EOFError:
                ui.console.print("\nInput interrupted.")
                return _prompt_exit_save(path, cards, ui)

            if back_input:
                break
            ui.console.print(
                "[bold red]Warning:[/bold red] Back side cannot be empty. Please enter back text."
            )

        cards.append(Flashcard(front=front_input, back=back_input))

    if cards:
        save_deck(path, cards)
        ui.console.print(
            f"\n[bold green]Success![/bold green] Saved {len(cards)} card(s) to '{path}'."
        )
        return True
    else:
        ui.console.print("\nNo cards added. Deck was not saved.")
        return False
