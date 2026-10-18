---
icon: lucide/rocket
---
# Flashcard Quizzer CLI

Welcome to the documentation for **Flashcard Quizzer CLI**, a command-line tool built to help you practice and memorize new concepts effectively.

This project was developed as part of the Udacity AI-Powered Software Engineer Nanodegree to demonstrate applied software engineering principles, robust design patterns, and effective CLI development in Python.

## Project Objectives

- **Effective Learning:** Provide an interactive, distraction-free environment for rote memorization and spaced repetition.
- **Robust Software Design:** Utilize foundational design patterns such as the **Strategy Pattern** for handling different quiz flows and the **Factory Pattern** for their instantiation.
- **Modularity:** Separate the UI layer, game logic, and file management to ensure maintainability and testability.
- **Developer Experience:** Leverage modern Python tooling (`uv`, `mypy`, `pytest`, `rich`) to ensure the codebase remains clean, fast, and strict.

## Feature Matrix

| Feature | Description |
| :--- | :--- |
| **Quiz Modes** | Choose between `sequential`, `random`, or `adaptive` learning modes. |
| **Adaptive Learning** | The adaptive mode repeats cards you miss until you get them right, reinforcing difficult concepts. |
| **Dual JSON Formats** | Supports simple `[{"front": "a", "back": "b"}]` arrays or wrapped objects `{"cards": [...]}` formats. |
| **Interactive Deck Creation** | Effortlessly create new decks from the terminal with append and overwrite options. |
| **Rich Terminal UI** | Enjoy a beautiful interface, colorized feedback, and comprehensive post-game statistics. |
