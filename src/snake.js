export const DIRECTIONS = {
  UP: { x: 0, y: -1 },
  DOWN: { x: 0, y: 1 },
  LEFT: { x: -1, y: 0 },
  RIGHT: { x: 1, y: 0 },
};

export const DEFAULT_BOARD = {
  columns: 16,
  rows: 16,
};

function serializePoint(point) {
  return point.x + "," + point.y;
}

function pointsEqual(a, b) {
  return a.x === b.x && a.y === b.y;
}

function isOppositeDirection(current, next) {
  return current.x + next.x === 0 && current.y + next.y === 0;
}

export function createInitialSnake(board = DEFAULT_BOARD) {
  const x = Math.floor(board.columns / 2);
  const y = Math.floor(board.rows / 2);

  return [
    { x, y },
    { x: x - 1, y },
    { x: x - 2, y },
  ];
}

export function getAvailableCells(board, snake) {
  const occupied = new Set(snake.map(serializePoint));
  const cells = [];

  for (let y = 0; y < board.rows; y += 1) {
    for (let x = 0; x < board.columns; x += 1) {
      if (!occupied.has(serializePoint({ x, y }))) {
        cells.push({ x, y });
      }
    }
  }

  return cells;
}

export function spawnFood(board, snake, randomFn = Math.random) {
  const cells = getAvailableCells(board, snake);

  if (cells.length === 0) {
    return null;
  }

  const index = Math.floor(randomFn() * cells.length);
  return cells[index];
}

export function createGameState(options = {}) {
  const board = options.board ?? DEFAULT_BOARD;
  const snake = options.snake ?? createInitialSnake(board);
  const direction = options.direction ?? DIRECTIONS.RIGHT;
  const food = options.food ?? spawnFood(board, snake, options.randomFn);

  return {
    board,
    snake,
    direction,
    queuedDirection: direction,
    food,
    score: options.score ?? 0,
    status: options.status ?? "ready",
    isPaused: options.isPaused ?? false,
  };
}

export function queueDirection(state, directionName) {
  const nextDirection = DIRECTIONS[directionName];

  if (!nextDirection) {
    return state;
  }

  if (state.snake.length > 1 && isOppositeDirection(state.direction, nextDirection)) {
    return state;
  }

  return {
    ...state,
    queuedDirection: nextDirection,
    status: state.status === "ready" ? "running" : state.status,
  };
}

export function togglePause(state) {
  if (state.status === "over" || state.status === "ready") {
    return state;
  }

  return {
    ...state,
    isPaused: !state.isPaused,
  };
}

export function stepGame(state, randomFn = Math.random) {
  if (state.status === "over" || state.status === "ready" || state.isPaused) {
    return state;
  }

  const direction = state.queuedDirection;
  const head = state.snake[0];
  const nextHead = {
    x: head.x + direction.x,
    y: head.y + direction.y,
  };

  const hitsWall =
    nextHead.x < 0 ||
    nextHead.y < 0 ||
    nextHead.x >= state.board.columns ||
    nextHead.y >= state.board.rows;

  if (hitsWall) {
    return {
      ...state,
      direction,
      status: "over",
    };
  }

  const willGrow = state.food !== null && pointsEqual(nextHead, state.food);
  const nextSnake = [nextHead, ...state.snake];

  if (!willGrow) {
    nextSnake.pop();
  }

  const body = nextSnake.slice(1);
  const hitsSelf = body.some((segment) => pointsEqual(segment, nextHead));

  if (hitsSelf) {
    return {
      ...state,
      direction,
      snake: nextSnake,
      status: "over",
    };
  }

  const food = willGrow ? spawnFood(state.board, nextSnake, randomFn) : state.food;
  const score = willGrow ? state.score + 1 : state.score;
  const status = food === null ? "over" : "running";

  return {
    ...state,
    snake: nextSnake,
    direction,
    queuedDirection: direction,
    food,
    score,
    status,
  };
}
