# learn_to_write

This project scrapes X (Twitter) accounts and generates "Claude Skills" — writing style guides that capture exactly how someone writes.

## Primary deliverable

`learn-to-write.md` — a portable Claude Skill that anyone can drop into their `.claude/commands/` folder. When run, it auto-clones this repo, installs dependencies, scrapes posts, and generates a writing style skill. No manual setup.

## Setup (for local development)

Only dependency is Playwright:
```bash
pip install playwright && playwright install chromium
```

## How it works

1. **Scraper** (`src/scraper.py` + `src/stealth.py`) — Playwright with stealth patches and human behavior simulation scrapes posts from any public X account. Outputs CSV to `data/<handle>/posts.csv`.
2. **You (Claude Code)** — Read the CSV, analyze the writing style, and generate a Claude Skill. Save it to `data/<handle>/skill.md`.

Each person gets their own subfolder under `data/`. Everything is tracked in git.

## Slash commands

- `/learn-to-write @handle [count]` — Full pipeline: scrape + analyze + generate skill (default 30 posts)
- `/scrape @handle [count]` — Same as above (when running from inside this repo)
- `/generate-skill @handle` — Re-generate a Claude Skill from existing scraped data
- `/apply-skill @handle <text>` — Rewrite text using a saved Claude Skill

## File layout

```
data/
  zarazhangrui/
    posts.csv          # Scraped posts (text, timestamp, likes, retweets, replies)
    skill.md           # Generated Claude Skill
  anotherhandle/
    posts.csv
    skill.md
```

- `learn-to-write.md` — The portable Claude Skill (main deliverable)
- `browser_profiles/` — Persistent browser state (cookies, cache) — gitignored
- `src/scraper.py` — Scraper entry point: `python3 -m src.scraper <handle> [max_posts] [--visible]`
- `src/stealth.py` — Browser stealth patches and human behavior simulation

## Running the scraper manually

```bash
python3 -m src.scraper <handle> [max_posts] [--visible]
```

- `handle` — X username without @
- `max_posts` — number to scrape (default 30)
- `--visible` — show browser window

## Important notes

- The scraper NEVER logs in. It uses a fresh anonymous browser profile.
- Default is 30 posts to avoid getting accounts rate-limited.
- Mouse moves on bezier curves, scrolling has natural variance, periodic breaks simulate real browsing.
- Posts save to `data/<handle>/posts.csv`, skills save to `data/<handle>/skill.md`.
