# learn_to_write

This project scrapes X (Twitter) accounts and generates "Claude Scales" — writing style guides that capture exactly how someone writes.

## Setup

Only dependency is Playwright:
```bash
pip install playwright && playwright install chromium
```

## How it works

1. **Scraper** (`src/scraper.py` + `src/stealth.py`) — Playwright with stealth patches and human behavior simulation scrapes posts from any public X account. Outputs CSV to `data/`.
2. **You (Claude Code)** — Read the CSV, analyze the writing style, and generate a Claude Scale. Save it to `scales/`.

There is no separate analyzer or API script. Claude Code does the analysis and generation directly.

## Slash commands

- `/scrape @handle [count]` — Scrape posts from an X account, save as CSV
- `/generate-scale @handle` — Read scraped CSV, analyze style, generate Claude Scale
- `/apply-scale @handle <text>` — Rewrite text using a saved Claude Scale
- `/learn-to-write @handle [count]` — Full pipeline: scrape + analyze + generate scale

## File layout

- `data/*.csv` — Scraped posts (text, timestamp, likes, retweets, replies)
- `scales/*_scale.md` — Generated Claude Scales
- `browser_profiles/` — Persistent browser state (cookies, cache)
- `src/scraper.py` — Scraper entry point: `python3 -m src.scraper <handle> [max_posts] [--visible]`
- `src/stealth.py` — Browser stealth patches and human behavior simulation

## Running the scraper manually

```bash
python3 -m src.scraper <handle> [max_posts] [--visible]
```

- `handle` — X username without @
- `max_posts` — number to scrape (default 200)
- `--visible` — show browser window

## Important notes

- The scraper NEVER logs in. It uses a fresh anonymous browser profile.
- Images load normally (blocking is detectable).
- Mouse moves on bezier curves, scrolling has natural variance, periodic breaks simulate real browsing.
- CSV files use the format: `data/{handle}_{YYYYMMDD_HHMMSS}.csv`
