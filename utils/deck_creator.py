"""
Re-export module for utils/deck_creator.py compatibility.
"""

from flashcard_quizzer.utils.deck_creator import (
    create_deck_interactive,
    handle_existing_file,
    save_deck,
)

__all__ = ["create_deck_interactive", "handle_existing_file", "save_deck"]
