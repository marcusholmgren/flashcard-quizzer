"""
Unit tests for flashcard loading and validation module.
"""

import json
from pathlib import Path

import pytest

from flashcard_quizzer.utils.file_handler import Flashcard, load_flashcards


def test_load_valid_flashcards_array(tmp_path: Path) -> None:
    """Test loading a plain array list of flashcard objects."""
    file_path = tmp_path / "cards.json"
    data = [
        {"front": "What is Python?", "back": "A programming language."},
        {"front": "What is 2 + 2?", "back": "4"},
    ]
    file_path.write_text(json.dumps(data), encoding="utf-8")
    result = load_flashcards(file_path)
    assert len(result) == 2
    assert result[0] == Flashcard("What is Python?", "A programming language.")
    assert result[1] == Flashcard("What is 2 + 2?", "4")


def test_load_valid_flashcards_wrapped(tmp_path: Path) -> None:
    """Test loading a wrapped dictionary containing a 'cards' list."""
    file_path = tmp_path / "wrapped_cards.json"
    data = {"cards": [{"front": "CPU", "back": "Central Processing Unit"}]}
    file_path.write_text(json.dumps(data), encoding="utf-8")
    result = load_flashcards(file_path)
    assert len(result) == 1
    assert result[0] == Flashcard("CPU", "Central Processing Unit")


def test_load_invalid_json(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test handling of malformed JSON file."""
    file_path = tmp_path / "invalid.json"
    file_path.write_text("{invalid json content", encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        load_flashcards(file_path)
    assert exc_info.value.code == 1
    assert "Error: Invalid JSON format" in capsys.readouterr().err


def test_load_missing_required_field(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test handling of cards with missing required fields."""
    file_path = tmp_path / "missing_fields.json"
    file_path.write_text(
        json.dumps([{"front": "Only front content"}]), encoding="utf-8"
    )
    with pytest.raises(SystemExit) as exc_info:
        load_flashcards(file_path)
    assert exc_info.value.code == 1
    err = capsys.readouterr().err
    assert "Error: Validation failed" in err and "Missing required fields" in err


def test_load_empty_string_fields(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test handling of cards with empty string fields."""
    file_path = tmp_path / "empty_fields.json"
    file_path.write_text(
        json.dumps([{"front": "   ", "back": "valid back"}]), encoding="utf-8"
    )
    with pytest.raises(SystemExit) as exc_info:
        load_flashcards(file_path)
    assert exc_info.value.code == 1
    assert "cannot be empty" in capsys.readouterr().err


def test_load_file_not_found(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test handling of non-existent file."""
    with pytest.raises(SystemExit) as exc_info:
        load_flashcards(tmp_path / "non_existent.json")
    assert exc_info.value.code == 1
    assert "Error: File not found" in capsys.readouterr().err


def test_load_non_dict_item(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test handling of item in array that is not a dictionary."""
    file_path = tmp_path / "non_dict.json"
    file_path.write_text(json.dumps(["not a dict"]), encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        load_flashcards(file_path)
    assert exc_info.value.code == 1
    assert "Error: Validation failed" in capsys.readouterr().err


def test_load_non_string_field_type(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test handling of front/back fields that are not strings."""
    file_path = tmp_path / "invalid_type.json"
    file_path.write_text(
        json.dumps([{"front": 123, "back": "valid"}]), encoding="utf-8"
    )
    with pytest.raises(SystemExit) as exc_info:
        load_flashcards(file_path)
    assert exc_info.value.code == 1
    assert "Error: Validation failed" in capsys.readouterr().err


def test_load_invalid_wrapped_structure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test handling of wrapped object missing 'cards' key."""
    file_path = tmp_path / "bad_wrapper.json"
    file_path.write_text(json.dumps({"wrong_key": []}), encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        load_flashcards(file_path)
    assert exc_info.value.code == 1
    assert "Error: Validation failed" in capsys.readouterr().err


def test_load_invalid_root_type(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test handling of root JSON element that is neither list nor dict."""
    file_path = tmp_path / "bad_root.json"
    file_path.write_text(json.dumps("string root"), encoding="utf-8")
    with pytest.raises(SystemExit) as exc_info:
        load_flashcards(file_path)
    assert exc_info.value.code == 1
    assert "Error: Validation failed" in capsys.readouterr().err
