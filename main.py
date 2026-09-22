"""
Main entry point for Flashcard Quizzer CLI application.
"""

from utils.file_handler import load_flashcards


def main() -> None:
    """Main function to run the Flashcard Quizzer CLI."""
    print("Welcome to Flashcard Quizzer!")
    cards = load_flashcards("data/sample_flashcards.json")
    print(f"Loaded {len(cards)} flashcards.")


if __name__ == "__main__":
    main()
