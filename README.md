# flashcard-quizzer

Command line tool for practicing and memorizing new concepts.

## Setup and Development

This project uses `uv` for Python 3.14 virtual environment and dependency management.

### Commands

- **Run Application:** `uv run flashcard-quizzer` (or `uv run python src/flashcard_quizzer/main.py`)
- **Run Tests:** `uv run pytest`
- **Format Code:** `uv run black .`
- **Sort Imports:** `uv run isort .`
- **Lint Code:** `uv run flake8 .`
- **Type Check:** `uv run mypy .`
- **Security Check:** `uv run bandit -r src`
- **Vulnerability Check:** `uv run safety check`
- **Documentation:** Built using `zenzical` in `docs/`
