---
icon: lucide/pilcrow
---
# AI-Assisted Development Project Report

**Student Name:** Marcus Holmgren  
**Project Title:** Flashcard Quizzer  
**Date:** 2026-10-18  

## Executive Summary

**Flashcard Quizzer** is a modular Python 3 command-line application built to help learners practice, memorize, and author study decks directly from the terminal. Extending the course starter template into a production-packaged CLI tool managed with `uv`, the application supports loading decks from multiple JSON schemas, studying flashcards across three interchangeable quizzing algorithms (`sequential`, `random`, and `adaptive`), viewing colorized real-time feedback and end-of-session performance metrics, and interactively creating or appending to flashcard decks from the command line.

Architecturally, the project emphasizes clean separation of concerns and minimal reliance on third-party libraries. Core domain logic in `quiz_engine.py` implements the **Strategy Pattern** (`QuizMode` and its concrete strategies) and the **Factory Pattern** (`QuizModeFactory`) using only the Python standard library, keeping terminal rendering (`ui.py`), CLI orchestration (`main.py`), and file I/O (`utils/file_handler.py` and `utils/deck_creator.py`) strictly decoupled. The only runtime third-party dependency is `rich`, used exclusively in the presentation layer for cross-platform ANSI terminal styling.

Throughout development, I collaborated with three AI tools in distinct roles: **Gemini** to help structure XML-tagged prompts, **Google Jules** as an autonomous coding agent that executed prompts and opened GitHub Pull Requests, and **Google Antigravity** as a local agentic pair-programmer for diagnosing packaging issues and consolidating CI/CD workflows. Every AI-generated pull request was checked out locally, verified against automated quality gates (`pytest`, `black`, `isort`, `flake8`, `mypy`, `bandit`, and `safety`), and manually smoke-tested—revealing key lessons about the gap between passing unit tests and shipping well-architected software.

---

## Project Overview

### Problem Statement

Learners studying programming concepts, terminology, or general trivia often need a fast, distraction-free way to drill flashcards using active recall and spaced-repetition principles without setting up a heavy web or desktop application. Existing command-line scripts are frequently monolithic, hardcode a single traversal order, crash with raw tracebacks on malformed JSON files, or lack a built-in way to author and append new cards cleanly.

Flashcard Quizzer addresses this need by providing a resilient, zero-configuration CLI tool that validates user decks defensively, adapts dynamically to the learner's mistakes during a study session, and includes an interactive deck builder with safe overwrite/append workflows.

### Solution Approach

My solution approach centered on four engineering pillars:

- **Restrict Usage of Third-Party Dependencies:** I deliberately constrained the runtime footprint to the Python 3.14 standard library (`abc`, `argparse`, `collections.deque`, `dataclasses`, `json`, `pathlib`, `random`, `sys`, `typing`) for all core logic, data validation, and file persistence. Only a single runtime package (`rich>=13.0.0`) was permitted for terminal color output, minimizing supply-chain risk and keeping environment synchronization fast.
- **Clean Architecture & Separation of Concerns:** The codebase was refactored from a flat starter script into the `src/flashcard_quizzer/` package divided into four layers:
 
    1. **Data Layer (`utils/file_handler.py`, `utils/deck_creator.py`):** Defines the `Flashcard` dataclass, parses both plain array and wrapped `{"cards": [...]}` JSON files, and persists user-created decks.
    2. **Domain Engine (`quiz_engine.py`):** Encapsulates card scheduling and answer tracking behind the `QuizMode` Strategy interface and `QuizModeFactory`, with zero terminal or `input()` dependencies.
    3. **Presentation Layer (`ui.py`):** Handles colored feedback, user prompts, and formatted session statistics.
    4. **CLI Orchestration (`main.py`, `__main__.py`):** Parses CLI arguments (`-f/--file`, `-m/--mode`, `--stats`, `--create`, and the `create` subcommand) and coordinates the quiz and deck-creation loops.

- **Modern Tooling & Automated CI/CD:** Dependency locking and virtual environments are managed deterministically via `uv` (`pyproject.toml` and `uv.lock`). Two GitHub Actions workflows enforce continuous integration (`ci.yml` running formatting, linting, static typing, security checks, and unit tests on every push/PR) and continuous documentation deployment (`docs.yml` publishing the **Zensical** documentation site to GitHub Pages).

### Final Features

- [x] **Dual-Schema JSON Flashcard Loader (`utils/file_handler.py`):** Supports both plain list (`[{"front": "...", "back": "..."}]`) and wrapped dictionary (`{"cards": [...]}`) JSON formats with strict validation for missing keys, empty strings, and empty decks, exiting cleanly with status code `1` on errors.
- [x] **Three Pluggable Quiz Modes (`quiz_engine.py`):**

    - `SequentialQuizMode`: Traverses flashcards in their original deck order (`1..N`).
    - `RandomQuizMode`: Shuffles the deck before presenting cards.
    - `AdaptiveQuizMode`: Prioritizes and re-queues incorrectly answered flashcards until the user masters them or reaches a configurable repeat cap (`max_repeats=3`).

- [x] **Interactive CLI Quiz Loop & Session Analytics (`main.py`, `ui.py`):** Case-insensitive and whitespace-normalized answer checking, immediate green/red terminal feedback via `rich`, graceful exit handling (`exit`, `Ctrl+C`, `EOFError`) without tracebacks, and a end-of-session summary displaying total questions answered, accuracy percentage, and missed terms.
- [x] **Interactive Deck Creator (`utils/deck_creator.py`):** Supports creating new JSON decks or modifying existing files via an interactive `[O]verwrite, [A]ppend, or [C]ancel?` workflow, complete with a running card counter (`[Card 1]`), empty-back re-prompting, and save confirmation on early exit.
- [x] **Zensical Documentation Site & Custom Decks (`docs/`, `data/`):** Complete project documentation deployed to GitHub Pages alongside curated study decks (`data/greek_mythology.json`, `data/earth.json`, and `data/sample_flashcards.json`).

---

## AI Collaboration Experience

### AI Tools Used

- [ ] Claude  
- [ ] GitHub Copilot  
- [ ] ChatGPT  
- [x] [Gemini](https://gemini.google.com/) with 3.8 Flash  
- [x] [Jules](https://jules.google.com/) with Gemini 3.6 Flash  
- [x] [Antigravity](https://antigravity.google/) with Gemini 3.8 Flash  
- [ ] Other:  

### Collaboration Workflow

1. **Structuring Prompts:** I organized development into 8 sequential milestones documented in `docs/prompts.md`. Using XML-style tags (`<role>`, `<task>`, `<context>`, `<requirements>`, `<testing_requirements>`, and `<constraints>`), each prompt specified the target files, architectural patterns, error-handling expectations, and required `pytest` cases.
2. **Task Delegation:** For this project, I forced myself to write prompts for almost all tasks. Only the initial setup of the GitHub repository, starter template, and custom JSON quiz datasets was done manually. At times, this strict prompt-only constraint was frustrating and is not how I would work on every task in the future—because there has to be a clear return on investment for writing a detailed prompt. When an issue is trivial—such as adding a missing `rich` dependency to `pyproject.toml`—and I already know Python and how to run `uv add rich` in two seconds, tying my hands behind my back and bringing out an AI sledgehammer to fix a one-line configuration issue feels counterproductive.
3. **Review and Validation Process:** Because every prompt submitted to Jules generated a GitHub Pull Request, I treated myself as the lead maintainer reviewing a developer's PR. For every PR, I fetched and checked out the branch locally, inspected the `git diff`, ran the unit test suite (`uv run pytest`), and manually executed the CLI application to verify the behavior in real terminal usage.
4. **Refining AI Suggestions:** When local verification exposed architectural flaws or runtime bugs, I either issued a targeted follow-up prompt in the PR (for example, when Jules pushed empty documentation files in PR `#9`), encoded the fix into a dedicated refactoring prompt (interaction 7 for dependency auditing and edge cases), or switched to **Antigravity** locally on the PR branch for interactive debugging (such as fixing the PEP 517 build system in PR `#4` and merging duplicate GitHub Actions workflows in PR `#10`).

### Most Valuable AI Interactions

#### Example 1

Implementing the Quiz Engine with Strategy and Factory Patterns (PR #5)

- **Context:** I needed to build the core quizzing domain logic in `src/flashcard_quizzer/quiz_engine.py` supporting sequential, random, and adaptive card scheduling without coupling the logic to terminal `input()` or `print()` calls.
- **AI Prompt Interaction 4:** Instructed Jules to implement an abstract `QuizMode` base class (`has_next()`, `get_next_card()`, `record_answer()`), three concrete strategy classes (`SequentialMode`, `RandomMode`, `AdaptiveMode`), and `QuizModeFactory.create_mode()` using only the Python standard library, plus unit tests in `tests/test_quiz_modes.py` with >90% coverage.
- **AI Response:** Jules created `src/flashcard_quizzer/quiz_engine.py` (165 lines) using `abc.ABC` and `collections.deque` for the adaptive re-queueing logic, along with 157 lines of unit tests achieving 96% coverage on `quiz_engine.py`.
- **Your Changes:** While the engine implementation and unit tests were excellent, Jules did not export the new strategy and factory classes in `src/flashcard_quizzer/__init__.py`. I updated `__init__.py` to expose the public API (`QuizMode`, `SequentialMode`, `RandomMode`, `AdaptiveMode`, `QuizModeFactory`) and added the CI badge to `README.md`.
- **Outcome:** A clean, extensible domain engine that met the Open/Closed and Single Responsibility principles and integrated seamlessly with the CLI layer in the next milestone.

#### Example 2

Diagnosing Packaging & Entry-Point Failures with Antigravity (PR #4)

- **Context:** In Prompt Interaction 3, I asked Jules to move `main.py` and `utils/` into `src/flashcard_quizzer/`, configure `[project.scripts]` in `pyproject.toml`, and add a GitHub Actions CI workflow.
- **AI Prompt Interaction 3 + Antigravity follow-up:** After Jules opened PR `#4` (with all CI checks passing), I checked out the branch locally and ran `uv run python src/flashcard_quizzer/main.py` and `uv run flashcard-quizzer`. Both failed (`ModuleNotFoundError: No module named 'flashcard_quizzer'`). I prompted Antigravity locally: *"The structure of this python app was refactored and utils was moved into the flashcard_quizzer structure. It looks like there are incorrect imports because I cant run `uv run flashcard-quizzer` or `uv run python src/flashcard_quizzer/main.py`. Please investigate and fix imports."*
- **AI Response:** Antigravity diagnosed that the imports in `main.py` were actually valid, and `pytest` only passed because `pythonpath = ["src"]` was configured in `[tool.pytest.ini_options]`. The real root cause was that `pyproject.toml` lacked a `[build-system]` declaration (`hatchling`), causing `uv sync` to skip installing the package in editable mode and skip registering `[project.scripts]`.
- **Your Changes:** With Antigravity, I added `[build-system]` (`requires = ["hatchling"]`, `build-backend = "hatchling.build"`) to `pyproject.toml`, added `src/flashcard_quizzer/__main__.py`, deleted the leftover hyphenated `src/flashcard-quizzer/` and root `utils/` directories, created `data/sample_flashcards.json`, and added `tests/test_main.py`.
- **Outcome:** All three invocation methods (`uv run flashcard-quizzer`, `uv run python -m flashcard_quizzer`, and `uv run python src/flashcard_quizzer/main.py`) executed cleanly.

#### Example 3

Interactive Deck Creator with Overwrite/Append Workflows (PR #7)

- **Context:** To provide full CRUD capabilities for flashcard decks, I wanted an interactive CLI workflow (`--create` / `create`) allowing users to author new decks or append cards to existing JSON files safely.
- **AI Prompt Interaction 6:** Specified file-existence handling (`[O]verwrite, [A]ppend, or [C]ancel?`), a guided card-entry loop with running progress counters (`[Card 1]`), non-empty back validation without resetting the front text, `"done"` and `"exit"` save confirmations, and `monkeypatch`/`tmp_path` tests in `tests/test_deck_creator.py`.
- **AI Response:** Jules implemented `src/flashcard_quizzer/utils/deck_creator.py` (182 lines), wired `--create` and `create` into `main.py`, and wrote 273 lines of unit tests covering every interactive branch.
- **Your Changes:** Because my prompt's `<context>` referenced `utils/deck_creator.py` instead of `src/flashcard_quizzer/utils/deck_creator.py`, Jules also created a redundant compatibility wrapper in a root `utils/` directory. During later refactoring, I ensured all imports pointed strictly to `src/flashcard_quizzer/utils/deck_creator.py`.
- **Outcome:** A user-friendly, fault-tolerant deck authoring feature with comprehensive automated test coverage.

#### Example 4

Codebase-Wide Dependency Audit and Edge-Case Hardening (PR #8)

- **Context:** During my review of PR `#6` (interaction 5), I noticed that Jules used `rich` in `ui.py` without adding `rich` to `pyproject.toml`—it only worked because `safety` (a dev tool) pulled `rich` into `uv.lock` transitively. I also wanted to harden edge cases across all modules.
- **AI Prompt Interaction 7:** Asked Jules to perform a `<dependency_audit>` of all imports against `pyproject.toml`, refactor class/variable names for clarity, add 100% PEP 257 docstrings and type annotations, and harden 5 specific edge cases (empty 0-card decks, division by zero when 0 questions are answered, whitespace trimming on inputs, bounded repeats in adaptive mode, and invalid deck creation paths).
- **AI Response:** Jules added `"rich>=13.0.0"` to `pyproject.toml`, standardized strategy class names (`SequentialQuizMode`, `RandomQuizMode`, `AdaptiveQuizMode`), added `max_repeats=3` to `AdaptiveQuizMode`, guarded 0-question stats division, trimmed answer whitespace, and expanded the test suite to 54 tests.
- **Your Changes:** Reviewed the diff and verified that `uv sync` properly categorized runtime vs. dev dependencies. I also noted in my review log that Jules used legacy `typing.Optional` / `typing.List` instead of Python 3.10+ `|` union syntax.
- **Outcome:** Production-hardened application with zero linting or type errors and 93% statement coverage.

### Challenges with AI Collaboration

- **Struggles with Repository Layout Migrations:** Across prompts in interaction 1-3 and 6, Jules repeatedly struggled with moving from a flat starter layout to a `src/flashcard_quizzer/` package structure—initially leaving files in the root, creating an empty `src/flashcard-quizzer/` directory with a hyphen (invalid in Python imports), omitting `[build-system]` in `pyproject.toml`, and creating duplicate shim files in root `utils/`.
- **Transitive Dependency Blind Spots:** Because Jules tests inside a dev environment where `uv sync --dev` is active, she did not notice when a runtime import (`rich`) was not defined in the `pyproject.toml` file, nor when a misspelled prompt requirement (`zenzical` in interaction 1) wasn't installed in `pyproject.toml`.
- **Empty File Commits and Duplicate Workflows (PR #9 / #10):** In interaction 8, Jules's initial commit claimed in its commit message to add four documentation files (`docs/index.md`, `getting-started.md`, `architecture.md`, `cli-reference.md`), but the committed files were all 0 bytes! Only after I inspected the PR diff and asked *"Where did the changes go? The files you pushed are all empty"* did Jules push the actual Markdown content (`bc2e31b`). She also created a duplicate `.github/workflows/deploy-docs.yml` alongside the existing `.github/workflows/docs.yml`, which I resolved with Antigravity.
- **Pretraining Bias Toward Legacy Python Typing:** Even with `requires-python = ">=3.14,<3.15"` in `pyproject.toml`, the AI defaulted to `from typing import Optional, List, Dict` rather than modern `X | None` and `list[...]` syntax unless explicitly forbidden.

---

## Software Engineering Practices

### Code Quality Measures

- [x] **Code formatting (`black`, `isort`):** Configured with an 88-character line length targeting `py314` in `pyproject.toml` and enforced in CI.
- [x] **Linting (`flake8`, `mypy`):** `flake8` enforces PEP 8 compliance across `src/` and `tests/`, while `mypy` runs with `disallow_untyped_defs = true`, `warn_return_any = true`, and `python_version = "3.14"`.
- [x] **Security & Vulnerability Scanning (`bandit`, `safety`):** `bandit -r src` scans for common security issues in application code, and `safety` audits locked dependencies.
- [x] **Type hints:** 100% of function and method signatures across all modules include explicit type annotations.
- [x] **Documentation/comments:** Every module, class, and public function includes PEP 257 docstrings detailing arguments, return values, and exceptions, complemented by a Zensical documentation site (`docs/`).
- [x] **Error handling:** Defensive validation traps `FileNotFoundError`, `json.JSONDecodeError`, `ValueError`, `OSError`, `KeyboardInterrupt`, and `EOFError`, printing friendly messages to `stderr` and exiting with well-defined status codes (`0` for user cancellation, `1` for errors) without exposing raw tracebacks.

### Testing Strategy

- **Layered Test Suite:** I organized tests into unit and integration suites under `tests/`:

    - `tests/test_flashcard_loader.py` (10 tests): Tests plain arrays, wrapped `{"cards": [...]}` objects, missing files, malformed JSON, empty decks, and missing/whitespace fields.
    - `tests/test_quiz_modes.py` (8 tests): Verifies `QuizModeFactory` instantiation, case-insensitivity, invalid mode errors, exact sequential order, random shuffling, and adaptive re-queueing and `max_repeats` bounds.
    - `tests/test_deck_creator.py` (15 tests): Uses `monkeypatch` and `tmp_path` to simulate creating new decks, overwriting, appending, cancelling, handling empty backs, and confirming saves on `"exit"` or `Ctrl+C`.
    - `tests/test_integration.py` & `tests/test_main.py` (13 tests): End-to-end CLI simulations testing full quiz sessions, accuracy calculation, division-by-zero protection on immediate exit, and CLI argument routing.
    - `tests/test_task_manager.py` (8 tests): Retains unit tests for the starter utility module.

- **Test Coverage & Reliability:** The suite comprises **54 passing tests** achieving **93% overall statement coverage** (with **100%** on `file_handler.py` and `ui.py`, **96%** on `quiz_engine.py`, and **93%** on `main.py`). Every pull request was gated by `.github/workflows/ci.yml` running the full quality and test pipeline automatically.

### Design Patterns Used

- **Strategy Pattern (`src/flashcard_quizzer/quiz_engine.py`):**

    - *Implementation:* Defined an abstract base class `QuizMode(ABC)` with abstract methods `has_remaining_cards() -> bool`, `get_next_card() -> Flashcard`, and `record_answer(card: Flashcard, is_correct: bool) -> None`. Three concrete subclasses encapsulate distinct scheduling algorithms: `SequentialQuizMode`, `RandomQuizMode`, and `AdaptiveQuizMode`.
    - *Rationale:* Decouples the quiz orchestration loop in `main.py` from how cards are ordered or repeated. `main.py` simply iterates while `quiz_strategy.has_remaining_cards()` is true without knowing whether the deck is static, shuffled, or dynamically re-queueing missed cards in a `deque`. Allowing for a future spaced-repetition strategy.

- **Factory Pattern (`src/flashcard_quizzer/quiz_engine.py`):**

     - *Implementation:* `QuizModeFactory.create_mode(mode_name: str, cards: Sequence[Flashcard]) -> QuizMode` normalizes the CLI mode string (case-insensitively and whitespace-trimmed) and instantiates the matching `QuizMode` strategy, raising a descriptive `ValueError` if an unsupported mode is requested.
    - *Rationale:* Centralizes strategy creation and validation in one place, keeping `main.py` free of conditional `if/elif/else` instantiation branches.

### Code Structure and Organization

```text
flashcard-quizzer/
├── .github/workflows/
│   ├── ci.yml                     # Automated lint, type-check, security & pytest pipeline
│   └── docs.yml                   # Automated Zensical build & GitHub Pages deployment
├── data/                          # JSON flashcard decks (greek_mythology, earth, sample)
├── docs/                          # Zensical documentation site, AI edit log, prompts & report
├── src/flashcard_quizzer/
│   ├── __init__.py                # Package exports
│   ├── __main__.py                # Module execution entry point (python -m flashcard_quizzer)
│   ├── main.py                    # CLI argument parsing and session/creation orchestration
│   ├── quiz_engine.py             # Domain layer: Strategy (QuizMode) & Factory patterns
│   ├── ui.py                      # Presentation layer: Rich terminal rendering & input
│   └── utils/
│       ├── deck_creator.py        # Interactive deck creation (overwrite/append/cancel)
│       ├── file_handler.py        # Flashcard dataclass & dual-schema JSON loader
│       └── task_manager.py        # Legacy starter CRUD utility
├── tests/                         # 54 unit and integration tests (93% coverage)
├── pyproject.toml                 # Project metadata, hatchling build-system & tool configs
├── uv.lock                        # Deterministic dependency lockfile
└── zensical.toml                  # Zensical documentation site configuration
```

---

## Technical Challenges and Solutions

### Challenge 1

`pytest` Masking Broken Package Installation (`ModuleNotFoundError`)

- **Problem:** After Jules refactored the repository into `src/flashcard_quizzer/` in PR `#4`, all unit tests passed in `pytest`, yet running `uv run flashcard-quizzer` or `uv run python src/flashcard_quizzer/main.py` failed with `ModuleNotFoundError: No module named 'flashcard_quizzer'`.
- **Solution:** Configured `[build-system]` (`requires = ["hatchling"]`, `build-backend = "hatchling.build"`) in `pyproject.toml`, added `src/flashcard_quizzer/__main__.py`, and ran `uv sync` so `uv` installed the package in editable mode and generated the `flashcard-quizzer` script binary in `.venv/bin/`.
- **AI Involvement:** I used **Antigravity** on the checked-out PR branch to inspect `uv sync` warnings and identify that `pythonpath = ["src"]` in `[tool.pytest.ini_options]` had allowed `pytest` to import `flashcard_quizzer` even though `uv` treated the project as an unpackaged virtual environment.
- **Lessons Learned:** Passing unit tests do not guarantee valid Python packaging. Always test the installed CLI entry point directly (`uv run <script>`).

### Challenge 2

Hidden Transitive Runtime Dependency (`rich`)

- **Problem:** In PR `#6`, Jules imported `rich` in `src/flashcard_quizzer/ui.py` to render colored terminal output. Both local tests and GitHub Actions CI passed, but when reviewing `pyproject.toml`, I discovered `dependencies = []` was still empty.
- **Solution:** Because `safety` (a dev dependency) depended on `rich` transitively, `rich` was present in `uv.lock` whenever `--dev` or `--all-groups` was installed. In interaction 7, I instructed Jules to audit all imports across `src/` and explicitly add `"rich>=13.0.0"` to `[project] dependencies` in `pyproject.toml`.
- **AI Involvement:** Human code review caught the bug; Jules executed the dependency audit and lockfile update in PR `#8`.
- **Lessons Learned:** Dev dependencies can mask missing runtime dependencies in lockfiles. Always review `pyproject.toml` alongside code diffs when third-party imports are added.

### Challenge 3

Empty Committed Files and Duplicate GitHub Actions Workflows in Documentation PR

- **Problem:** In PR `#9` (interaction 8), Jules's first commit pushed 0-byte empty files for `docs/index.md`, `docs/getting-started.md`, `docs/architecture.md`, and `docs/cli-reference.md`. Additionally, after Jules fixed the empty files, the branch contained two competing GitHub Pages workflows: `.github/workflows/docs.yml` (generated by `zensical new` using `pip`) and `.github/workflows/deploy-docs.yml` (created by Jules using `uv`).
- **Solution:** I caught the empty files during PR diff review and prompted Jules to push the missing content (`bc2e31b`). Then, using Antigravity, I merged the `concurrency: group: "pages"` config, `astral-sh/setup-uv@v5` caching, `.python-version`, and `uv sync --dev` / `uv run zensical build --clean` steps from `deploy-docs.yml` into `docs.yml`, deleted `deploy-docs.yml`, and updated the CLI examples to use `data/greek_mythology.json`.
- **AI Involvement:** Jules generated the documentation content after my PR review prompt; Antigravity consolidated the two GitHub Actions workflows cleanly.
- **Lessons Learned:** Never trust an AI agent's commit message or PR summary without inspecting the file diffs, and always reconcile AI-generated CI workflows with existing project workflows.

* * *

## Code Quality Analysis

### Metrics

- **Lines of code:** 965 lines of Python in `src/flashcard_quizzer/` (387 executable statements) + 837 lines of Python in `tests/` (1,802 total lines of Python)
- **Test coverage:** **93%** overall statement coverage across 54 unit and integration tests (`file_handler.py`: 100%, `ui.py`: 100%, `quiz_engine.py`: 96%, `main.py`: 93%, `deck_creator.py`: 87%)
- **Number of functions/classes:** 8 classes and 46 functions/methods in `src/flashcard_quizzer/`
- **Linting score:** **0 errors / 100% pass rate** across `flake8`, `black --check`, `isort --check`, `mypy` (strict mode), and `bandit -r src`

### Self-Assessment

- **Code Readability:** **5/5** — All modules follow PEP 8 strictly, functions are concise and focused on single responsibilities, identifiers are descriptive (`SequentialQuizMode`, `has_remaining_cards`, `missed_cards`), and every class and function has a clear PEP 257 docstring.
- **Code Maintainability:** **5/5** — The Strategy and Factory patterns cleanly isolate card-scheduling logic from terminal UI and file I/O, and the project is packaged with deterministic dependencies (`uv.lock`) and automated CI (`ci.yml`).
- **Test Quality:** **5/5** — The 54-test suite tests both happy paths and critical edge cases (malformed JSON, empty decks, division by zero on 0 answered cards, adaptive mode repeat bounds, `Ctrl+C` / `EOFError` exits, and file overwrite/append flows) without relying on fragile sleep timers or external network calls.
- **Documentation:** **5/5** — Includes a comprehensive `README.md`, a deployed Zensical documentation site (`index.md`, `getting-started.md`, `architecture.md`, `cli-reference.md`), full prompt records (`prompts.md`), and a transparent `ai_edit_log.md`.

---

## Learning Outcomes

### Technical Skills Developed

- **Modern Python Packaging with `uv` and Python 3.14:** Gained hands-on experience configuring `pyproject.toml` with PEP 517 build backends (`hatchling`), `[project.scripts]` entry points, `[dependency-groups]`, and deterministic `uv.lock` workflows in CI.
- **Static Analysis & Security Toolchains:** Integrated `black`, `isort`, `flake8`, `mypy`, `bandit`, and `safety` into a unified local and GitHub Actions workflow.
- **Documentation Engineering with Zensical:** Learned how to initialize, configure (`zensical.toml`), and deploy a static documentation site using Zensical and GitHub Pages (`actions/deploy-pages`).

### AI Collaboration Skills

- **Structured XML Prompt Engineering:** Learned how organizing prompts with explicit `<role>`, `<context>`, `<requirements>`, `<testing_requirements>`, and `<constraints>` tags dramatically reduces ambiguity and improves first-pass code quality.
- **Multi-Agent Workflow Orchestration:** Discovered the complementary strengths of different AI paradigms—using an asynchronous PR agent (**Jules**) for well-scoped feature implementation and test generation, while using a local interactive agent (**Antigravity**) for rapid environment debugging and file consolidation.
- **Pragmatic Task Selection (When Not to Prompt):** Forcing myself to use prompts for nearly every change taught me a valuable lesson about developer ergonomics: AI agents excel at generating 200-line modules and test suites, but using a full PR agent cycle for a 1-line fix (like adding a missing dependency to `pyproject.toml`) has high overhead compared to making the edit directly with `uv add`.

### Software Engineering Insights

- **Automated Linters Eliminate Hallucinations, Not Architectural Flaws:** Because Jules ran `pytest`, `mypy`, `flake8`, and `black` before opening each PR, I experienced zero syntax errors or hallucinated standard-library methods. However, automated tools did not prevent architectural mistakes like missing `[build-system]` metadata, unpinned transitive dependencies, or duplicate CI workflows—proving that human architectural oversight remains indispensable.
- **Value of Design Patterns for Testability:** Isolating `QuizMode` strategies from `ui.py` made it trivial to test complex adaptive re-queueing behavior deterministically in milliseconds without mocking terminal I/O.

---

## Reflection

### What Worked Well

- **Strict Quality Gates in `pyproject.toml` and CI:** Having `pytest`, `mypy`, `flake8`, `black`, `isort`, and `bandit` configured from Interaction 1 meant every subsequent AI PR had to pass a high technical bar before review.
- **Incremental, PR-Based Development:** Breaking the application into 8 focused PRs made code reviews manageable and allowed me to checkout and test each vertical slice locally before building the next layer.
- **Separation of Domain and Presentation Layers:** The boundary between `quiz_engine.py`, `ui.py`, and `utils/file_handler.py` kept the codebase clean and easy to reason about.

### What Could Be Improved

- **Establish `src/` Packaging Before Feature Prompts:** In hindsight, I should have configured the `src/flashcard_quizzer/` directory layout and `[build-system]` (`hatchling`) in Interaction 1 rather than migrating files across the prompts in interaction 2 and 3.
- **Explicit Modern Python Typing Constraints:** Adding a rule in `AGENTS.md` and prompt `<constraints>` requiring PEP 604 union syntax (`X | None`) and PEP 585 built-in generics (`list`, `dict`) would have prevented the AI from defaulting to legacy `typing.Optional` and `typing.List` imports.
- **Hybrid Human + AI Editing Workflow:** Rather than restricting myself to prompt-only edits for minor fixes, combining direct manual edits for trivial configuration tweaks with AI prompts for larger feature and test generation is much faster and less frustrating.

### Future Enhancements

- **Persistent Spaced-Repetition Metadata:** Extend the JSON schema and `AdaptiveQuizMode` to persist per-card mastery scores, ease factors, and next-review timestamps across sessions.
- **Fuzzy / Levenshtein Answer Matching:** Allow configurable tolerance for minor spelling typos using Python's standard library [difflib.SequenceMatcher](https://docs.python.org/3/library/difflib.html).
- **Session History & Export:** Log completed study sessions to a local SQLite database or CSV/Markdown progress report to track accuracy trends over time.

---

## Conclusion

Building **Flashcard Quizzer** demonstrated both the power and the boundaries of modern AI-assisted software development. By combining structured prompt engineering, rigorous automated tooling (`uv`, `pytest`, `mypy`, `flake8`, `black`, `isort`, `bandit`), and disciplined local code reviews of every pull request, I was able to transform a basic starter template into a well-architected, 93%-covered Python 3.14 CLI application with comprehensive documentation.

More importantly, this project reshaped how I view AI coding assistants: when paired with strong automated linters and type checkers, modern AI agents rarely hallucinate syntax or APIs, yet they still require an experienced engineer to guide package architecture, audit dependencies, verify real-world execution, and decide when a direct manual edit is wiser than a prompt. Moving forward, I will continue using strict static analysis gates, design patterns that isolate domain logic, and a pragmatic combination of autonomous PR agents and local interactive AI pair-programming.

---

## Appendices

### Appendix A: AI Interaction Log
The complete chronological record of all 8 AI interactions, including exact prompts, Jules commit messages, code review findings, and local fixes with Antigravity, is available in:

- [`docs/ai_edit_log.md`](ai_edit_log.md) — Detailed AI Edit Log
- [`docs/prompts.md`](prompts.md) — Full text of prompts interaction 1 through 8

Key highlights from `docs/ai_edit_log.md`:

1. **Interaction 1 (`d000c31`, PR #2):** Python 3.14 & `uv` environment setup and linter configuration.
2. **Interaction 2 (`29b11f3`, PR #3):** `Flashcard` dataclass & dual-schema JSON loader (`file_handler.py`).
3. **Interaction 3 (`c2a8e63`, PR #4):** `src/flashcard_quizzer/` migration, CI workflow, and Antigravity fix for `hatchling` `[build-system]`.
4. **Interaction 4 (`26d4f53`, PR #5):** Strategy (`QuizMode`) and Factory (`QuizModeFactory`) implementation in `quiz_engine.py`.
5. **Interaction 5 (`7feba0a`, PR #6):** Rich terminal UI (`ui.py`), CLI loop (`main.py`), and discovery of the undeclared `rich` dependency.
6. **Interaction 6 (`38220b1`, PR #7):** Interactive deck creator (`deck_creator.py`) with overwrite/append/cancel support.
7. **Interaction 7 (`1bca64d`, PR #8):** Dependency audit, identifier refactoring, PEP 257 docstrings, and edge-case hardening.
8. **Interaction 8 (`752916f`, PR #9 & #10):** Zensical documentation site, resolution of empty committed files, and GitHub Actions workflow consolidation.

### Appendix B: Code Statistics

| Module | Statements | Missed | Coverage | Role |
| :--- | ---: | ---: | ---: | :--- |
| `src/flashcard_quizzer/__init__.py` | 2 | 0 | **100%** | Package exports |
| `src/flashcard_quizzer/__main__.py` | 3 | 3 | **0%** | `python -m` entry point |
| `src/flashcard_quizzer/main.py` | 84 | 6 | **93%** | CLI parser & session orchestration |
| `src/flashcard_quizzer/quiz_engine.py` | 80 | 3 | **96%** | Strategy & Factory quiz engine |
| `src/flashcard_quizzer/ui.py` | 33 | 0 | **100%** | Rich terminal presentation |
| `src/flashcard_quizzer/utils/__init__.py` | 0 | 0 | **100%** | Utils subpackage |
| `src/flashcard_quizzer/utils/deck_creator.py` | 115 | 15 | **87%** | Interactive deck builder |
| `src/flashcard_quizzer/utils/file_handler.py` | 44 | 0 | **100%** | JSON loader & `Flashcard` model |
| `src/flashcard_quizzer/utils/task_manager.py` | 26 | 0 | **100%** | Starter CRUD utility |
| **Total (`54 passed in 0.31s`)** | **387** | **27** | **93%** | **Full Application** |

### Appendix C: Additional Resources
- [uv Documentation (Astral)](https://docs.astral.sh/uv/) — Python package and project management
- [Zensical Documentation](https://zensical.org/) — Static documentation site generator
- [Rich Documentation](https://rich.readthedocs.io/) — Terminal formatting and color output
- [ArjanCodes](https://www.arjancodes.com/) YouTube videos
