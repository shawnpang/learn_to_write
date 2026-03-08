# learn_to_write

Turn any X (Twitter) account into a reusable writing style. Scrape their posts, analyze the patterns, and generate a **Claude Skill** — a style guide that lets you write like anyone or transform any content to match their voice.

Built for [Claude Code](https://claude.ai/claude-code). No API keys, no CLI to learn. Just slash commands.

## Setup

```bash
git clone https://github.com/shawnpang/learn_to_write.git
cd learn_to_write
pip install playwright && playwright install chromium
```

That's it. Open the project in Claude Code and use the slash commands.

## Usage

### Full pipeline — one command

```
/learn-to-write @somehandle 300
```

This scrapes 300 posts, analyzes the writing style, and generates a Claude Skill. Everything saved automatically.

### Step by step

```
/scrape @somehandle 300          # Scrape posts → data/somehandle/posts.csv
/generate-skill @somehandle      # Analyze CSV → data/somehandle/skill.md
/apply-skill @somehandle "Your content here"   # Rewrite in their style
```

### What you get

```
data/somehandle/
  posts.csv    # Raw posts with engagement metrics
  skill.md     # The Claude Skill
```

## What's a Claude Skill?

A structured writing style guide with 9 sections:

| Section | What it captures |
|---------|-----------------|
| **Voice Identity** | 2-3 sentence summary of who this writer is on the page |
| **Sentence Mechanics** | Length, rhythm, punctuation, capitalization, line breaks |
| **Word Choice** | Register, signature phrases, jargon, slang |
| **Structural Patterns** | How they open, build, and close posts |
| **Rhetorical Devices** | Questions, analogies, humor, emphasis, opinions |
| **Engagement Patterns** | What gets traction, hooks, calls to action |
| **Distinctive Quirks** | Unique habits and things they never do |
| **Rewrite Rules** | 5-7 concrete "When you see X, do Y" rules |
| **Example Transformations** | 3 generic statements rewritten in their style |

You can also paste a Claude Skill into any Claude conversation directly and it will adopt that voice.

## How it works

```
  SCRAPE + SEARCH                     ANALYZE + GENERATE
  ───────────────                     ──────────────────
  Playwright scraper                  Claude Code reads the CSV,
  + web search fallback               analyzes all writing patterns,
  collects posts into CSV             and generates the Claude Skill
       │                                     │
       ▼                                     ▼
  data/{handle}/posts.csv                   data/{handle}/skill.md
```

**Stage 1: Collect posts** — Two methods, used together:

1. **Playwright scraper** (`src/scraper.py` + `src/stealth.py`) — Launches stealth Chromium with persistent browser profiles, bezier mouse movement, variable scrolling, reading pauses, and human behavior simulation. Gets ~30-60 posts per session with full engagement data (likes, retweets, replies).

2. **Web search supplement** — X limits anonymous browsing, so Claude Code runs web searches to find additional tweets indexed by Google. Tweet text is extracted from search result titles. This can find hundreds of posts that the scraper can't reach.

Both sources merge into a single CSV. Run `/scrape` multiple times to accumulate more data.

**Stage 2: Analyze + Generate** — Claude Code reads the CSV directly and does the analysis itself. No separate Python scripts, no API keys needed. Claude Code examines sentence structure, vocabulary, tone markers, formatting habits, and engagement patterns across all posts, then synthesizes a Claude Skill with concrete rewrite rules and example transformations.

## Project structure

```
learn_to_write/
├── CLAUDE.md                        # Project instructions for Claude Code
├── README.md
├── requirements.txt                 # Just playwright
├── .claude/commands/
│   ├── scrape.md                    # /scrape @handle [count]
│   ├── generate-skill.md           # /generate-skill @handle
│   ├── apply-skill.md              # /apply-skill @handle <text>
│   └── learn-to-write.md           # /learn-to-write @handle [count]
├── src/
│   ├── __init__.py
│   ├── scraper.py                   # Playwright scraper, outputs CSV
│   └── stealth.py                   # Browser stealth + human simulation
├── data/                            # One subfolder per person (posts.csv + skill.md)
│   ├── zarazhangrui/
│   │   ├── posts.csv
│   │   └── skill.md
│   └── ...
└── browser_profiles/                # Persistent browser state (gitignored)
```

## How the scraper avoids detection

**Your account is never involved.** No login, no cookies from your real browser, no X credentials.

**The browser looks real.** Stealth patches hide every standard automation signal:
- `navigator.webdriver` → `undefined` (Playwright normally sets this to `true`)
- `window.chrome` runtime → present (missing in default Playwright)
- `navigator.plugins` → 3 realistic Chrome plugins (Playwright shows 0)
- WebGL renderer → real GPU string instead of "SwiftShader"
- Media devices, connection info, permissions API → all match real Chrome

**The browser has history.** Persistent profiles accumulate cookies, localStorage, and cache across runs. X sees a returning visitor, not a fresh install.

**The behavior looks human.** Mouse on bezier curves, variable scroll distances with momentum, reading pauses that decrease over time (fatigue), random post clicks, periodic 5-15s breaks.

## Privacy & ethics

- Only scrapes publicly visible content
- No X login required or used
- Skills are for learning and improving your own writing
- Don't use this to impersonate people
