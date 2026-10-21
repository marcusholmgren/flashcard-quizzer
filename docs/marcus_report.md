---
icon: lucide/pilcrow
---
# AI-Assisted Development Project Report

**Student Name:** Marcus Holmgren  
**Project Title:** Flashcard Quizzer  
**Date:** 2026-10-21  

## Executive Summary

**Flashcard Quizzer** is a Python 3.14 CLI tool for studying and authoring flashcards. Managed with `uv`, it loads dual JSON schemas, runs quizzes across three modes (`sequential`, `random`, and `adaptive`), displays colored feedback and statistics, and includes a deck creator.

The project enforces separation of concerns using the standard library. Core logic in `quiz_engine.py` uses the **Strategy Pattern** (`QuizMode`) and **Factory Pattern** (`QuizModeFactory`), decoupling UI (`ui.py`), CLI (`main.py`), and JSON I/O (`file_handler.py`, `deck_creator.py`). Only `rich` is used at runtime.

I used three AI tools: **Gemini** for XML prompt design, **Google Jules** as an autonomous GitHub PR agent, and **Google Antigravity** for local debugging. Every PR was checked out locally, verified against quality gates (`pytest`, `black`, `isort`, `flake8`, `mypy`, `bandit`, `safety`), and smoke-tested. Full logs are in [`docs/ai_edit_log.md`](ai_edit_log.md).

## Project Overview

### Problem Statement

Learners need a distraction-free CLI tool for active recall. Basic scripts hardcode card order, crash on invalid JSON, or lack safe deck authoring tools. Flashcard Quizzer solves this with JSON validation, adaptive re-queueing, and an atomic deck builder.

### Solution Approach

- **Minimal Dependencies:** Used the Python 3.14 standard library (`abc`, `argparse`, `collections.deque`, `dataclasses`, `json`, `pathlib`, `random`, `tempfile`, `typing`), adding only `rich` for styling.
- **Layered Architecture:** Organized `src/flashcard_quizzer/` into Data (`file_handler.py`, `deck_creator.py`), Domain (`quiz_engine.py`), UI (`ui.py`), and CLI (`main.py`). See [`docs/architecture.md`](architecture.md).
- **Tooling & CI/CD:** Managed via `uv` (`pyproject.toml`, `uv.lock`) with GitHub Actions for CI (`ci.yml`) and **Zensical** docs (`docs.yml`).

### Final Features

- [x] **Dual-Schema JSON Loader (`file_handler.py`):** Validates list and wrapped `cards` JSON formats, exiting with code `1` on errors.
- [x] **Three Quiz Modes (`quiz_engine.py`):** `SequentialQuizMode`, `RandomQuizMode`, and `AdaptiveQuizMode` (re-queues missed cards up to five retries).
- [x] **Interactive Quiz Loop & Stats (`main.py`, `ui.py`):** Case-insensitive matching, `rich` feedback, graceful exits, and accuracy reports.
- [x] **Interactive Deck Creator (`deck_creator.py`):** Creates or updates decks via Overwrite, Append, or Cancel prompts with atomic saves.

## AI Collaboration Experience

### AI Tools Used

- [ ] Claude  
- [ ] GitHub Copilot  
- [ ] ChatGPT  
- [x] Other: **Gemini** (prompt design), **Google Jules** (PR agent), and **Google Antigravity** (local IDE pair-programmer)

### Collaboration Workflow

1. **Structuring Prompts:** Organized 8 milestones in [`docs/prompts.md`](prompts.md) using XML tags (`role`, `task`, `context`, `requirements`, `testing_requirements`, `constraints`).
2. **Task Delegation:** Delegated feature modules, tests, and docs via prompts while manually creating the repo and custom JSON decks.
3. **Review and Validation:** Checked out each Jules PR, inspected `git diff`, ran `uv run pytest` and linters, and smoke-tested the CLI.
4. **Refining AI Suggestions:** Fixed packaging bugs, missing dependencies, and duplicate workflows via follow-up prompts or **Antigravity** (see [`docs/ai_edit_log.md`](ai_edit_log.md)).

### Most Valuable AI Interactions

#### Example 1: Quiz Engine with Strategy and Factory Patterns (PR #5)
**Context:** Needed quizzing logic in `quiz_engine.py` for sequential, random, and adaptive modes without UI coupling.  
**AI Prompt:** Asked Jules (Interaction 4 in [`docs/prompts.md`](prompts.md)) to build an abstract `QuizMode` class, three strategies, `QuizModeFactory.create_mode()`, and unit tests.  
**AI Response:** Jules built `quiz_engine.py` using `abc.ABC` and `collections.deque` plus tests in `tests/test_quiz_modes.py` (96% coverage).  
**Your Changes:** Exported classes in `__init__.py` and added the CI badge to `README.md`.  
**Outcome:** Decoupled domain engine following SOLID principles.

#### Example 2: Diagnosing Packaging Failures with Antigravity (PR #4)
**Context:** In Interaction 3, Jules moved code to `src/flashcard_quizzer/` and added `project.scripts` in `pyproject.toml`. CI `pytest` passed, but `uv run flashcard-quizzer` raised `ModuleNotFoundError`.  
**AI Prompt:** Asked Antigravity why `uv run flashcard-quizzer` failed despite passing tests.  
**AI Response:** Antigravity showed `pythonpath` let `pytest` pass while a missing `build-system` table caused `uv sync` to skip editable installation.  
**Your Changes:** Added `build-system` (`hatchling`), created `__main__.py`, removed stale folders, and added `data/sample_flashcards.json` and `tests/test_main.py`.  
**Outcome:** All CLI entry points ran cleanly.

#### Example 3: Dependency Audit and Edge-Case Hardening (PR #8)
**Context:** Reviewing PR `#6` showed `rich` was imported in `ui.py` but missing from `pyproject.toml` `dependencies` (masked in CI because `safety` installed `rich` transitively).  
**AI Prompt:** Asked Jules (Interaction 7) to audit imports against `pyproject.toml`, standardize strategy names, complete docstrings, and harden edge cases (empty decks, zero-division, whitespace, and retry limits).  
**AI Response:** Jules added `rich` to `pyproject.toml`, standardized names, guarded zero-division, and expanded tests.  
**Your Changes:** Verified installation via `uv sync` and logged typing critiques in [`docs/ai_edit_log.md`](ai_edit_log.md).  
**Outcome:** Hardened CLI with explicit dependencies and 93% coverage.

### Challenges with AI Collaboration

- **Package Migrations:** Jules struggled migrating to `src/flashcard_quizzer/`, leaving root shims and omitting `build-system` (Interactions 1–3, 6 in [`docs/ai_edit_log.md`](ai_edit_log.md)).
- **Transitive Dependencies:** Dev tools hid the missing `rich` dependency in `pyproject.toml`.
- **Empty Commits & Duplicate Workflows:** In PR `#9` (Interaction 8), Jules pushed 0-byte doc files and a duplicate `deploy-docs.yml`, resolved via diff review and Antigravity.

## Software Engineering Practices

### Code Quality Measures

- [x] Code formatting (`black`, `isort`)
- [x] Linting (`flake8`, strict `mypy`, `bandit`, `safety`)
- [x] Type hints (100% of signatures)
- [x] Documentation/comments (PEP 257 docstrings + Zensical site)
- [x] Error handling (Graceful exits for file, JSON, and input errors)

### Testing Strategy

A `pytest` suite across 6 files uses `monkeypatch`, `capsys`, and `tmp_path` to test original and AI-generated code. All **54 tests pass** with **93% coverage** on `src/flashcard_quizzer/`, verifying happy paths, invalid JSON, empty decks, 0-question accuracy math, adaptive retry caps, and overwrite, append, and cancel flows.

### Design Patterns Used

- **Strategy Pattern (`quiz_engine.py`):** `QuizMode` defines `has_remaining_cards()`, `get_next_card()`, and `record_answer()`, implemented by `SequentialQuizMode`, `RandomQuizMode`, and `AdaptiveQuizMode` to decouple `main.py` from card scheduling.
- **Factory Pattern (`quiz_engine.py`):** `QuizModeFactory.create_mode()` centralizes strategy creation and validation without branching in `main.py`.

### Code Structure and Organization

`src/flashcard_quizzer/` separates CLI orchestration (`main.py`), UI (`ui.py`), domain strategies (`quiz_engine.py`), and file I/O (`file_handler.py`, `deck_creator.py`), with tests in `tests/` and docs in `docs/`.

## Technical Challenges and Solutions

### Challenge 1: `pytest` Masking Uninstalled Package
**Problem:** In PR `#4`, `pytest` passed, but `uv run flashcard-quizzer` raised `ModuleNotFoundError`.  
**Solution:** Added `build-system` (`hatchling`) to `pyproject.toml` and `__main__.py` so `uv sync` installed the CLI script.  
**AI Involvement:** Antigravity diagnosed how `pythonpath` masked the missing build backend.  
**Lessons Learned:** Always smoke-test CLI entry points beyond `pytest`.

### Challenge 2: Empty Commits and Duplicate CI Workflows
**Problem:** In PR `#9`, Jules pushed 0-byte Markdown files and a duplicate `deploy-docs.yml`.  
**Solution:** Asked Jules to push the content, then used Antigravity to merge `uv` caching into `docs.yml` and remove `deploy-docs.yml`.  
**AI Involvement:** Jules wrote the docs; Antigravity merged the workflows.  
**Lessons Learned:** Inspect `git diff` rather than trusting commit messages.

## Code Quality Analysis

### Metrics

- **Lines of code:** 965 in `src/` (387 statements) + 837 in `tests/`
- **Test coverage:** **93%** (54 tests)
- **Number of functions/classes:** 8 classes, 46 functions/methods
- **Linting score:** **0 errors** (`flake8`, `black`, `isort`, `mypy`, `bandit`)

### Self-Assessment

- **Code Readability:** **5/5** — PEP 8 compliant with clear names and docstrings.
- **Code Maintainability:** **5/5** — Clean Strategy/Factory separation and CI checks.
- **Test Quality:** **5/5** — 54 deterministic tests covering edge cases and interrupts.
- **Documentation:** **5/5** — Complete `README.md`, Zensical docs, D2 diagram, and AI log.

## Learning Outcomes

### Technical Skills Developed

- Configured Python 3.14 packaging with `uv`, `hatchling`, and `project.scripts`.
- Integrated `black`, `isort`, `flake8`, `mypy`, `bandit`, and `pytest-cov` in CI.
- Built static docs with **Zensical** and D2 SVG diagrams.

### AI Collaboration Skills

- Used XML prompts to specify architecture, edge cases, and tests.
- Paired PR agents (Jules) with local agents (Antigravity) for debugging.
- Balanced prompt overhead against direct manual edits.

### Software Engineering Insights

- Automated linters catch syntax errors, but human review is vital for packaging and dependencies.
- Decoupling `QuizMode` from `QuizUI` makes stateful logic easy to test.

## Reflection

### What Worked Well

- Enforcing quality gates from Interaction 1 kept every PR consistent.
- Reviewing features as isolated GitHub PRs caught defects early.

### What Could Be Improved

- Configure `src/flashcard_quizzer/` and `build-system` in Interaction 1.
- Require PEP 604 union types in `AGENTS.md`.

### Future Enhancements

- Persist spaced-repetition mastery scores in JSON decks.
- Add fuzzy answer matching via `difflib`.
- Export session history to SQLite or CSV.

## Conclusion

Building **Flashcard Quizzer** showed that combining structured prompts, automated quality gates, and human review turns AI assistants into reliable force multipliers. Linters and unit tests caught syntax errors, while manual smoke testing and diff reviews resolved packaging, dependency, and workflow issues.

## Appendices

### Appendix A: AI Interaction Log
Full logs and prompts: [`docs/ai_edit_log.md`](ai_edit_log.md) and [`docs/prompts.md`](prompts.md).

### Appendix B: Code Statistics
**Coverage (54 passed):** **93% total** (`file_handler.py`, `ui.py`, `task_manager.py`: 100%; `quiz_engine.py`: 96%; `main.py`: 93%; `deck_creator.py`: 87%).

### Appendix C: Additional Resources
`uv`, `Zensical`, `Rich`, and ArjanCodes Python design pattern guides.
