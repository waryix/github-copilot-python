# Copilot Instructions — Flask Sudoku Project

## Project Goal

This project is a Flask-based Sudoku game being refactored from legacy Python code into a clean, maintainable application.

The application must support:

* Easy, Medium, and Hard difficulty levels
* Sudoku puzzles with exactly one unique solution
* Locked prefilled cells
* Immediate invalid-move feedback
* Check functionality
* Hint functionality
* Puzzle completion detection
* A game timer
* A persistent Top 10 scoreboard using browser localStorage
* Light and dark modes
* Responsive desktop and mobile layouts
* Alternating colors for the 3×3 Sudoku regions

## Code Quality

Write modern, readable Python and JavaScript.

Prefer:

* Small, focused functions
* Meaningful variable and function names
* Modular and reusable components
* Clear separation of responsibilities
* Consistent formatting
* Explicit error handling
* Minimal duplication
* Simple solutions over unnecessarily complex abstractions

Avoid:

* Global mutable state where it can be avoided
* Duplicated Sudoku logic
* Unnecessary dependencies
* Large functions that perform multiple unrelated tasks
* Changing unrelated files when implementing a feature
* Breaking existing functionality without explaining why

## Architecture

Keep Sudoku/game logic separate from Flask routes and presentation logic.

Flask routes should primarily:

1. Receive input
2. Validate input
3. Call appropriate game logic
4. Return a response

Sudoku generation, solving, validation, and uniqueness checking should be implemented in reusable functions or modules that can be tested independently.

Frontend behavior should remain separate from backend game logic wherever practical.

## Sudoku Rules

A valid Sudoku solution must:

* Contain numbers 1–9
* Have no duplicate values in any row
* Have no duplicate values in any column
* Have no duplicate values in any 3×3 region

Every generated puzzle must have exactly one valid solution.

Difficulty should be represented explicitly and should control the number of prefilled cells.

Prefilled and hint-filled cells must be locked from normal user editing.

## Testing

Tests should be written using a standard Python testing framework such as pytest.

Important logic should be testable independently of the Flask UI.

Tests should cover:

* Sudoku validity
* Sudoku solving
* Unique solution detection
* Difficulty behavior
* Puzzle generation
* Flask routes
* Important game behavior

Run the existing tests before modifying application behavior.

After every significant change, run the complete test suite.

## Frontend and Accessibility

The UI should:

* Work on desktop and mobile
* Support light and dark modes
* Maintain readable contrast
* Use clear button labels
* Provide meaningful focus states
* Avoid layout shifts
* Use semantic HTML where practical
* Provide accessible labels for interactive controls

The Sudoku grid should clearly distinguish the nine 3×3 regions using alternating visual styles.

## Copilot Behavior

When suggesting changes:

1. Explain the purpose of significant changes.
2. Prefer incremental modifications.
3. Do not rewrite unrelated code.
4. Preserve working behavior unless the change intentionally modifies it.
5. Identify assumptions.
6. Suggest tests for important new functionality.
7. If an existing implementation is incorrect, explain why before replacing it.
8. Do not introduce a library when a simple standard-library solution is sufficient.

When there are multiple reasonable approaches, briefly explain the trade-offs before implementing one.

## Development Workflow

Follow this workflow:

1. Understand the existing implementation.
2. Write or update tests.
3. Make one focused change.
4. Run the tests.
5. Manually verify the feature.
6. Review the generated code.
7. Accept, modify, or reject the suggestion.
8. Commit the working change.

Do not make large unrelated changes in a single step.

## Documentation

Keep the README updated with:

* Project description
* Features
* Setup instructions
* How to run the application
* How to run tests
* Project structure
* Any important implementation decisions

Document significant design decisions when useful.
