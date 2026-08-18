"""
Pytest configuration and shared fixtures for the Sudoku application.
"""
import pytest
import sys
from pathlib import Path

# Add the starter directory to the path so we can import app and sudoku_logic
sys.path.insert(0, str(Path(__file__).parent.parent))

import app
import sudoku_logic


@pytest.fixture
def flask_app():
    """Create a Flask app configured for testing."""
    app.app.config['TESTING'] = True
    return app.app


@pytest.fixture
def client(flask_app):
    """Create a test client for the Flask app."""
    return flask_app.test_client()


@pytest.fixture
def sample_empty_puzzle():
    """A sample empty 9x9 puzzle for testing."""
    return sudoku_logic.create_empty_board()


@pytest.fixture
def sample_filled_puzzle():
    """A sample fully filled valid sudoku puzzle."""
    puzzle = sudoku_logic.create_empty_board()
    sudoku_logic.fill_board(puzzle)
    return puzzle


@pytest.fixture
def sample_puzzle_with_solution():
    """A sample puzzle and its corresponding solution."""
    puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
    return puzzle, solution
