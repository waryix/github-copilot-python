import copy
import random

SIZE = 9
EMPTY = 0
DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 30,
}
_BASE_TEMPLATE = [
    [0, 0, 0, 0, 0, 0, 0, 1, 0], [4, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 5, 0, 4, 0, 7],
    [0, 0, 8, 0, 0, 0, 3, 0, 0], [0, 0, 1, 0, 9, 0, 0, 0, 0],
    [3, 0, 0, 4, 0, 0, 2, 0, 0], [0, 5, 0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 8, 0, 6, 0, 0, 0],
]
_BASE_SOLUTION = None


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def get_clue_count_for_difficulty(difficulty='medium'):
    normalized = (difficulty or 'medium').lower()
    if normalized not in DIFFICULTY_CLUES:
        raise ValueError(f"Unsupported difficulty: {difficulty}")
    return DIFFICULTY_CLUES[normalized]


def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def validate_board(board):
    """Return True when a board is structurally valid and consistent with Sudoku rules."""
    if len(board) != SIZE or any(len(row) != SIZE for row in board):
        return False

    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            if value < 1 or value > SIZE:
                return False
            for x in range(SIZE):
                if x != col and board[row][x] == value:
                    return False
            for y in range(SIZE):
                if y != row and board[y][col] == value:
                    return False
            start_row = (row // 3) * 3
            start_col = (col // 3) * 3
            for r in range(start_row, start_row + 3):
                for c in range(start_col, start_col + 3):
                    if (r != row or c != col) and board[r][c] == value:
                        return False
    return True


def count_solutions(board, limit=2):
    """Count valid Sudoku completions for a board up to a given limit."""
    if limit <= 0:
        return 0

    working_board = deep_copy(board)
    if not validate_board(working_board):
        return 0

    solution_count = 0

    row_masks = [0] * SIZE
    column_masks = [0] * SIZE
    box_masks = [0] * SIZE
    for row in range(SIZE):
        for col in range(SIZE):
            value = working_board[row][col]
            if value:
                bit = 1 << value
                row_masks[row] |= bit
                column_masks[col] |= bit
                box_masks[(row // 3) * 3 + col // 3] |= bit

    def backtrack():
        nonlocal solution_count
        if solution_count >= limit:
            return

        best_cell = None
        best_candidates = None

        for row in range(SIZE):
            for col in range(SIZE):
                if working_board[row][col] != EMPTY:
                    continue
                box = (row // 3) * 3 + col // 3
                used = row_masks[row] | column_masks[col] | box_masks[box]
                candidates = [candidate for candidate in range(1, SIZE + 1)
                              if not used & (1 << candidate)]
                if not candidates:
                    return
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_cell = (row, col)
                    best_candidates = candidates
                    if len(best_candidates) == 1:
                        break
            if best_candidates is not None and len(best_candidates) == 1:
                break

        if best_cell is None:
            solution_count += 1
            return

        row, col = best_cell
        box = (row // 3) * 3 + col // 3
        for candidate in best_candidates:
            bit = 1 << candidate
            working_board[row][col] = candidate
            row_masks[row] |= bit
            column_masks[col] |= bit
            box_masks[box] |= bit
            backtrack()
            row_masks[row] &= ~bit
            column_masks[col] &= ~bit
            box_masks[box] &= ~bit
            working_board[row][col] = EMPTY
            if solution_count >= limit:
                return

    backtrack()
    return solution_count


def remove_cells(board, clues):
    if clues < 0 or clues > SIZE * SIZE:
        raise ValueError("clues must be between 0 and 81")

    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)
             if board[row][col] != EMPTY]
    if len(cells) < clues:
        raise ValueError("Cannot request more clues than the board contains.")
    random.shuffle(cells)
    for row, col in cells[:len(cells) - clues]:
        board[row][col] = EMPTY
    return board


def _remove_cells_preserving_uniqueness(board, clues):
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)
    for row, col in cells:
        if sum(cell != EMPTY for current_row in board for cell in current_row) == clues:
            return board
        value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board, limit=2) != 1:
            board[row][col] = value
    if sum(cell != EMPTY for current_row in board for cell in current_row) == clues:
        return board
    raise RuntimeError(f"Unable to reach {clues} clues while preserving a unique solution.")


def generate_puzzle(clues=35):
    if clues < 0 or clues > SIZE * SIZE:
        raise ValueError("clues must be between 0 and 81")

    global _BASE_SOLUTION
    if _BASE_SOLUTION is None:
        _BASE_SOLUTION = deep_copy(_BASE_TEMPLATE)
        if not fill_board(_BASE_SOLUTION):
            raise RuntimeError("Unable to establish a unique Sudoku base puzzle.")
    solution = deep_copy(_BASE_SOLUTION)
    template = deep_copy(_BASE_TEMPLATE)

    puzzle = deep_copy(template)
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)
             if puzzle[row][col] == EMPTY]
    random.shuffle(cells)
    for row, col in cells[:max(0, clues - 17)]:
        puzzle[row][col] = solution[row][col]
    return puzzle, solution
