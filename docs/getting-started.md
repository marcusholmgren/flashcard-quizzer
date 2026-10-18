---
icon: lucide/square-play
---
# Getting Started

Follow these steps to set up the Flashcard Quizzer on your local machine.

## Prerequisites

The project strictly utilizes `uv` for dependency management and running the application. Make sure you have `uv` installed.

If you don't have `uv` installed, check their [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/marcusholmgren/flashcard-quizzer.git
   cd flashcard-quizzer
   ```

2. **Sync the environment:**
   Use `uv` to create the virtual environment and install dependencies based on the `uv.lock` file.
   ```bash
   uv sync
   ```

## Sample Data Files

The application requires flashcards to be stored in JSON format. It supports two different structures.

**Format 1: Array of Objects**
```json
[
  {
    "front": "What does HTTP stand for?",
    "back": "HyperText Transfer Protocol"
  },
  {
    "front": "What is 1 + 1?",
    "back": "2"
  }
]
```

**Format 2: Wrapped Object**
```json
{
  "cards": [
    {
      "front": "What does HTTP stand for?",
      "back": "HyperText Transfer Protocol"
    }
  ]
}
```

Store your decks in the `data/` directory (or anywhere on your machine).

## Running Your First Quiz

Once you have a JSON file ready, you can start the application:

```bash
uv run flashcard-quizzer -f data/greek_mythology.json -m sequential
```

For more details on commands and flags, see the [CLI Reference](cli-reference.md).
