"""Main entry point and CLI orchestration layer for Flashcard Quizzer application."""

import argparse
import sys
from typing import List, Optional, Tuple

from flashcard_quizzer.quiz_engine import QuizMode, QuizModeFactory
from flashcard_quizzer.ui import QuizUI, display_exit_message
from flashcard_quizzer.utils.deck_creator import create_deck_interactive
from flashcard_quizzer.utils.file_handler import Flashcard, load_flashcards


def parse_arguments(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments.

    Args:
        args: Optional list of command-line arguments for testing.

    Returns:
        argparse.Namespace: Parsed Namespace containing flags.
    """
    parser = argparse.ArgumentParser(description="Flashcard Quizzer CLI Application")
    parser.add_argument(
        "command",
        nargs="?",
        choices=["create"],
        help="Optional subcommand ('create' to enter interactive deck creation mode).",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        required=True,
        help="Path to JSON flashcard deck file.",
    )
    parser.add_argument(
        "-c",
        "--create",
        action="store_true",
        help="Launch interactive deck creator mode.",
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


def _evaluate_card_answer(
    user_answer: str,
    flashcard: Flashcard,
) -> bool:
    """Compare user input answer with expected flashcard answer after trimming.

    Args:
        user_answer: Raw user string answer.
        flashcard: Flashcard instance being answered.

    Returns:
        bool: True if answers match after whitespace normalization, False otherwise.
    """
    normalized_user = user_answer.strip().lower()
    normalized_expected = flashcard.back.strip().lower()
    return normalized_user == normalized_expected


def _calculate_accuracy(correct_count: int, total_answered: int) -> float:
    """Safely calculate accuracy percentage without division by zero.

    Args:
        correct_count: Number of correctly answered questions.
        total_answered: Total questions answered.

    Returns:
        float: Calculated accuracy percentage (0.0 to 100.0).
    """
    if total_answered <= 0:
        return 0.0
    return (correct_count / total_answered) * 100.0


def _process_quiz_loop(
    ui: QuizUI,
    quiz_strategy: QuizMode,
) -> Tuple[int, int, List[Tuple[str, str]]]:
    """Execute main quiz loop over remaining flashcards.

    Args:
        ui: QuizUI presentation object.
        quiz_strategy: Instantiated QuizMode strategy.

    Returns:
        Tuple[int, int, List[Tuple[str, str]]]: Counts for total answered,
        correct answers, and list of missed term tuples.
    """
    total_answered: int = 0
    correct_count: int = 0
    missed_terms: List[Tuple[str, str]] = []

    while quiz_strategy.has_remaining_cards():
        card = quiz_strategy.get_next_card()
        ui.display_card_front(card)

        user_answer = ui.get_user_answer()
        if user_answer.strip().lower() == "exit":
            display_exit_message(ui.console)
            sys.exit(0)

        is_correct = _evaluate_card_answer(user_answer, card)
        ui.display_feedback(is_correct, card.back)

        quiz_strategy.record_answer(card, is_correct)
        total_answered += 1

        if is_correct:
            correct_count += 1
        else:
            missed_pair = (card.front, card.back)
            if missed_pair not in missed_terms:
                missed_terms.append(missed_pair)

    return total_answered, correct_count, missed_terms


def run_quiz_session(
    ui: QuizUI,
    parsed_args: argparse.Namespace,
    flashcards: List[Flashcard],
) -> None:
    """Execute the interactive quiz session loop.

    Args:
        ui: QuizUI instance for rendering and interaction.
        parsed_args: Namespace containing command-line options.
        flashcards: List of loaded Flashcard objects.
    """
    try:
        quiz_strategy = QuizModeFactory.create_mode(parsed_args.mode, flashcards)
    except ValueError as error:
        ui.display_error(str(error))
        sys.exit(1)

    ui.display_welcome(len(flashcards), parsed_args.mode)

    try:
        total_answered, correct_count, missed_terms = _process_quiz_loop(
            ui, quiz_strategy
        )
    except KeyboardInterrupt, EOFError:
        display_exit_message(ui.console)
        sys.exit(0)

    if parsed_args.stats:
        accuracy_pct = _calculate_accuracy(correct_count, total_answered)
        ui.display_summary(total_answered, accuracy_pct, missed_terms)


def main(sys_args: Optional[List[str]] = None) -> None:
    """Main function to run the Flashcard Quizzer CLI.

    Args:
        sys_args: Optional command line argument list for testing.
    """
    ui = QuizUI()
    try:
        parsed_args = parse_arguments(sys_args)
    except SystemExit as exit_exc:
        if exit_exc.code != 0:
            ui.display_error("Invalid or missing CLI arguments.")
            sys.exit(1)
        sys.exit(0)

    if parsed_args.create or parsed_args.command == "create":
        create_deck_interactive(parsed_args.file, ui)
        sys.exit(0)

    try:
        flashcards = load_flashcards(parsed_args.file)
    except SystemExit as exit_exc:
        sys.exit(exit_exc.code)
    except Exception as error:
        ui.display_error(f"Failed to load file: {error}")
        sys.exit(1)

    if not flashcards:
        ui.display_error("The flashcard deck is empty.")
        sys.exit(1)

    run_quiz_session(ui, parsed_args, flashcards)


if __name__ == "__main__":
    main()
