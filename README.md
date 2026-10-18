# Flashcard Quizzer

[![CI](https://github.com/marcusholmgren/flashcard-quizzer/actions/workflows/ci.yml/badge.svg)](https://github.com/marcusholmgren/flashcard-quizzer/actions/workflows/ci.yml)

A powerful, terminal-based Flashcard Quizzer CLI designed for practicing and memorizing new concepts.

Developed as part of the Udacity AI-Powered Software Engineer Nanodegree, this tool showcases robust software engineering principles including the **Strategy Pattern** for quiz modes, the **Factory Pattern** for mode instantiation, a modular architecture, and strict type safety.

## Documentation

Full documentation is available on [GitHub Pages](https://marcusholmgren.github.io/flashcard-quizzer/).

## Features

- **Three Quiz Modes:**
  - **Sequential:** Go through cards in their original order.
  - **Random:** Shuffle the deck for a varied learning experience.
  - **Adaptive:** Intelligently repeats missed cards until mastered.
- **Flexible Data Formats:** Supports dual JSON formats (array format and wrapped object format) with strict error handling.
- **Rich Terminal UI:** Enjoy a beautiful, colorized interface with detailed session statistics via the `rich` library.
- **Interactive Deck Creation:** Easily create and update decks with intuitive interactive workflows (overwrite, append, cancel).

## Quickstart & Setup

### Prerequisites
- Install `uv`, the extremely fast Python package and project manager.

### Installation
Clone the repository and sync the environment:

```bash
git clone https://github.com/marcusholmgren/flashcard-quizzer.git
cd flashcard-quizzer
uv sync
```

## Usage Examples

Run the application directly using `uv run`.

**Start a quiz with the adaptive mode:**
```bash
uv run flashcard-quizzer -f data/greek_mythology.json -m adaptive
```

**View stats after finishing:**
```bash
uv run flashcard-quizzer -f data/greek_mythology.json -m random --stats
```

**Create a new deck interactively:**
```bash
uv run flashcard-quizzer -f data/my_new_deck.json --create
```
If the file doesn't exist, the CLI will guide you through creating it, allowing you to append or overwrite cards interactively.

## Development & Testing

This project uses `uv` for seamless dependency management and task execution.

- **Run test suite:**
  ```bash
  uv run pytest
  ```
- **Generate coverage report:**
  ```bash
  uv run pytest --cov=. --cov-report=html
  ```
- **Code formatting & linting:**
  ```bash
  uv run flake8 .
  uv run black .
  uv run isort .
  ```
- **Type Checking:**
  ```bash
  uv run mypy src/.
  ```
