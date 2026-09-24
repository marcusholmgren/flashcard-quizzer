"""Data loading and validation module for flashcard data."""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Union


@dataclass
class Flashcard:
    """Represents a flashcard with front and back text content."""

    front: str
    back: str


def _validate_and_build_flashcard(raw_item: Any) -> Flashcard:
    """Validate a single dictionary item and convert it to Flashcard.

    Args:
        raw_item: Object expected to be a valid flashcard dictionary.

    Returns:
        Flashcard: Validated Flashcard instance with trimmed whitespace.

    Raises:
        ValueError: If raw_item is not a dict, or fields are not non-empty strings.
        KeyError: If required keys 'front' or 'back' are missing.
    """
    if not isinstance(raw_item, dict):
        raise ValueError("Flashcard item must be a JSON object (dictionary).")

    if "front" not in raw_item or "back" not in raw_item:
        raise KeyError("Missing required fields 'front' or 'back'.")

    front_text = raw_item["front"]
    back_text = raw_item["back"]

    if not isinstance(front_text, str) or not isinstance(back_text, str):
        raise ValueError("Fields 'front' and 'back' must be strings.")

    front_text = front_text.strip()
    back_text = back_text.strip()

    if not front_text or not back_text:
        raise ValueError("Fields 'front' and 'back' cannot be empty.")

    return Flashcard(front=front_text, back=back_text)


def load_flashcards(filepath: Union[str, Path]) -> List[Flashcard]:
    """Load and validate flashcards from a JSON file.

    Supports two formats:
    1. Plain list: [{"front": "...", "back": "..."}]
    2. Wrapped dict: {"cards": [{"front": "...", "back": "..."}]}

    Args:
        filepath: Path to JSON flashcard deck file.

    Returns:
        List[Flashcard]: List of validated Flashcard objects.

    Raises:
        SystemExit: Gracefully exits with status code 1 on errors.
    """
    target_path = Path(filepath)
    try:
        with target_path.open("r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)

        if isinstance(data, dict):
            if "cards" not in data or not isinstance(data["cards"], list):
                raise KeyError("Wrapped JSON format must contain a 'cards' list.")
            items = data["cards"]
        elif isinstance(data, list):
            items = data
        else:
            raise ValueError("Root JSON element must be a list or object with 'cards'.")

        return [_validate_and_build_flashcard(item) for item in items]

    except FileNotFoundError:
        sys.stderr.write(f"Error: File not found at '{target_path}'.\n")
        sys.exit(1)
    except json.JSONDecodeError as json_error:
        sys.stderr.write(
            f"Error: Invalid JSON format in '{target_path}': {json_error}\n"
        )
        sys.exit(1)
    except (KeyError, ValueError) as validation_error:
        clean_message = str(validation_error).strip("'\"")
        sys.stderr.write(
            f"Error: Validation failed for '{target_path}': {clean_message}\n"
        )
        sys.exit(1)
