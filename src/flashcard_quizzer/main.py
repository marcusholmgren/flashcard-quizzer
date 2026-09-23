"""
Main entry point and CLI orchestration layer for Flashcard Quizzer application.
"""

import argparse
import sys
from typing import List, Optional, Tuple

from flashcard_quizzer.quiz_engine import QuizModeFactory
from flashcard_quizzer.ui import QuizUI, display_exit_message
from flashcard_quizzer.utils.file_handler import Flashcard, load_flashcards


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Optional list of command-line arguments for testing.

    Returns:
        Parsed argparse.Namespace containing flags.
    """
    parser = argparse.ArgumentParser(description="Flashcard Quizzer CLI Application")
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        required=True,
        help="Path to JSON flashcard deck file.",
    )
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="sequential",
        help="Quiz mode: 'sequential', 'random', or 'adaptive' (default: 'sequential').",
    )
    parser.add_argument(
        "--stats",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Toggle final summary session report presentation (default: True).",
    )
    return parser.parse_args(args)


def run_quiz_session(
    ui: QuizUI,
    parsed_args: argparse.Namespace,
    cards: List[Flashcard],
) -> None:
    """Execute the interactive quiz session loop.

    Args:
        ui: QuizUI instance for rendering and interaction.
        parsed_args: Namespace containing command-line options.
        cards: List of loaded Flashcard objects.
    """
    try:
        quiz_mode = QuizModeFactory.create_mode(parsed_args.mode, cards)
    except ValueError as err:
        ui.display_error(str(err))
        sys.exit(1)

    ui.display_welcome(len(cards), parsed_args.mode)

    total_answered: int = 0
    correct_count: int = 0
    missed_terms: List[Tuple[str, str]] = []

    try:
        while quiz_mode.has_next():
            card = quiz_mode.get_next_card()
            ui.display_card_front(card)

            user_answer = ui.get_user_answer()
            if user_answer.lower() == "exit":
                display_exit_message(ui.console)
                sys.exit(0)

            is_correct = user_answer.lower() == card.back.lower()
            ui.display_feedback(is_correct, card.back)

            quiz_mode.record_answer(card, is_correct)
            total_answered += 1

            if is_correct:
                correct_count += 1
            else:
                if (card.front, card.back) not in missed_terms:
                    missed_terms.append((card.front, card.back))

    except KeyboardInterrupt, EOFError:
        display_exit_message(ui.console)
        sys.exit(0)

    if parsed_args.stats:
        accuracy = (
            (correct_count / total_answered * 100.0) if total_answered > 0 else 0.0
        )
        ui.display_summary(total_answered, accuracy, missed_terms)


def main(sys_args: Optional[List[str]] = None) -> None:
    """Main function to run the Flashcard Quizzer CLI."""
    ui = QuizUI()
    try:
        parsed_args = parse_arguments(sys_args)
    except SystemExit as e:
        if e.code != 0:
            ui.display_error("Invalid or missing CLI arguments.")
            sys.exit(1)
        sys.exit(0)

    try:
        cards = load_flashcards(parsed_args.file)
    except SystemExit as e:
        # load_flashcards handles error printing and sys.exit(1)
        sys.exit(e.code)
    except Exception as err:
        ui.display_error(f"Failed to load file: {err}")
        sys.exit(1)

    if not cards:
        ui.display_error("The flashcard deck is empty.")
        sys.exit(1)

    run_quiz_session(ui, parsed_args, cards)


if __name__ == "__main__":
    main()
