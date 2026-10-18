---
icon: lucide/pencil
---
# Prompts

These are the structured prompts used to build this flashcard-quizzer project.

## Interaction 01

[Setup Python 3.14 environment with uv and update dev tooling (#2)](https://github.com/marcusholmgren/flashcard-quizzer/commit/d000c3164bc9781be0f40dc7381204798ee1ecd2)

```text
<role>Senior Python Developer specializing in modular CLI design and clean architecture</role>

<task>
Modern Python environment with uv
</task>

<context>
    - Use uv to manage the Python environment.
</context>

<requirements>
<tech>
    - Use Python 3.14 standard library.
    - Use latest version of isort, black, flake8, mypy, bandit and safety
    - Replace shpinx with zenzical for documentation generation
    - Don't use pre-commit package
</tech>

<testing_requirements>
  Use Pytest for testing.
</testing_requirements>
</requirements>

<constraints>
- Prefer standard library over third-party packages.
</constraints>
```

## Interaction 02

[Implement flashcard loader and project structure (#3)](https://github.com/marcusholmgren/flashcard-quizzer/commit/29b11f31cc5f63f55df3776bc052bf94ca88a5da)

```text
<role>Senior Python developer following SOLID principles and clean architecture</role>

<task>
    Move Python files and use a default uv project structure.
    Implement the data loading and validation module in utils/file_handler.py, along with complete unit tests in tests/test_flashcard_loader.py.
</task>

<context>
Building the data layer for a Flashcard Quizzer CLI app managed via `uv`.
Target files:
- utils/file_handler.py
- tests/test_flashcard_loader.py
</context>

<requirements>
<folder_structure>
    ├── pyproject.toml
    ├── README.md
    └── src
        └── flashcard-quizzer
            └── __init__.py    
</folder_structure>
<functional_requirements>
- Support two JSON formats:
  1. Plain list of dictionaries: [{"front": "...", "back": "..."}]
  2. Wrapped dictionary: {"cards": [{"front": "...", "back": "..."}]}
- Provide type hints on all functions.
- Define a Flashcard dataclass or named tuple for strong typing.
- Return a List[Flashcard] on successful parse.
</functional_requirements>

<error_handling>
- Handle FileNotFoundError, json.JSONDecodeError, and KeyError/ValueError (missing fields or empty strings).
- Print a clear, formatted error message to stderr and exit gracefully with code 1 without printing a raw stack trace.
</error_handling>

<testing_requirements>
- Use pytest in tests/test_flashcard_loader.py.
- Implement test_load_valid_flashcards_array.
- Implement test_load_invalid_json.
- Implement test_load_missing_required_field.
</testing_requirements>
</requirements>

<constraints>
- Adhere strictly to PEP 8.
- Use Python standard library (json, dataclasses, typing, sys, pathlib).
- Keep code clean, modular, and under 150 lines per file.
</constraints>
```

## Interaction 03

[Refactor package structure and add GitHub Actions CI workflow (#4)](https://github.com/marcusholmgren/flashcard-quizzer/commit/c2a8e632274b5c601fbf6a03ad83a3e355162d4d)

```text
<role>Senior Python developer following SOLID principles and clean architecture</role>

<task>
    Move python files `main.py` and the `utils/` package for into the `src/flashcard-quizzer` directory.
    Leave the `tests/` directory in the root directory.

    Add `[project.scripts]` to the `pyproject.toml` file for running the project as a script.

    Add GitHub Actions workflow that runs on main branch and for pull requests.
</task>
```

## Interaction 04

[Implement core quiz engine using Strategy and Factory patterns (#5)](https://github.com/marcusholmgren/flashcard-quizzer/commit/26d4f53c0be28df09f1036433a9b27efe359a360)

```text
<role>Senior Python Developer specializing in object-oriented design and design patterns</role>

<task>
Implement the core quiz engine in quiz_engine.py using the Strategy Pattern and Factory Pattern, along with comprehensive unit tests in tests/test_quiz_modes.py.
</task>

<context>
Flashcard Quizzer CLI application managed via uv.
Target files:
- quiz_engine.py
- tests/test_quiz_modes.py
Prerequisites: Flashcard data model exists in utils/file_handler.py.
</context>

<requirements>
<architecture_and_patterns>
- Implement the Strategy Pattern for quiz modes using an abstract base class QuizMode (inheriting from abc.ABC).
- QuizMode must define abstract methods for serving cards and processing outcomes, such as:
  - has_next() -> bool
  - get_next_card() -> Flashcard
  - record_answer(card: Flashcard, is_correct: bool) -> None
- Concrete strategy classes to implement:
  1. SequentialMode: Presents cards in their initial order (1 to N).
  2. RandomMode: Shuffles cards randomly before or during presentation.
  3. AdaptiveMode: Tracks card performance and prioritizes or re-queues cards answered incorrectly.
- Implement the Factory Pattern via QuizModeFactory:
  - Provide a factory method (e.g., create_mode(mode_name: str, cards: List[Flashcard]) -> QuizMode).
  - Handle case-insensitive mode names ("sequential", "random", "adaptive").
  - Raise a clean ValueError with supported choices when passed an unknown mode name.
</architecture_and_patterns>

<type_safety>
- Include Python type hints on all classes, methods, and functions.
- Import Flashcard from utils.file_handler.
</type_safety>

<testing_requirements>
- Write pytest tests in tests/test_quiz_modes.py targeting at least 90% coverage on quiz_engine.py.
- Include test_quiz_mode_factory verifying correct strategy instantiation and invalid mode handling.
- Include test_sequential_mode ensuring exact order traversal.
- Include test_random_mode verifying all cards are presented.
- Include test_adaptive_mode_behavior explicitly verifying that incorrectly answered cards are reintroduced or prioritized over mastered cards.
</testing_requirements>
</requirements>

<constraints>
- Strict adherence to PEP 8.
- Pure Python standard library for core logic (abc, random, collections, typing).
- Do not include CLI rendering or user input handling inside quiz_engine.py; keep it strictly domain logic.
- Keep each class cohesive, adhering to Single Responsibility and Open/Closed principles.
</constraints>
```

## Interaction 05

[Implement CLI presentation, interaction loop, and integration tests (#6)](https://github.com/marcusholmgren/flashcard-quizzer/commit/7feba0ae24d6ea5871a30bd745cee6be6620e10c)

```text
<role>Senior Python Developer specializing in CLI user experience and test-driven architecture</role>

<task>
Implement the command-line interface, user interaction loop, and session summary reporting across main.py and ui.py, along with full end-to-end integration tests in tests/test_integration.py.
</task>

<context>
Building the presentation and CLI orchestration layer for the Flashcard Quizzer application.
Dependencies already implemented:
- utils/file_handler.py (data loading and validation)
- quiz_engine.py (QuizMode Strategy and QuizModeFactory)
Target files:
- ui.py (terminal rendering, colors, and user input handling)
- main.py (entry point and argparse configuration)
- tests/test_integration.py (pytest end-to-end simulation)
</context>

<requirements>
<cli_specifications>
- Use argparse in main.py supporting flags:
  - -f or --file: path to JSON flashcard deck (required).
  - -m or --mode: quiz mode ("sequential", "random", "adaptive") with default "sequential".
  - --stats: flag to toggle final summary presentation (default True).
- Implement clean exception handling: if loading or factory initialization fails, display friendly console messages and exit with status code 1.
</cli_specifications>

<interaction_loop>
- Keep ui.py responsible for terminal output and input formatting.
- Present the "Front" text of each flashcard to the user.
- Accept user text input and compare it case-insensitively against the "Back" text.
- Provide immediate colored terminal feedback:
  - Green for correct answers.
  - Red for incorrect answers (showing the expected back).
  - Use rich for cross-platform ANSI color support.
- Support clean termination:
  - If user inputs "exit" or triggers KeyboardInterrupt (Ctrl+C), exit cleanly without raising a Python traceback.
- Record each response into the active QuizMode strategy.
</interaction_loop>

<session_summary>
- At the end of the session, display a summary report:
  - Total Questions Answered
  - Accuracy Percentage (formatted to 1 decimal place)
  - List of missed terms (front and expected back)
</session_summary>

<testing_requirements>
- In tests/test_integration.py, use pytest and unittest.mock (e.g., monkeypatch or patch for sys.argv, input, and print) to verify:
  1. test_full_session: Simulate a multi-card session, user inputs, and check final output calculation.
  2. test_graceful_exit: Verify typing "exit" or triggering KeyboardInterrupt terminates with status code 0.
  3. test_cli_argument_parsing: Verify arguments route correctly to file loaders and mode factories.
</testing_requirements>
</requirements>

<constraints>
- Adhere strictly to PEP 8.
- Separate CLI rendering (ui.py) from CLI entry orchestration (main.py).
- No uncaught exceptions or raw Python tracebacks displayed to the user.
</constraints>
```

## Interaction 06

[Add interactive deck creator module and CLI subcommand/flag (#7)](https://github.com/marcusholmgren/flashcard-quizzer/commit/38220b15cb9781803550ad26c91c3ad128247b08)

```text
<role>Senior Python Developer specializing in CLI user interaction and reliable file I/O</role>

<task>
Implement an interactive deck creator module in utils/deck_creator.py with a corresponding CLI subcommand/option, along with full unit tests in tests/test_deck_creator.py.
</task>

<context>
Flashcard Quizzer CLI application managed via uv.
Target files:
- utils/deck_creator.py
- tests/test_deck_creator.py
- main.py (wire up a new command or flag, e.g., `create` or `--create`)
Dependencies: utils/file_handler.py (Flashcard data structure and JSON file loader).
</context>

<requirements>
<file_handling>
- Accept a destination file path from the user.
- If the target file already exists:
  - Prompt: "[O]verwrite, [A]ppend, or [C]ancel? "
  - "Overwrite": Clear existing cards and start fresh.
  - "Append": Read existing flashcards using utils.file_handler, retain them, and append new cards to the collection.
  - "Cancel": Abort cleanly without modifying the file.
- If the file does not exist, create necessary parent directories and initialize a new deck.
- Persist the resulting cards formatted cleanly as JSON matching the app's supported schema (e.g., {"cards": [{"front": "...", "back": "..."}]}).
</file_handling>

<input_loop_ux>
- Guide the user clearly before entering the loop:
  - Explain that pressing [Enter] with an empty Front or typing "done" saves and finishes.
  - Explain that typing "exit" cancels and prompts to discard or save.
- Prompt sequence per card:
  1. Front: Prompt for front text.
     - If user enters empty string or "done" (case-insensitive): break loop and trigger save.
     - If user enters "exit": ask whether to save cards created so far (y/n).
  2. Back: Prompt for back text.
     - Validate that Back is not empty. If empty, warn and re-prompt for Back without resetting the Front.
- Provide a running counter (e.g., "[Card 1]", "[Card 2]") for clear progress tracking.
- Handle KeyboardInterrupt (Ctrl+C) gracefully by confirming exit rather than throwing a traceback.
</input_loop_ux>

<testing_requirements>
- Write pytest tests in tests/test_deck_creator.py using `monkeypatch` and `tmp_path`.
- test_create_new_deck: Verify writing new cards to a non-existent path.
- test_append_existing_deck: Verify appending new cards preserves previous cards.
- test_overwrite_existing_deck: Verify overwrite replaces prior content.
- test_exit_conditions: Verify loop termination on "done", empty string, and "exit".
</testing_requirements>
</requirements>

<constraints>
- Adhere strictly to PEP 8 with explicit type hints.
- Do not lose user-entered data on unexpected errors; save safely using atomic file writing or standard json.dump with error traps.
- Keep terminal output clean, readable, and consistent with the rest of the application styling.
</constraints>
```

## Interaction 07

[Refactor dependencies, naming clarity, and edge cases (#8)](https://github.com/marcusholmgren/flashcard-quizzer/commit/1bca64dcd06f021e0cc3dca688bd366ef7d0144c)

```text
<role>Principal Python Software Engineer and Code Reviewer</role>

<task>
Perform a dependency audit, codebase refactor for naming clarity and documentation, and implement missing edge cases across the Flashcard Quizzer repository.
</task>

<context>
Flashcard Quizzer CLI project managed via uv.
Target files:
- pyproject.toml
- main.py
- ui.py
- quiz_engine.py
- utils/file_handler.py
- utils/deck_creator.
- tests/
</context>

<requirements>
<dependency_audit>
- Scan all Python files (.py) for external import statements (e.g., `rich`, `colorama`).
- Ensure all direct third-party runtime imports are explicitly listed under `dependencies` in `pyproject.toml`.
- Ensure testing and linting tools (`pytest`, `pytest-cov`, `flake8`) are classified under dev dependencies.
- Update `pyproject.toml` and synchronize the lockfile using `uv`.
</dependency_audit>

<naming_clarity_and_readability>
- Audit variable, function, and class identifiers across all modules:
  - Replace ambiguous single-letter or abbreviated variables (e.g., `c`, `idx`, `res`, `q_m`) with expressive domain names (e.g., `card`, `card_index`, `result`, `quiz_strategy`).
  - Ensure boolean flags and methods are framed descriptively (e.g., `is_valid`, `has_remaining_cards()`, `should_record_stats`).
  - Verify that Strategy and Factory class names follow standard conventions (`QuizMode`, `AdaptiveQuizMode`, `QuizModeFactory`).
- Eliminate redundant or convoluted logic; keep functions under 25 lines where feasible adhering to Single Responsibility.
</naming_clarity_and_readability>

<documentation_and_typing>
- Verify that every class, public method, and standalone function has a PEP 257 compliant docstring explaining:
  - Purpose and behavior
  - Args, Types, and Return values
  - Raised exceptions
- Ensure 100% Python type hints coverage across function signatures.
</documentation_and_typing>

<edge_case_hardening>
- Implement and verify safeguards against:
  1. Empty decks: Display a clean error and exit gracefully with code 1 if a deck has 0 cards.
  2. Division by zero: Ensure stats calculation handles 0 questions answered without crashing.
  3. Whitespace handling: Normalize both user input and card answers by trimming whitespace prior to comparison.
  4. Adaptive mode bounds: Ensure the adaptive queue terminates cleanly when cards are mastered or reaches a defined repeat threshold.
  5. Deck creation: Handle invalid destination paths and empty inputs reliably.
</edge_case_hardening>

<test_verification>
- Add new test cases in tests/ targeting every edge case above.
- Run `uv run pytest --cov=. --cov-report=term-missing` and ensure code coverage remains above 85%.
- Run `uv run flake8 .` to guarantee zero PEP 8 linting errors.
</test_verification>
</requirements>

<constraints>
- Do not introduce breaking CLI interface changes.
- Never output raw Python tracebacks to the user.
- Keep output modular across the existing file structure.
</constraints>
```

## Interaction 08

[Zensical Documentation Site and GitHub Actions Workflow Consolidation (PR #9 & PR #10)](https://github.com/marcusholmgren/flashcard-quizzer/commit/752916ff03e9129f81657b41f100294ea7a00848)

```text
<role>Technical Writer and Senior Python Developer</role>

<task>
Create a comprehensive, production-ready README.md and set up the documentation structure using Zensical for GitHub Pages deployment.
</task>

<context>
Flashcard Quizzer CLI project managed via `uv` for the Udacity AI-Powered Software Engineer Nanodegree.
Target files to generate or update:
- README.md
- zensical.toml (or config/entry point required by Zensical)
- docs/index.md
- docs/getting-started.md
- docs/architecture.md
- docs/cli-reference.md
- .github/workflows/deploy-docs.yml (GitHub Actions workflow to publish via GitHub Pages)
</context>

<requirements>
<readme_specifications>
Update `README.md` to serve as the project gateway, including:
1. Project Title & Overview:
   - High-level pitch of the Flashcard Quizzer CLI.
   - Core design highlights (Strategy & Factory design patterns, modular architecture, type safety).
2. Features List:
   - Three quiz modes: Sequential, Random, and Adaptive (repeat missed cards).
   - Dual JSON format support (array and wrapped object formats) with strict error handling.
   - Rich terminal UI with colorized feedback and detailed session statistics.
   - Interactive deck creation (overwrite, append, cancel workflows).
3. Quickstart & Setup:
   - Prerequisites (`uv` installed).
   - Cloning, environment sync (`uv sync`), and direct execution instructions via `uv run`.
4. Usage Examples:
   - Starting a quiz: `uv run main.py -f data/python_basics.json -m adaptive`.
   - Creating/updating a deck: commands and interactive prompt tips.
5. Development & Testing:
   - Running test suite: `uv run pytest`.
   - Generating coverage report: `uv run pytest --cov=. --cov-report=html`.
   - Code formatting & linting: `uv run flake8 .`.
6. Documentation Link:
   - Explicit callout to the live Zensical GitHub Pages site.
</readme_specifications>

<zensical_site_structure>
Set up the documentation content inside `docs/`:
- `docs/index.md`: Overview, project objectives, and high-level feature matrix.
- `docs/getting-started.md`: Step-by-step installation, dependency management with `uv`, and sample data files.
- `docs/architecture.md`:
  - Detailed explanation of the Strategy Pattern (`QuizMode`, `SequentialMode`, `RandomMode`, `AdaptiveMode`).
  - Explanation of the Factory Pattern (`QuizModeFactory`).
  - Separation of concerns between CLI UI, engine, and data layers (`ui.py`, `quiz_engine.py`, `utils/file_handler.py`).
- `docs/cli-reference.md`: Complete table of CLI arguments (`-f`, `-m`, `--stats`, interactive exit commands).
</zensical_site_structure>

<github_pages_workflow>
Create `.github/workflows/deploy-docs.yml`:
- Trigger on pushes to the default branch (e.g., `main`).
- Set up Python and `uv`.
- Install dependencies and build documentation via Zensical CLI.
- Upload GitHub Pages artifact and trigger deployment via `actions/deploy-pages`.
</github_pages_workflow>
</requirements>

<constraints>
- Keep Markdown cleanly formatted with consistent heading hierarchies.
- Ensure all commands use `uv run` to match project conventions.
- Do not hardcode machine-specific paths.
- Ensure the setup satisfies the project rubric for clear setup instructions and architecture documentation.
</constraints>
```
