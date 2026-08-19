# Flask Sudoku

A responsive Sudoku game built with Flask and vanilla JavaScript. Puzzles are generated server-side, while gameplay state, timing, hints, theme, and the local Top 10 scoreboard are managed in the browser.

## Features

- Easy, Medium, and Hard difficulty levels with 45, 35, and 30 clues.
- Randomized puzzles with exactly one solution.
- Immediate rule and solution feedback, full-board checking, one-cell hints, locked prefilled/hinted cells, and a completion timer.
- Persistent Top 10 scores using browser `localStorage`, sorted by completion time.
- Light/dark themes, accessible labels, alternating 3x3 box colors, and a square mobile-friendly board.

## Setup and Running

From the repository root:

```bash
cd starter
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in a browser.

## Tests

```bash
pytest
```

## Difficulty and Unique-Solution Algorithm

Easy gives 45 clues, Medium gives 35, and Hard gives 30. The server first creates a complete valid board, then tries removing candidate cells. A removal is kept only when `count_solutions(board, limit=2)` finds exactly one completion. The backtracking counter stops as soon as a second solution is found. Generation and removal have bounded retry limits and return a controlled error when an exact puzzle cannot be produced.

## Scoreboard

Only completed games can be saved. The browser stores the player name, completion time, difficulty, and hints used in `localStorage`, sorts fastest first, keeps ten entries, and renders the list after refresh.

## Project Structure

```text
starter/
  app.py                 Flask routes and request validation
  sudoku_logic.py        Board generation and unique-solution solver
  templates/index.html   Game markup
  static/main.js         Gameplay, timer, hints, theme, and scores
  static/styles.css      Responsive and light/dark styling
  tests/                 Flask and Sudoku logic tests
```
