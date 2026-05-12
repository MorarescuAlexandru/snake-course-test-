# AGENTS.md — Snake Game

## Quick start

```bash
pip install pygame
python snake_game.py
```

- Single-file pygame game, no package structure.
- Entrypoint: `snake_game.py` — run directly, no `__main__.py` or module imports.
- No tests, no linting, no type checking, no CI.
- Game tick rate: 10 FPS. Speed ramps up as score rises (+1 FPS per 5 points, cap 20 FPS).
- WIDTH, HEIGHT, CELL_SIZE are hardcoded globals (lines 10-12).
- State machine: MENU → PLAYING → (PAUSED | GAMEOVER) → MENU.
- High score persisted to `highscore.txt` via `load_highscore()` / `save_highscore()`.
- Snake rendered as circles (not rectangles) with eyes on head; body color gradients from head to tail.
- Food pulses with `math.sin(time * 0.005)`.
