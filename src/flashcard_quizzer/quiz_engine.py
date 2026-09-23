"""
Core quiz engine module implementing Strategy and Factory patterns for quiz modes.
"""

import random
from abc import ABC, abstractmethod
from collections import deque
from typing import Dict, List, Type

from flashcard_quizzer.utils.file_handler import Flashcard


class QuizMode(ABC):
    """Abstract base class defining the Strategy interface for quiz modes."""

    def __init__(self, cards: List[Flashcard]) -> None:
        """Initialize the quiz mode with a list of flashcards.

        Args:
            cards: List of Flashcard objects to be used in the quiz.
        """
        self._initial_cards: List[Flashcard] = list(cards)

    @abstractmethod
    def has_next(self) -> bool:
        """Check if there are remaining cards to present in the quiz.

        Returns:
            True if cards remain, False otherwise.
        """
        pass

    @abstractmethod
    def get_next_card(self) -> Flashcard:
        """Retrieve the next flashcard to present.

        Returns:
            The next Flashcard instance.

        Raises:
            IndexError: If no cards remain in the quiz.
        """
        pass

    @abstractmethod
    def record_answer(self, card: Flashcard, is_correct: bool) -> None:
        """Record the outcome of a user's answer for a card.

        Args:
            card: The Flashcard that was answered.
            is_correct: True if answered correctly, False otherwise.
        """
        pass


class SequentialMode(QuizMode):
    """Quiz mode strategy that presents cards in their initial order (1 to N)."""

    def __init__(self, cards: List[Flashcard]) -> None:
        """Initialize SequentialMode with cards queued in initial order."""
        super().__init__(cards)
        self._queue: deque[Flashcard] = deque(self._initial_cards)

    def has_next(self) -> bool:
        """Check if remaining cards exist in sequence."""
        return len(self._queue) > 0

    def get_next_card(self) -> Flashcard:
        """Get the next card in sequential order."""
        if not self._queue:
            raise IndexError("No cards remaining in quiz.")
        return self._queue.popleft()

    def record_answer(self, card: Flashcard, is_correct: bool) -> None:
        """Record answer for sequential mode (no queue modification needed)."""
        pass


class RandomMode(QuizMode):
    """Quiz mode strategy that shuffles cards randomly before presentation."""

    def __init__(self, cards: List[Flashcard]) -> None:
        """Initialize RandomMode with randomly shuffled cards."""
        super().__init__(cards)
        shuffled = list(self._initial_cards)
        random.shuffle(shuffled)
        self._queue: deque[Flashcard] = deque(shuffled)

    def has_next(self) -> bool:
        """Check if remaining cards exist in random queue."""
        return len(self._queue) > 0

    def get_next_card(self) -> Flashcard:
        """Get the next randomly shuffled card."""
        if not self._queue:
            raise IndexError("No cards remaining in quiz.")
        return self._queue.popleft()

    def record_answer(self, card: Flashcard, is_correct: bool) -> None:
        """Record answer for random mode (no queue modification needed)."""
        pass


class AdaptiveMode(QuizMode):
    """Quiz mode strategy that re-queues incorrectly answered cards until mastered."""

    def __init__(self, cards: List[Flashcard]) -> None:
        """Initialize AdaptiveMode with active cards queue."""
        super().__init__(cards)
        self._queue: deque[Flashcard] = deque(self._initial_cards)

    def has_next(self) -> bool:
        """Check if remaining cards exist in adaptive queue."""
        return len(self._queue) > 0

    def get_next_card(self) -> Flashcard:
        """Get the next card from the adaptive queue."""
        if not self._queue:
            raise IndexError("No cards remaining in quiz.")
        return self._queue.popleft()

    def record_answer(self, card: Flashcard, is_correct: bool) -> None:
        """Record answer outcome. Re-queues card if answered incorrectly."""
        if not is_correct:
            self._queue.append(card)


class QuizModeFactory:
    """Factory pattern implementation for creating QuizMode instances."""

    _MODES: Dict[str, Type[QuizMode]] = {
        "sequential": SequentialMode,
        "random": RandomMode,
        "adaptive": AdaptiveMode,
    }

    @classmethod
    def create_mode(cls, mode_name: str, cards: List[Flashcard]) -> QuizMode:
        """Factory method to instantiate a QuizMode based on mode name.

        Args:
            mode_name: Name of mode ('sequential', 'random', 'adaptive').
            cards: List of Flashcard objects for the quiz session.

        Returns:
            An instance of a concrete QuizMode subclass.

        Raises:
            ValueError: If mode_name is not supported or invalid.
        """
        if not isinstance(mode_name, str):
            raise ValueError(
                f"Mode name must be a string, got {type(mode_name).__name__}."
            )

        normalized_name = mode_name.strip().lower()
        mode_class = cls._MODES.get(normalized_name)

        if mode_class is None:
            supported = ", ".join(cls._MODES.keys())
            raise ValueError(
                f"Unsupported quiz mode '{mode_name}'. Supported modes are: {supported}."
            )

        return mode_class(cards)
