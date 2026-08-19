const SIZE = 9;
const SCORE_KEY = 'sudoku_top_scores';
const THEME_KEY = 'sudoku_theme';
let puzzle = [];
let solution = [];
let timerId = null;
let elapsedSeconds = 0;
let currentDifficulty = 'medium';
let hintsUsed = 0;
let gameStartedAt = null;

function pad(value) {
  return String(value).padStart(2, '0');
}

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${pad(minutes)}:${pad(seconds)}`;
}

function startTimer() {
  clearInterval(timerId);
  elapsedSeconds = 0;
  gameStartedAt = Date.now();
  const timerEl = document.getElementById('timer');
  timerEl.textContent = formatTime(elapsedSeconds);
  timerId = setInterval(() => {
    elapsedSeconds = Math.floor((Date.now() - gameStartedAt) / 1000);
    timerEl.textContent = formatTime(elapsedSeconds);
  }, 1000);
}

function stopTimer() {
  if (timerId) {
    clearInterval(timerId);
    timerId = null;
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = String(i);
      input.dataset.col = String(j);
      input.setAttribute('role', 'gridcell');
      input.addEventListener('input', (event) => {
        const val = event.target.value.replace(/[^1-9]/g, '');
        event.target.value = val;
        validateCell(event.target);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz, soln = null) {
  puzzle = puz;
  solution = soln || puzzle.map((row) => [...row]);
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      inp.value = val !== 0 ? String(val) : '';
      inp.disabled = val !== 0;
      inp.className = 'sudoku-cell';
      if (val !== 0) {
        inp.classList.add('prefilled');
      }
      if ((i === 2 || i === 5) && j === 8) {
        inp.classList.add('box-bottom-right');
      }
    }
  }
}

function getBoardFromInputs() {
  const inputs = document.querySelectorAll('.sudoku-cell');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const value = inputs[idx].value;
      board[i][j] = value === '' ? 0 : parseInt(value, 10);
    }
  }
  return board;
}

function setMessage(text, type = 'info') {
  const messageEl = document.getElementById('message');
  messageEl.textContent = text;
  messageEl.className = `message ${type}`;
}

function validateCell(input) {
  const row = Number(input.dataset.row);
  const col = Number(input.dataset.col);
  const value = input.value === '' ? 0 : Number(input.value);
  const locked = input.disabled;
  input.classList.remove('incorrect', 'valid');

  if (locked || value === 0) {
    return;
  }

  if (value < 1 || value > 9) {
    input.classList.add('incorrect');
    return;
  }

  const board = getBoardFromInputs();
  const conflictsWithRules = board.some((boardRow, boardRowIndex) =>
    boardRow.some((cellValue, cellColIndex) => {
      if (boardRowIndex === row && cellColIndex === col) return false;
      if (cellValue !== value) return false;
      return boardRowIndex === row || cellColIndex === col ||
        (Math.floor(boardRowIndex / 3) === Math.floor(row / 3) &&
         Math.floor(cellColIndex / 3) === Math.floor(col / 3));
    })
  );

  if (conflictsWithRules || value !== solution[row][col]) {
    input.classList.add('incorrect');
  } else {
    input.classList.add('valid');
  }
}

async function newGame() {
  const difficulty = document.getElementById('difficulty-select').value;
  currentDifficulty = difficulty;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (data.error) {
    setMessage(data.error, 'error');
    return;
  }
  renderPuzzle(data.puzzle, data.solution);
  setMessage('');
  startTimer();
}

async function checkSolution() {
  const board = getBoardFromInputs();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  if (data.error) {
    setMessage(data.error, 'error');
    return;
  }

  const inputs = document.querySelectorAll('.sudoku-cell');
  inputs.forEach((input) => {
    if (input.disabled) return;
    const row = Number(input.dataset.row);
    const col = Number(input.dataset.col);
    const isIncorrect = data.incorrect.some(([r, c]) => r === row && c === col);
    input.classList.remove('incorrect', 'valid');
    if (isIncorrect) {
      input.classList.add('incorrect');
    } else if (input.value !== '') {
      input.classList.add('valid');
    }
  });

  if (data.solved) {
    stopTimer();
    setMessage(`Congratulations! You solved the ${currentDifficulty} puzzle in ${formatTime(elapsedSeconds)}.`, 'success');
    saveScore();
  } else if (data.incorrect.length > 0) {
    setMessage('Some cells are incorrect. Check the highlighted values.', 'error');
  } else {
    setMessage('Everything looks valid so far.', 'info');
  }
}

async function requestHint() {
  const board = getBoardFromInputs();
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  if (data.error) {
    setMessage(data.error, 'error');
    return;
  }

  hintsUsed += 1;
  const idx = data.row * SIZE + data.col;
  const input = document.querySelectorAll('.sudoku-cell')[idx];
  input.value = String(data.value);
  input.disabled = true;
  input.classList.add('prefilled', 'hinted');
  input.classList.remove('incorrect');
  setMessage(`Hint used (${hintsUsed}).`, 'info');
}

function saveScore() {
  const name = prompt('Enter your name for the Top 10 leaderboard:', 'Player');
  if (!name) {
    return;
  }
  let scores;
  try {
    scores = JSON.parse(localStorage.getItem(SCORE_KEY) || '[]');
  } catch (error) {
    scores = [];
  }
  if (!Array.isArray(scores)) scores = [];
  scores.push({
    name: name.trim() || 'Player',
    time: elapsedSeconds,
    difficulty: currentDifficulty,
    hints: hintsUsed,
    createdAt: Date.now()
  });
  scores.sort((a, b) => a.time - b.time);
  const topScores = scores.slice(0, 10);
  localStorage.setItem(SCORE_KEY, JSON.stringify(topScores));
  renderScores();
}

function renderScores() {
  const scoreboard = document.getElementById('scoreboard');
  let scores;
  try {
    scores = JSON.parse(localStorage.getItem(SCORE_KEY) || '[]');
  } catch (error) {
    scores = [];
  }
  if (!Array.isArray(scores)) scores = [];
  scoreboard.innerHTML = '';
  if (scores.length === 0) {
    const li = document.createElement('li');
    li.textContent = 'No scores yet';
    scoreboard.appendChild(li);
    return;
  }
  scores.forEach((score, index) => {
    const li = document.createElement('li');
    const label = `${index + 1}. ${score.name} — ${formatTime(score.time)} — ${score.difficulty} — hints ${score.hints}`;
    li.textContent = label;
    scoreboard.appendChild(li);
  });
}

function applyTheme(theme) {
  document.body.dataset.theme = theme;
  localStorage.setItem(THEME_KEY, theme);
  const toggle = document.getElementById('theme-toggle');
  toggle.textContent = theme === 'dark' ? '☀️' : '🌙';
}

function toggleTheme() {
  const nextTheme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
}

window.addEventListener('load', () => {
  const savedTheme = localStorage.getItem(THEME_KEY) || 'light';
  applyTheme(savedTheme);
  renderScores();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', requestHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  newGame();
});