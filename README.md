# Snake

Minimal classic Snake implemented as a dependency-free browser app.

## Files

- `index.html` - single entry page
- `styles.css` - minimal layout and board styling
- `src/snake.js` - deterministic game logic
- `src/app.js` - DOM rendering, keyboard input, timer loop

## Run

Because this repo did not include an existing dev server or frontend toolchain, run the game by opening `index.html` in a browser.

If you prefer serving it locally, use any static file server already available on your machine and open the repo root.

## Navigate

Open the app at the repo root page:

- `./index.html`

## Manual verification

- Start moving with arrow keys and `W`, `A`, `S`, `D`
- Confirm the snake advances one grid cell per tick
- Eat food and confirm the score increments and the snake grows by one segment
- Confirm food never spawns on top of the snake
- Hit a wall and confirm the game ends
- Run into the snake body and confirm the game ends
- Press `Space` or the pause button and confirm movement stops and resumes
- Press `R` or the restart button and confirm the game resets to score `0`

## Notes

- No test runner or app framework was present in this repo, so I did not add framework-specific tests or dependencies.
