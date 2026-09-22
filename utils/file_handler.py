"""
Data loading and validation module for flashcard data.
"""

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


def _validate_and_build_flashcard(item: Any) -> Flashcard:
    """Validate a single dictionary item and convert it to Flashcard."""
    if not isinstance(item, dict):
        raise ValueError("Flashcard item must be a JSON object (dictionary).")

    if "front" not in item or "back" not in item:
        raise KeyError("Missing required fields 'front' or 'back'.")

    front = item["front"]
    back = item["back"]

    if not isinstance(front, str) or not isinstance(back, str):
        raise ValueError("Fields 'front' and 'back' must be strings.")

    front = front.strip()
    back = back.strip()

    if not front or not back:
        raise ValueError("Fields 'front' and 'back' cannot be empty.")

    return Flashcard(front=front, back=back)


def load_flashcards(filepath: Union[str, Path]) -> List[Flashcard]:
    """Load and validate flashcards from a JSON file.

    Supports two formats:
    1. Plain list: [{"front": "...", "back": "..."}]
    2. Wrapped dict: {"cards": [{"front": "...", "back": "..."}]}

    Exits gracefully with status code 1 on errors.
    """
    path = Path(filepath)
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

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
        sys.stderr.write(f"Error: File not found at '{path}'.\n")
        sys.exit(1)
    except json.JSONDecodeError as err:
        sys.stderr.write(f"Error: Invalid JSON format in '{path}': {err}\n")
        sys.exit(1)
    except (KeyError, ValueError) as err:
        clean_msg = str(err).strip("'\"")
        sys.stderr.write(f"Error: Validation failed for '{path}': {clean_msg}\n")
        sys.exit(1)
