# Growth Book Tracker

A self-updating website for a QQQ trend + volatility-target + breadth strategy.

- **The page** (`docs/index.html`) is served by GitHub Pages and fetches `docs/signal.json`.
- **The daily signal** is recomputed by a scheduled GitHub Action (`.github/workflows/refresh-signal.yml`)
  running `gen_signal.py` every weekday after the US close.

Educational tool. Not investment advice.
