"""Core quiz engine module implementing Strategy and Factory patterns for quiz modes."""

import random
from abc import ABC, abstractmethod
from collections import deque
from typing import Dict, List, Type

from flashcard_quizzer.utils.file_handler import Flashcard


class QuizMode(ABC):
    """Abstract base class defining the Strategy interface for quiz modes."""

    def __init__(self, flashcards: List[Flashcard]) -> None:
        """Initialize the quiz mode with a list of flashcards.

        Args:
            flashcards: List of Flashcard objects to be used in the quiz.
        """
        self._initial_flashcards: List[Flashcard] = list(flashcards)

    @abstractmethod
    def has_remaining_cards(self) -> bool:
        """Check if there are remaining flashcards to present in the quiz.

        Returns:
            bool: True if cards remain, False otherwise.
        """
        pass

    def has_next(self) -> bool:
        """Backward-compatible alias for has_remaining_cards.

        Returns:
            bool: True if cards remain, False otherwise.
        """
        return self.has_remaining_cards()

    @abstractmethod
    def get_next_card(self) -> Flashcard:
        """Retrieve the next flashcard to present.

        Returns:
            Flashcard: The next Flashcard instance.

        Raises:
            IndexError: If no cards remain in the quiz.
        """
        pass

    @abstractmethod
    def record_answer(self, card: Flashcard, is_correct: bool) -> None:
        """Record the outcome of a user's answer for a flashcard.

        Args:
            card: The Flashcard that was answered.
            is_correct: True if answered correctly, False otherwise.
        """
        pass


class SequentialQuizMode(QuizMode):
    """Quiz mode strategy that presents cards in their initial order (1 to N)."""

    def __init__(self, flashcards: List[Flashcard]) -> None:
        """Initialize SequentialQuizMode with cards queued in initial order.

        Args:
            flashcards: List of Flashcard objects for the quiz session.
        """
        super().__init__(flashcards)
        self._card_queue: deque[Flashcard] = deque(self._initial_flashcards)

    def has_remaining_cards(self) -> bool:
        """Check if remaining cards exist in sequence.

        Returns:
            bool: True if cards remain in the queue, False otherwise.
        """
        return len(self._card_queue) > 0

    def get_next_card(self) -> Flashcard:
        """Get the next card in sequential order.

        Returns:
            Flashcard: The next card in sequence.

        Raises:
            IndexError: If no cards remain in the queue.
        """
        if not self._card_queue:
            raise IndexError("No cards remaining in quiz.")
        return self._card_queue.popleft()

    def record_answer(self, card: Flashcard, is_correct: bool) -> None:
        """Record answer for sequential mode (no queue modification needed).

        Args:
            card: The Flashcard answered.
            is_correct: True if correct, False otherwise.
        """
        pass


class RandomQuizMode(QuizMode):
    """Quiz mode strategy that shuffles cards randomly before presentation."""

    def __init__(self, flashcards: List[Flashcard]) -> None:
        """Initialize RandomQuizMode with randomly shuffled cards.

        Args:
            flashcards: List of Flashcard objects for the quiz session.
        """
        super().__init__(flashcards)
        shuffled_flashcards = list(self._initial_flashcards)
        random.shuffle(shuffled_flashcards)
        self._card_queue: deque[Flashcard] = deque(shuffled_flashcards)

    def has_remaining_cards(self) -> bool:
        """Check if remaining cards exist in random queue.

        Returns:
            bool: True if cards remain in the queue, False otherwise.
        """
        return len(self._card_queue) > 0

    def get_next_card(self) -> Flashcard:
        """Get the next randomly shuffled card.

        Returns:
            Flashcard: The next card in random queue.

        Raises:
            IndexError: If no cards remain in the queue.
        """
        if not self._card_queue:
            raise IndexError("No cards remaining in quiz.")
        return self._card_queue.popleft()

    def record_answer(self, card: Flashcard, is_correct: bool) -> None:
        """Record answer for random mode (no queue modification needed).

        Args:
            card: The Flashcard answered.
            is_correct: True if correct, False otherwise.
        """
        pass


class AdaptiveQuizMode(QuizMode):
    """Quiz mode strategy re-queueing incorrect cards up to max_retries."""

    def __init__(self, flashcards: List[Flashcard], max_retries: int = 5) -> None:
        """Initialize AdaptiveQuizMode with active cards queue and retry limits.

        Args:
            flashcards: List of Flashcard objects for the quiz session.
            max_retries: Maximum times an incorrect card can be re-queued.
        """
        super().__init__(flashcards)
        self._card_queue: deque[Flashcard] = deque(self._initial_flashcards)
        self.max_retries: int = max_retries
        self._failure_counts: Dict[int, int] = {}

    def has_remaining_cards(self) -> bool:
        """Check if remaining cards exist in adaptive queue.

        Returns:
            bool: True if cards remain in the queue, False otherwise.
        """
        return len(self._card_queue) > 0

    def get_next_card(self) -> Flashcard:
        """Get the next card from the adaptive queue.

        Returns:
            Flashcard: The next card in adaptive queue.

        Raises:
            IndexError: If no cards remain in the queue.
        """
        if not self._card_queue:
            raise IndexError("No cards remaining in quiz.")
        return self._card_queue.popleft()

    def record_answer(self, card: Flashcard, is_correct: bool) -> None:
        """Record answer outcome and re-queue card if under retry threshold.

        Args:
            card: The Flashcard answered.
            is_correct: True if correct, False otherwise.
        """
        if is_correct:
            return

        card_id = id(card)
        current_failures = self._failure_counts.get(card_id, 0) + 1
        self._failure_counts[card_id] = current_failures

        if current_failures <= self.max_retries:
            self._card_queue.append(card)


# Compatibility aliases for legacy import references
SequentialMode = SequentialQuizMode
RandomMode = RandomQuizMode
AdaptiveMode = AdaptiveQuizMode


class QuizModeFactory:
    """Factory pattern implementation for creating QuizMode instances."""

    _MODES: Dict[str, Type[QuizMode]] = {
        "sequential": SequentialQuizMode,
        "random": RandomQuizMode,
        "adaptive": AdaptiveQuizMode,
    }

    @classmethod
    def create_mode(cls, mode_name: str, flashcards: List[Flashcard]) -> QuizMode:
        """Factory method to instantiate a QuizMode based on mode name.

        Args:
            mode_name: Name of mode ('sequential', 'random', 'adaptive').
            flashcards: List of Flashcard objects for the quiz session.

        Returns:
            QuizMode: An instance of a concrete QuizMode subclass.

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
            supported_modes = ", ".join(cls._MODES.keys())
            raise ValueError(
                f"Unsupported quiz mode '{mode_name}'. "
                f"Supported modes are: {supported_modes}."
            )

        return mode_class(flashcards)
