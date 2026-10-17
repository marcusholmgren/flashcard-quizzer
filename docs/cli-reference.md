# CLI Reference

The Flashcard Quizzer provides a simple but powerful command-line interface.

## Application Commands

To run the application, use `uv run main.py` followed by the appropriate arguments.

| Argument | Short | Description | Required | Default |
| :--- | :---: | :--- | :---: | :---: |
| `--file` | `-f` | Path to the JSON file containing the flashcard deck. If the file does not exist, the CLI will enter creation mode. | Yes | None |
| `--mode` | `-m` | Quiz mode strategy to use. Options: `sequential`, `random`, `adaptive`. | No | `sequential` |
| `--stats` | | Flag to print detailed session statistics after the quiz is finished. | No | `False` |
| `--help` | `-h` | Show the help message and exit. | No | |

### Examples

Basic run using sequential mode:
```bash
uv run main.py -f data/python.json
```

Run in random mode with end-of-game stats:
```bash
uv run main.py -f data/python.json -m random --stats
```

## Interactive Quiz Commands

During a quiz session, you can input specific commands instead of your answer to control the flow.

| Command | Action |
| :--- | :--- |
| `q` or `quit` | Immediately exits the quiz and (if the `--stats` flag was passed) shows your current statistics. |
| `h` or `hint` | Provides a hint for the current card, if available. (Note: Depends on implementation details in future updates). |

## Interactive Deck Creation Commands

When you provide a file path via `-f` that does not exist, the app enters **Interactive Deck Creation Mode**.

During this mode, you will be prompted for a "Front" and a "Back" for each card.

| Command | Action |
| :--- | :--- |
| `done` | Type `done` when prompted for the "Front" of a card to save the deck and exit creation mode. |
