"""
Terminal rendering, colors, and user interaction module for Flashcard Quizzer.
"""

from typing import List, Optional, Tuple

from rich.console import Console

from flashcard_quizzer.utils.file_handler import Flashcard


class QuizUI:
    """Handles CLI presentation, ANSI color rendering, and terminal input/output."""

    def __init__(
        self,
        console: Optional[Console] = None,
        stderr_console: Optional[Console] = None,
    ) -> None:
        """Initialize QuizUI with optional Rich Console instances.

        Args:
            console: An optional Console object from rich for stdout.
            stderr_console: An optional Console object from rich for stderr.
        """
        self.console: Console = console if console is not None else Console()
        self.stderr_console: Console = (
            stderr_console if stderr_console is not None else Console(stderr=True)
        )

    def display_welcome(self, total_cards: int, mode_name: str) -> None:
        """Display welcome greeting and session details.

        Args:
            total_cards: Total number of loaded cards.
            mode_name: Name of the active quiz mode.
        """
        self.console.print("[bold blue]Welcome to Flashcard Quizzer![/bold blue]")
        self.console.print(
            f"Loaded [bold]{total_cards}[/bold] flashcards in [cyan]{mode_name}[/cyan] mode."
        )
        self.console.print(
            "Type '[yellow]exit[/yellow]' or press [yellow]Ctrl+C[/yellow] at any time to quit.\n"
        )

    def display_card_front(self, card: Flashcard) -> None:
        """Display the front text of a flashcard.

        Args:
            card: The Flashcard to present.
        """
        self.console.print(f"[bold cyan]Front:[/bold cyan] {card.front}")

    def get_user_answer(self) -> str:
        """Prompt user for text input.

        Returns:
            The input answer provided by the user.
        """
        return input("Your Answer: ").strip()

    def display_feedback(self, is_correct: bool, expected_back: str) -> None:
        """Display colored terminal feedback based on answer accuracy.

        Args:
            is_correct: True if the user's answer was correct, False otherwise.
            expected_back: The expected back text of the flashcard.
        """
        if is_correct:
            self.console.print("[bold green]Correct![/bold green]\n")
        else:
            self.console.print(
                f"[bold red]Incorrect![/bold red] Expected: [yellow]{expected_back}[/yellow]\n"
            )

    def display_summary(
        self,
        total_answered: int,
        accuracy_pct: float,
        missed_terms: List[Tuple[str, str]],
    ) -> None:
        """Display session summary report with stats and missed terms.

        Args:
            total_answered: Total count of questions answered.
            accuracy_pct: Accuracy percentage (0.0 to 100.0).
            missed_terms: List of tuples containing (front, back) for missed cards.
        """
        self.console.print("\n[bold cyan]=== Session Summary ===[/bold cyan]")
        self.console.print(f"Total Questions Answered: {total_answered}")
        self.console.print(f"Accuracy Percentage: {accuracy_pct:.1f}%")

        if missed_terms:
            self.console.print("\n[bold red]Missed Terms:[/bold red]")
            for front, back in missed_terms:
                self.console.print(
                    f"  • [cyan]{front}[/cyan] -> Expected: [yellow]{back}[/yellow]"
                )
        else:
            self.console.print("\n[bold green]Great job! No missed terms.[/bold green]")

    def display_error(self, message: str) -> None:
        """Display friendly error message to standard error.

        Args:
            message: Error description to print.
        """
        self.stderr_console.print(f"[bold red]Error:[/bold red] {message}")


def display_exit_message(console: Optional[Console] = None) -> None:
    """Display graceful exit message on termination."""
    active_console = console if console is not None else Console()
    active_console.print("\n[yellow]Session ended. Goodbye![/yellow]")
