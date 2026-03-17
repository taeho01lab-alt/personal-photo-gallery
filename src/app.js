import {
  DEFAULT_BOARD,
  createGameState,
  queueDirection,
  stepGame,
  togglePause,
} from "./snake.js";

const TICK_MS = 140;

const boardElement = document.getElementById("board");
const scoreElement = document.getElementById("score");
const statusElement = document.getElementById("status");
const pauseButton = document.getElementById("pause-button");
const restartButton = document.getElementById("restart-button");
const controlButtons = document.querySelectorAll("[data-direction]");

let state = createGameState({ board: DEFAULT_BOARD });
let timerId = null;

function pointKey(point) {
  return point.x + "," + point.y;
}

function getStatusMessage(nextState) {
  if (nextState.status === "ready") {
    return "Press an arrow key, WASD, or the controls below to begin.";
  }

  if (nextState.status === "over") {
    return "Game over. Press Restart or R to play again.";
  }

  if (nextState.isPaused) {
    return "Paused. Press Space or Pause to continue.";
  }

  return "Keep going.";
}

function render() {
  scoreElement.textContent = String(state.score);
  statusElement.textContent = getStatusMessage(state);
  pauseButton.textContent = state.isPaused ? "Resume" : "Pause";

  const snakeCells = new Set(state.snake.map(pointKey));
  const headKey = pointKey(state.snake[0]);
  const foodKey = state.food ? pointKey(state.food) : "";
  const cells = [];

  for (let y = 0; y < state.board.rows; y += 1) {
    for (let x = 0; x < state.board.columns; x += 1) {
      const key = pointKey({ x, y });
      const classes = ["cell"];

      if (snakeCells.has(key)) {
        classes.push("cell--snake");
      }

      if (key === headKey) {
        classes.push("cell--head");
      }

      if (key === foodKey) {
        classes.push("cell--food");
      }

      cells.push(`<div class="${classes.join(" ")}" role="gridcell" aria-label="${key}"></div>`);
    }
  }

  boardElement.innerHTML = cells.join("");
}

function tick() {
  state = stepGame(state);
  if (state.status === "over" && timerId !== null) {
    window.clearInterval(timerId);
    timerId = null;
  }
  render();
}

function startLoop() {
  if (timerId !== null) {
    return;
  }

  timerId = window.setInterval(tick, TICK_MS);
}

function restart() {
  state = createGameState({ board: DEFAULT_BOARD });
  render();
}

function handleDirection(direction) {
  state = queueDirection(state, direction);
  render();
  startLoop();
}

const keyDirectionMap = {
  ArrowUp: "UP",
  ArrowDown: "DOWN",
  ArrowLeft: "LEFT",
  ArrowRight: "RIGHT",
  w: "UP",
  a: "LEFT",
  s: "DOWN",
  d: "RIGHT",
};

document.addEventListener("keydown", (event) => {
  const key = event.key.length === 1 ? event.key.toLowerCase() : event.key;
  const direction = keyDirectionMap[key];

  if (direction) {
    event.preventDefault();
    handleDirection(direction);
    return;
  }

  if (event.key === " " || event.code === "Space") {
    event.preventDefault();
    state = togglePause(state);
    render();
    startLoop();
    return;
  }

  if (key === "r") {
    restart();
  }
});

pauseButton.addEventListener("click", () => {
  state = togglePause(state);
  render();
  startLoop();
});

restartButton.addEventListener("click", restart);

controlButtons.forEach((button) => {
  button.addEventListener("click", () => {
    handleDirection(button.dataset.direction);
  });
});

render();
