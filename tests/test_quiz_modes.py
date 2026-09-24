"""Unit tests for quiz modes and quiz mode factory (Strategy & Factory patterns)."""

from unittest.mock import patch

import pytest

from flashcard_quizzer.quiz_engine import (
    AdaptiveMode,
    AdaptiveQuizMode,
    QuizMode,
    QuizModeFactory,
    RandomMode,
    RandomQuizMode,
    SequentialMode,
    SequentialQuizMode,
)
from flashcard_quizzer.utils.file_handler import Flashcard


@pytest.fixture
def sample_cards() -> list[Flashcard]:
    """Fixture providing a list of sample Flashcard objects."""
    return [
        Flashcard("Question 1", "Answer 1"),
        Flashcard("Question 2", "Answer 2"),
        Flashcard("Question 3", "Answer 3"),
    ]


def test_quiz_mode_factory(sample_cards: list[Flashcard]) -> None:
    """Verify correct strategy instantiation and invalid mode handling in QuizModeFactory."""
    seq_mode = QuizModeFactory.create_mode("sequential", sample_cards)
    assert isinstance(seq_mode, SequentialQuizMode)
    assert isinstance(seq_mode, SequentialMode)
    assert isinstance(seq_mode, QuizMode)

    rand_mode = QuizModeFactory.create_mode("  RANDOM ", sample_cards)
    assert isinstance(rand_mode, RandomQuizMode)
    assert isinstance(rand_mode, RandomMode)

    adapt_mode = QuizModeFactory.create_mode("Adaptive", sample_cards)
    assert isinstance(adapt_mode, AdaptiveQuizMode)
    assert isinstance(adapt_mode, AdaptiveMode)

    with pytest.raises(ValueError, match="Unsupported quiz mode 'invalid_mode'"):
        QuizModeFactory.create_mode("invalid_mode", sample_cards)

    with pytest.raises(ValueError, match="Mode name must be a string"):
        QuizModeFactory.create_mode(123, sample_cards)  # type: ignore[arg-type]


def test_sequential_mode(sample_cards: list[Flashcard]) -> None:
    """Ensure exact order traversal and exhaustion in SequentialQuizMode."""
    mode = SequentialQuizMode(sample_cards)

    assert mode.has_remaining_cards() is True
    assert mode.has_next() is True
    card1 = mode.get_next_card()
    assert card1 == sample_cards[0]
    mode.record_answer(card1, True)

    assert mode.has_remaining_cards() is True
    card2 = mode.get_next_card()
    assert card2 == sample_cards[1]
    mode.record_answer(card2, False)

    assert mode.has_remaining_cards() is True
    card3 = mode.get_next_card()
    assert card3 == sample_cards[2]
    mode.record_answer(card3, True)

    assert mode.has_remaining_cards() is False
    with pytest.raises(IndexError, match="No cards remaining in quiz."):
        mode.get_next_card()


def test_random_mode(sample_cards: list[Flashcard]) -> None:
    """Verify all cards are presented in RandomQuizMode regardless of shuffle order."""
    mode = RandomQuizMode(sample_cards)

    presented_cards = []
    while mode.has_remaining_cards():
        card = mode.get_next_card()
        mode.record_answer(card, True)
        presented_cards.append(card)

    assert len(presented_cards) == len(sample_cards)
    for card in sample_cards:
        assert card in presented_cards

    assert mode.has_remaining_cards() is False
    with pytest.raises(IndexError, match="No cards remaining in quiz."):
        mode.get_next_card()


def test_random_mode_shuffling(sample_cards: list[Flashcard]) -> None:
    """Verify that random.shuffle is invoked on initial cards."""
    with patch("random.shuffle") as mock_shuffle:
        RandomQuizMode(sample_cards)
        mock_shuffle.assert_called_once()


def test_adaptive_mode_behavior(sample_cards: list[Flashcard]) -> None:
    """Explicitly verify that incorrectly answered cards are reintroduced."""
    mode = AdaptiveQuizMode(sample_cards)

    c1 = mode.get_next_card()
    assert c1 == sample_cards[0]
    mode.record_answer(c1, is_correct=False)

    c2 = mode.get_next_card()
    assert c2 == sample_cards[1]
    mode.record_answer(c2, is_correct=True)

    c3 = mode.get_next_card()
    assert c3 == sample_cards[2]
    mode.record_answer(c3, is_correct=True)

    assert mode.has_remaining_cards() is True
    reintroduced_c1 = mode.get_next_card()
    assert reintroduced_c1 == sample_cards[0]

    mode.record_answer(reintroduced_c1, is_correct=True)

    assert mode.has_remaining_cards() is False
    with pytest.raises(IndexError, match="No cards remaining in quiz."):
        mode.get_next_card()


def test_adaptive_mode_multiple_failures(sample_cards: list[Flashcard]) -> None:
    """Verify that a card failed multiple times remains in rotation until correct."""
    card = sample_cards[0]
    mode = AdaptiveQuizMode([card])

    c = mode.get_next_card()
    mode.record_answer(c, is_correct=False)
    assert mode.has_remaining_cards() is True

    c = mode.get_next_card()
    mode.record_answer(c, is_correct=False)
    assert mode.has_remaining_cards() is True

    c = mode.get_next_card()
    mode.record_answer(c, is_correct=True)
    assert mode.has_remaining_cards() is False


def test_adaptive_mode_max_retries_threshold(sample_cards: list[Flashcard]) -> None:
    """Verify AdaptiveQuizMode drops a card once max_retries limit is reached."""
    card = sample_cards[0]
    mode = AdaptiveQuizMode([card], max_retries=2)

    c1 = mode.get_next_card()
    mode.record_answer(c1, is_correct=False)
    assert mode.has_remaining_cards() is True

    c2 = mode.get_next_card()
    mode.record_answer(c2, is_correct=False)
    assert mode.has_remaining_cards() is True

    c3 = mode.get_next_card()
    mode.record_answer(c3, is_correct=False)
    assert mode.has_remaining_cards() is False


def test_empty_card_list() -> None:
    """Verify behavior when instantiated with an empty list of cards."""
    for mode_name in ["sequential", "random", "adaptive"]:
        mode = QuizModeFactory.create_mode(mode_name, [])
        assert mode.has_remaining_cards() is False
        with pytest.raises(IndexError):
            mode.get_next_card()
