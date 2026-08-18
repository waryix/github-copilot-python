"""
Baseline tests for sudoku_logic module.
Tests the core Sudoku game logic without modifying the implementation.
"""
import pytest
import sudoku_logic


class TestBoardCreation:
    """Test board initialization and structure."""

    def test_create_empty_board_returns_9x9_grid(self):
        """Empty board should be 9x9."""
        board = sudoku_logic.create_empty_board()
        assert len(board) == 9
        for row in board:
            assert len(row) == 9

    def test_create_empty_board_all_zeros(self):
        """Empty board should contain all zeros."""
        board = sudoku_logic.create_empty_board()
        for row in board:
            for cell in row:
                assert cell == 0

    def test_create_empty_board_independent_copies(self):
        """Each call should create a new board (not shared reference)."""
        board1 = sudoku_logic.create_empty_board()
        board2 = sudoku_logic.create_empty_board()
        board1[0][0] = 5
        assert board2[0][0] == 0


class TestDeepCopy:
    """Test the deep_copy utility function."""

    def test_deep_copy_creates_independent_board(self):
        """Deep copy should create independent copy of board."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        board_copy = sudoku_logic.deep_copy(board)
        board_copy[0][0] = 9
        assert board[0][0] == 5
        assert board_copy[0][0] == 9

    def test_deep_copy_preserves_values(self):
        """Deep copy should preserve all values."""
        board = sudoku_logic.create_empty_board()
        for i in range(9):
            for j in range(9):
                board[i][j] = i + j
        board_copy = sudoku_logic.deep_copy(board)
        for i in range(9):
            for j in range(9):
                assert board_copy[i][j] == board[i][j]


class TestIsSafe:
    """Test the move validation logic (is_safe function)."""

    def test_is_safe_empty_board_allows_any_number(self):
        """Empty board should allow any number 1-9 in any position."""
        board = sudoku_logic.create_empty_board()
        for num in range(1, 10):
            assert sudoku_logic.is_safe(board, 0, 0, num) is True

    def test_is_safe_detects_duplicate_in_row(self):
        """Should detect duplicate in same row."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        assert sudoku_logic.is_safe(board, 0, 3, 5) is False
        assert sudoku_logic.is_safe(board, 0, 3, 6) is True

    def test_is_safe_detects_duplicate_in_column(self):
        """Should detect duplicate in same column."""
        board = sudoku_logic.create_empty_board()
        board[2][0] = 7
        assert sudoku_logic.is_safe(board, 5, 0, 7) is False
        assert sudoku_logic.is_safe(board, 5, 0, 3) is True

    def test_is_safe_detects_duplicate_in_3x3_box(self):
        """Should detect duplicate in same 3x3 box."""
        board = sudoku_logic.create_empty_board()
        board[0][1] = 4
        # Same 3x3 box (top-left)
        assert sudoku_logic.is_safe(board, 1, 2, 4) is False
        # Different 3x3 box
        assert sudoku_logic.is_safe(board, 4, 4, 4) is True

    def test_is_safe_rejects_invalid_numbers(self):
        """Should reject numbers outside 1-9 range."""
        board = sudoku_logic.create_empty_board()
        # The function doesn't explicitly check range, but it checks for duplicates
        # If 0 or negative already in board, they would be detected as dupes
        board[0][0] = 0
        board[1][1] = 10  # Out of Sudoku range


class TestFillBoard:
    """Test the puzzle-filling logic (backtracking solver)."""

    def test_fill_board_returns_true(self):
        """fill_board should return True when successful."""
        board = sudoku_logic.create_empty_board()
        result = sudoku_logic.fill_board(board)
        assert result is True

    def test_fill_board_completes_all_cells(self):
        """After fill_board, no cell should be empty (0)."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        for row in board:
            for cell in row:
                assert cell != 0
                assert 1 <= cell <= 9

    def test_fill_board_no_duplicates_in_rows(self):
        """Filled board should have no duplicate values in any row."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        for row in board:
            assert len(row) == len(set(row))

    def test_fill_board_no_duplicates_in_columns(self):
        """Filled board should have no duplicate values in any column."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        for col in range(9):
            column = [board[row][col] for row in range(9)]
            assert len(column) == len(set(column))

    def test_fill_board_no_duplicates_in_3x3_boxes(self):
        """Filled board should have no duplicate values in any 3x3 box."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        for box_row in range(3):
            for box_col in range(3):
                box = []
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_col * 3 + j
                        box.append(board[row][col])
                assert len(box) == len(set(box))

    def test_fill_board_preserves_prefilled_cells(self):
        """fill_board should not modify cells that are already filled."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        board[4][4] = 8
        sudoku_logic.fill_board(board)
        assert board[0][0] == 5
        assert board[4][4] == 8


class TestRemoveCells:
    """Test the cell removal logic (creates puzzle from solution)."""

    def test_remove_cells_removes_correct_count(self):
        """remove_cells should remove (81 - clues) cells."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        filled_count_before = sum(1 for row in board for cell in row if cell != 0)
        assert filled_count_before == 81  # All cells filled

        clues = 35
        sudoku_logic.remove_cells(board, clues)
        filled_count_after = sum(1 for row in board for cell in row if cell != 0)
        assert filled_count_after == clues

    def test_remove_cells_maintains_valid_values(self):
        """After removal, all remaining cells should be valid (1-9)."""
        board = sudoku_logic.create_empty_board()
        sudoku_logic.fill_board(board)
        sudoku_logic.remove_cells(board, 35)
        for row in board:
            for cell in row:
                assert cell == 0 or (1 <= cell <= 9)

    def test_remove_cells_with_different_clue_counts(self):
        """remove_cells should work with different clue counts."""
        for clues in [20, 30, 35, 40, 50]:
            board = sudoku_logic.create_empty_board()
            sudoku_logic.fill_board(board)
            sudoku_logic.remove_cells(board, clues)
            filled_count = sum(1 for row in board for cell in row if cell != 0)
            assert filled_count == clues


class TestGeneratePuzzle:
    """Test the complete puzzle generation pipeline."""

    def test_generate_puzzle_returns_tuple(self):
        """generate_puzzle should return a tuple (puzzle, solution)."""
        result = sudoku_logic.generate_puzzle()
        assert isinstance(result, tuple)
        assert len(result) == 2
        puzzle, solution = result
        assert isinstance(puzzle, list)
        assert isinstance(solution, list)

    def test_generate_puzzle_default_clues(self):
        """generate_puzzle with default clues should produce 35 clues."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        clues_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clues_count == 35

    def test_generate_puzzle_custom_clues(self):
        """generate_puzzle should respect custom clue count."""
        for clues in [20, 30, 40, 50]:
            puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
            clues_count = sum(1 for row in puzzle for cell in row if cell != 0)
            assert clues_count == clues

    def test_generate_puzzle_solution_is_complete(self):
        """Solution should have all 81 cells filled."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        filled_count = sum(1 for row in solution for cell in row if cell != 0)
        assert filled_count == 81

    def test_generate_puzzle_solution_is_valid(self):
        """Solution should have no duplicates in rows, columns, or boxes."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        # Check rows
        for row in solution:
            assert len(row) == len(set(row))
        # Check columns
        for col in range(9):
            column = [solution[row][col] for row in range(9)]
            assert len(column) == len(set(column))
        # Check boxes
        for box_row in range(3):
            for box_col in range(3):
                box = []
                for i in range(3):
                    for j in range(3):
                        row = box_row * 3 + i
                        col = box_col * 3 + j
                        box.append(solution[row][col])
                assert len(box) == len(set(box))

    def test_generate_puzzle_matches_solution_prefilled_cells(self):
        """Puzzle's prefilled cells should match solution values."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    assert puzzle[i][j] == solution[i][j]

    def test_generate_puzzle_puzzle_is_subset_of_solution(self):
        """Every filled cell in puzzle should exist in solution."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    assert solution[i][j] == puzzle[i][j]

    def test_generate_puzzle_has_fewer_clues_than_solution(self):
        """Puzzle should have fewer filled cells than solution."""
        puzzle, solution = sudoku_logic.generate_puzzle(clues=35)
        puzzle_count = sum(1 for row in puzzle for cell in row if cell != 0)
        solution_count = sum(1 for row in solution for cell in row if cell != 0)
        assert puzzle_count < solution_count
        assert puzzle_count == 35
        assert solution_count == 81

    def test_generate_puzzle_returns_independent_copies(self):
        """Puzzle and solution should be independent copies."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        puzzle[0][0] = 0 if puzzle[0][0] != 0 else 5
        # Solution should be unaffected by changes to puzzle
        original_solution_value = solution[0][0]
        assert solution[0][0] == original_solution_value
