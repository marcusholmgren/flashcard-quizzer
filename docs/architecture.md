# Architecture

The Flashcard Quizzer CLI is built with a focus on maintainability, modularity, and adherence to Object-Oriented Programming (OOP) design patterns.

## Separation of Concerns

The application logic is clearly divided into distinct layers:

1.  **UI Layer (`ui.py`):** Handles all user interactions, printing to the terminal, capturing input, and formatting output using the `rich` library. It does not contain business logic.
2.  **Engine Layer (`quiz_engine.py`):** Contains the core business logic, managing the state of the quiz, statistics, and executing the selected quiz mode.
3.  **Data Layer (`utils/file_handler.py`):** Responsible for reading and writing flashcard data to and from JSON files, handling the two supported formats robustly.
4.  **CLI Entry Point (`main.py`):** Parses command-line arguments using `argparse`, orchestrates the initialization of the other layers, and handles interactive deck creation.

## Design Patterns

### The Strategy Pattern

The quiz execution logic utilizes the **Strategy Pattern** to allow interchangeable algorithms for how cards are presented to the user.

-   **`QuizMode` (Abstract Base Class):** Defines the contract that all specific quiz modes must follow. It requires the implementation of a `get_next_card` method.
-   **`SequentialMode`:** Implements `QuizMode` by returning cards in the exact order they appear in the JSON file.
-   **`RandomMode`:** Implements `QuizMode` by shuffling the deck and presenting cards in a random order.
-   **`AdaptiveMode`:** Implements `QuizMode` by maintaining a queue. If a user answers incorrectly, the card is pushed back into the queue to be reviewed again later.

This pattern allows adding new quiz modes in the future without modifying existing engine logic.

### The Factory Pattern

To cleanly instantiate the correct `QuizMode` strategy based on user input, the application uses the **Factory Pattern**.

-   **`QuizModeFactory`:** A static factory class containing a `create_mode` method. It takes a string identifier (e.g., `"sequential"`, `"adaptive"`) and the deck of cards, returning the corresponding concrete `QuizMode` object.

This encapsulates the creation logic, keeping `main.py` and `quiz_engine.py` clean and agnostic to the specific classes being instantiated.
