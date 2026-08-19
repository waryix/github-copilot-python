"""
Baseline tests for Flask application routes.
Tests the existing Flask endpoints without modifying the implementation.
"""
import pytest
import json
import app as app_module


class TestIndexRoute:
    """Test the index (/) route."""

    def test_index_returns_200(self, client):
        """GET / should return status 200."""
        response = client.get('/')
        assert response.status_code == 200

    def test_index_returns_html(self, client):
        """GET / should return HTML content."""
        response = client.get('/')
        assert response.content_type.startswith('text/html')

    def test_index_contains_sudoku_board_div(self, client):
        """GET / should return HTML containing sudoku-board div."""
        response = client.get('/')
        assert b'sudoku-board' in response.data

    def test_index_contains_new_game_button(self, client):
        """GET / should return HTML containing new-game button."""
        response = client.get('/')
        assert b'new-game' in response.data


class TestNewGameRoute:
    """Test the new game (/new) route."""

    def test_new_game_returns_200(self, client):
        """GET /new should return status 200."""
        response = client.get('/new')
        assert response.status_code == 200

    def test_new_game_returns_json(self, client):
        """GET /new should return JSON response."""
        response = client.get('/new')
        assert response.content_type.startswith('application/json')

    def test_new_game_returns_puzzle_key(self, client):
        """GET /new should return JSON with 'puzzle' key."""
        response = client.get('/new')
        data = json.loads(response.data)
        assert 'puzzle' in data
        assert isinstance(data['puzzle'], list)

    def test_new_game_puzzle_is_9x9(self, client):
        """Returned puzzle should be 9x9 grid."""
        response = client.get('/new')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        assert len(puzzle) == 9
        for row in puzzle:
            assert len(row) == 9

    def test_new_game_puzzle_contains_valid_values(self, client):
        """Puzzle should only contain 0 and values 1-9."""
        response = client.get('/new')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        for row in puzzle:
            for cell in row:
                assert cell == 0 or (1 <= cell <= 9)

    def test_new_game_stores_in_session(self, client):
        """GET /new should store puzzle and solution in CURRENT."""
        client.get('/new')
        assert app_module.CURRENT['puzzle'] is not None
        assert app_module.CURRENT['solution'] is not None

    def test_new_game_default_clues_35(self, client):
        """GET /new with no clues param should create puzzle with 35 clues."""
        response = client.get('/new')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        clues_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clues_count == 35

    def test_new_game_custom_clues(self, client):
        """GET /new should accept custom clues parameter."""
        response = client.get('/new?clues=40')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        clues_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clues_count == 40

    def test_new_game_clues_as_string(self, client):
        """GET /new should handle clues parameter as string."""
        response = client.get('/new?clues=30')
        assert response.status_code == 200
        data = json.loads(response.data)
        puzzle = data['puzzle']
        clues_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clues_count == 30

    def test_new_game_replaces_previous_game(self, client):
        """Calling /new twice should replace previous puzzle and solution."""
        response1 = client.get('/new')
        puzzle1 = json.loads(response1.data)['puzzle']
        old_puzzle = app_module.CURRENT['puzzle']

        response2 = client.get('/new')
        puzzle2 = json.loads(response2.data)['puzzle']
        new_puzzle = app_module.CURRENT['puzzle']

        # Puzzles might be same or different (random generation),
        # but CURRENT should be updated
        assert new_puzzle == puzzle2

    def test_new_game_uses_selected_difficulty(self, client):
        response = client.get('/new?difficulty=easy')
        data = response.get_json()
        assert data['difficulty'] == 'easy'
        assert sum(cell != 0 for row in data['puzzle'] for cell in row) == 45

    def test_invalid_board_values_return_bad_request(self, client):
        client.get('/new')
        response = client.post('/check', json={'board': [['x'] * 9 for _ in range(9)]})
        assert response.status_code == 400


class TestHintRoute:
    def test_hint_fills_one_empty_cell_and_tracks_usage(self, client):
        client.get('/new')
        board = [row[:] for row in app_module.CURRENT['puzzle']]
        response = client.post('/hint', json={'board': board})
        data = response.get_json()
        assert response.status_code == 200
        assert data['hints_used'] == 1
        assert board[data['row']][data['col']] == 0


class TestCheckRoute:
    """Test the check solution (/check) POST route."""

    def test_check_requires_game_in_progress(self, client):
        """POST /check without prior /new should return error."""
        # Reset CURRENT to no game
        app_module.CURRENT['puzzle'] = None
        app_module.CURRENT['solution'] = None

        response = client.post('/check', 
                              data=json.dumps({'board': []}),
                              content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_check_returns_json(self, client):
        """POST /check should return JSON response."""
        client.get('/new')
        response = client.post('/check',
                              data=json.dumps({'board': [[0]*9 for _ in range(9)]}),
                              content_type='application/json')
        assert response.content_type.startswith('application/json')

    def test_check_returns_incorrect_cells(self, client):
        """POST /check should return 'incorrect' key with list of cells."""
        client.get('/new')
        board = [[0]*9 for _ in range(9)]
        response = client.post('/check',
                              data=json.dumps({'board': board}),
                              content_type='application/json')
        data = json.loads(response.data)
        assert 'incorrect' in data
        assert isinstance(data['incorrect'], list)

    def test_check_detects_incorrect_cells(self, client):
        """POST /check should identify cells that don't match solution."""
        client.get('/new')
        solution = app_module.CURRENT['solution']
        # Create board with wrong value in a cell
        board = [row[:] for row in solution]  # Copy solution
        # Find a cell and change it
        board[0][0] = 5 if solution[0][0] != 5 else 6
        
        response = client.post('/check',
                              data=json.dumps({'board': board}),
                              content_type='application/json')
        data = json.loads(response.data)
        incorrect = data['incorrect']
        # Should have found the incorrect cell
        assert len(incorrect) > 0
        assert [0, 0] in incorrect

    def test_check_accepts_complete_solution(self, client):
        """POST /check with correct solution should return empty incorrect list."""
        client.get('/new')
        solution = app_module.CURRENT['solution']
        board = [row[:] for row in solution]  # Copy solution exactly

        response = client.post('/check',
                              data=json.dumps({'board': board}),
                              content_type='application/json')
        data = json.loads(response.data)
        incorrect = data['incorrect']
        assert len(incorrect) == 0

    def test_check_multiple_incorrect_cells(self, client):
        """POST /check should detect multiple incorrect cells."""
        client.get('/new')
        solution = app_module.CURRENT['solution']
        board = [row[:] for row in solution]  # Copy solution
        # Change multiple cells
        board[0][0] = 5 if solution[0][0] != 5 else 6
        board[1][1] = 7 if solution[1][1] != 7 else 8
        board[2][2] = 3 if solution[2][2] != 3 else 4

        response = client.post('/check',
                              data=json.dumps({'board': board}),
                              content_type='application/json')
        data = json.loads(response.data)
        incorrect = data['incorrect']
        assert len(incorrect) == 3

    def test_check_board_9x9_grid(self, client):
        """POST /check should accept 9x9 board."""
        client.get('/new')
        board = [[0]*9 for _ in range(9)]
        response = client.post('/check',
                              data=json.dumps({'board': board}),
                              content_type='application/json')
        assert response.status_code == 200


class TestGameFlow:
    """Test the complete game flow: new game -> check solution."""

    def test_complete_game_flow(self, client):
        """Test basic game flow: start game and check solution."""
        # Start new game
        response = client.get('/new')
        assert response.status_code == 200
        puzzle_data = json.loads(response.data)
        puzzle = puzzle_data['puzzle']

        # Verify puzzle structure
        assert len(puzzle) == 9
        for row in puzzle:
            assert len(row) == 9

        # Verify puzzle and solution are stored
        stored_puzzle = app_module.CURRENT['puzzle']
        stored_solution = app_module.CURRENT['solution']
        assert stored_puzzle is not None
        assert stored_solution is not None

        # Submit solution
        response = client.post('/check',
                              data=json.dumps({'board': stored_solution}),
                              content_type='application/json')
        assert response.status_code == 200
        check_data = json.loads(response.data)
        assert 'incorrect' in check_data
        assert len(check_data['incorrect']) == 0

    def test_game_flow_with_wrong_answers(self, client):
        """Test game flow with incorrect submission."""
        # Start new game
        client.get('/new')
        solution = app_module.CURRENT['solution']

        # Create board with intentional mistakes
        board = [row[:] for row in solution]
        for i in range(min(5, 9)):
            board[i][0] = (board[i][0] % 9) + 1

        # Check solution
        response = client.post('/check',
                              data=json.dumps({'board': board}),
                              content_type='application/json')
        check_data = json.loads(response.data)
        assert len(check_data['incorrect']) > 0
