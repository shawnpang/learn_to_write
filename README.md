# learn_to_write

Scrape any X (Twitter) account, analyze their writing style, and generate a **Claude Scale** — a portable style guide that lets you write like anyone or transform any content to match their voice.

## How it works

```
@handle → Scrape Posts → Analyze Style → Generate Claude Scale → Write like them
```

1. **Scrape** — Playwright opens a fresh browser (no cookies, no logged-in session) and scrolls through the target account collecting posts
2. **Analyze** — Statistical analysis of sentence structure, vocabulary, tone, formatting habits, and engagement patterns
3. **Generate** — Claude reads the analysis + sample posts and produces a detailed, actionable writing style guide (the "Claude Scale")
4. **Apply** — Feed the scale as a system prompt to Claude. Either write new content or rewrite existing content in that person's exact style

## Setup

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/learn_to_write.git
cd learn_to_write

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Set your Anthropic API key
cp .env.example .env
# Edit .env with your key
```

## Usage

### Full pipeline (recommended)

```bash
python main.py pipeline elonmusk --max-posts 300
```

This runs all three steps and outputs a Claude Scale to `scales/elonmusk_scale.md`.

### Step by step

```bash
# 1. Scrape
python main.py scrape elonmusk --max-posts 300

# 2. Analyze
python main.py analyze elonmusk data/elonmusk_20240101_120000.json

# 3. Generate scale
python main.py generate elonmusk data/elonmusk_profile.json

# 4. Apply scale to rewrite content
python main.py apply scales/elonmusk_scale.md "Your content here"
```

### Options

| Flag | Description |
|------|-------------|
| `--max-posts N` | Number of posts to scrape (default: 200) |
| `--visible` | Show the browser window while scraping |
| `--model` | Claude model to use (default: claude-sonnet-4-20250514) |

## What's a Claude Scale?

A Claude Scale is a structured writing style guide that captures:

- **Voice identity** — The overall personality and tone
- **Sentence mechanics** — Length, rhythm, punctuation habits
- **Word choice** — Register, signature phrases, jargon level
- **Structural patterns** — How they open, build, and close posts
- **Rhetorical devices** — Questions, analogies, humor style
- **Rewrite rules** — Concrete "when you see X, do Y" transformations
- **Example transformations** — Before/after demonstrations

You can paste a Claude Scale into any Claude conversation as context, and it will write in that person's style.

## Project structure

```
learn_to_write/
├── main.py                  # CLI entry point
├── src/
│   ├── scraper.py           # Playwright X scraper (fresh browser each run)
│   ├── analyzer.py          # Statistical style analysis
│   └── scale_generator.py   # Claude Scale generation + application
├── data/                    # Scraped posts & style profiles
├── scales/                  # Generated Claude Scales
├── requirements.txt
└── .env.example
```

## Privacy & ethics

- Uses a fresh browser context every run — no login, no cookies, no account association
- Only scrapes publicly visible posts
- Generated scales are for personal learning and writing improvement
- Be thoughtful about impersonation — use this to learn writing techniques, not to deceive
