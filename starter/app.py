from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

CURRENT = {
    'puzzle': None,
    'solution': None,
    'difficulty': 'medium',
    'hints_used': 0,
    'hint_cells': set(),
    'locked_cells': set(),
}


def _normalize_board(board):
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        raise ValueError('Board must be a 9x9 list.')
    normalized = []
    for row in board:
        if not isinstance(row, list) or len(row) != sudoku_logic.SIZE:
            raise ValueError('Each board row must contain 9 cells.')
        normalized_row = []
        for value in row:
            if value in (None, ''):
                normalized_row.append(0)
                continue
            if isinstance(value, bool):
                raise ValueError('Board values must be integers from 1 to 9.')
            try:
                normalized_value = int(value)
            except (TypeError, ValueError):
                raise ValueError('Board values must be integers from 1 to 9.') from None
            if normalized_value < 0 or normalized_value > sudoku_logic.SIZE:
                raise ValueError('Board values must be between 0 and 9.')
            normalized_row.append(normalized_value)
        normalized.append(normalized_row)
    return normalized


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new')
def new_game():
    clue_override = request.args.get('clues')
    difficulty = request.args.get('difficulty', 'medium')

    if clue_override is not None:
        try:
            clues = int(clue_override)
        except (TypeError, ValueError):
            return jsonify({'error': 'Puzzle clue count must be a number.'}), 400
    else:
        try:
            clues = sudoku_logic.get_clue_count_for_difficulty(difficulty)
        except ValueError:
            return jsonify({'error': 'Unsupported difficulty.'}), 400

    try:
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
    except (RuntimeError, ValueError):
        return jsonify({'error': 'Unable to generate a puzzle. Please try again.'}), 503
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty.lower() if clue_override is None else 'custom'
    CURRENT['hints_used'] = 0
    CURRENT['hint_cells'] = set()
    CURRENT['locked_cells'] = {
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if puzzle[row][col] != 0
    }
    return jsonify({'puzzle': puzzle, 'solution': solution, 'difficulty': CURRENT['difficulty']})


@app.route('/check', methods=['POST'])
def check_solution():
    if CURRENT.get('solution') is None:
        return jsonify({'error': 'No game in progress'}), 400

    try:
        data = request.get_json(force=True, silent=True) or {}
        board = _normalize_board(data.get('board', []))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != CURRENT['solution'][i][j]:
                incorrect.append([i, j])
    solved = not incorrect
    return jsonify({'incorrect': incorrect, 'solved': solved})


@app.route('/hint', methods=['POST'])
def get_hint():
    if CURRENT.get('solution') is None:
        return jsonify({'error': 'No game in progress'}), 400

    try:
        data = request.get_json(force=True, silent=True) or {}
        board = _normalize_board(data.get('board', []))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if board[row][col] != 0:
                continue
            if (row, col) in CURRENT['locked_cells']:
                continue
            board[row][col] = CURRENT['solution'][row][col]
            CURRENT['hints_used'] += 1
            CURRENT['hint_cells'].add((row, col))
            CURRENT['locked_cells'].add((row, col))
            return jsonify({'row': row, 'col': col, 'value': CURRENT['solution'][row][col], 'hints_used': CURRENT['hints_used']})
    return jsonify({'error': 'No empty cells available for a hint.'}), 400


@app.route('/validate', methods=['POST'])
def validate_board():
    if CURRENT.get('solution') is None:
        return jsonify({'error': 'No game in progress'}), 400

    try:
        data = request.get_json(force=True, silent=True) or {}
        board = _normalize_board(data.get('board', []))
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 400

    invalid = []
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            value = board[row][col]
            if value == 0:
                continue
            if CURRENT['puzzle'][row][col] == 0 and value != CURRENT['solution'][row][col]:
                invalid.append([row, col])
    return jsonify({'invalid': invalid})


if __name__ == '__main__':
    app.run(debug=True)