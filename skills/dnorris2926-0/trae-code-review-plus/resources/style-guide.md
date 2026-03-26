# Code Review Style Guide & Engineering Standards

This guide defines the core coding standards and best practices to follow during code reviews.

## 1. Python Coding Standards (PEP 8)
- **Naming Conventions**: 
  - Use `snake_case` for functions and variables.
  - Use `PascalCase` for classes.
  - Use `UPPER_SNAKE_CASE` for constants.
- **Indentation**: Use 4 spaces per indentation level. Never mix Tabs and Spaces.
- **Line Length**: Limit all lines to a maximum of 79-88 characters for better readability.
- **Imports**: Order should be: Standard Library -> Third-party Libraries -> Local Project Modules. Separate groups with a blank line.

## 2. Documentation & Comments
- **Docstrings**: Every public function, class, and module must have a docstring (Google or NumPy style).
- **Comment Purpose**: Comments should explain the "Why" behind the logic, not the "What". Code should be self-documenting through clear naming.
- **TODOs**: Use the format `TODO(username): description` to mark pending tasks.

## 3. Function Design Principles
- **Single Responsibility (SRP)**: Each function should do one thing and do it well.
- **Length Limit**: Functions should generally not exceed 50 lines. If they do, consider refactoring.
- **Parameter Control**: Minimize the number of parameters. If a function requires more than 4 arguments, use a Dataclass or a Dictionary.

## 4. Error Handling & Logging
- **Explicit Catching**: Avoid bare `except:`. Always specify the exception type (e.g., `except ValueError:`).
- **Logging**: Use the `logging` module with appropriate levels (`INFO`, `WARNING`, `ERROR`, `CRITICAL`) instead of `print` statements. Always log stack traces for exceptions.

## 5. Security Best Practices (CRITICAL)
- **Input Validation**: Treat all user input as untrusted. Validate and sanitize before processing.
- **Secret Management**: Never hardcode API keys, passwords, or tokens. Use environment variables or a Secret Manager.
- **Resource Cleanup**: Ensure resources like file handles and database connections are properly closed using `with` statements or `finally` blocks.

## 6. Performance & Optimization
- **Algorithm Complexity**: Be mindful of time and space complexity, especially in loops and recursive calls.
- **Lazy Loading**: Use generators or lazy loading for large datasets to minimize memory footprint.
- **Avoid Global State**: Minimize the use of global variables as they make code harder to test and debug.

## 7. Testing & Maintainability
- **Unit Tests**: Ensure new logic is covered by unit tests. Follow the "Arrange-Act-Assert" pattern.
- **DRY (Don't Repeat Yourself)**: Refactor duplicate code into reusable functions or classes.
- **KISS (Keep It Simple, Stupid)**: Avoid over-engineering. Choose the simplest solution that meets the requirements.
