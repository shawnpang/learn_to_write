# learn_to_write

Turn any X (Twitter) account into a reusable writing style. Scrape their posts, analyze the patterns, and generate a **Claude Skill** — a style guide that lets you write like anyone or transform any content to match their voice.

## Quick start

Copy [`learn-to-write.md`](learn-to-write.md) into your Claude Code project's `.claude/commands/` folder:

```bash
mkdir -p .claude/commands
curl -o .claude/commands/learn-to-write.md https://raw.githubusercontent.com/shawnpang/learn_to_write/main/learn-to-write.md
```

Then in Claude Code:

```
/learn-to-write @somehandle
```

That's it. Claude will automatically clone the scraper, install Playwright, scrape posts, analyze the writing style, and generate a Claude Skill. No manual setup.

## How it works

When you run the skill, Claude:

1. **Downloads the scraper** (first run only) — clones this repo and installs Playwright
2. **Scrapes posts** — Stealth Playwright browser collects ~30 posts with engagement data
3. **Supplements with web search** — Finds additional posts indexed by Google
4. **Analyzes & generates** — Reads all posts, analyzes writing patterns, generates a 9-section Claude Skill
5. **Saves everything** — `learn_to_write/data/<handle>/posts.csv` + `learn_to_write/data/<handle>/skill.md`

```
  SCRAPE + SEARCH                     ANALYZE + GENERATE
  ───────────────                     ──────────────────
  Playwright scraper                  Claude reads the CSV,
  + web search fallback               analyzes all writing patterns,
  collects posts into CSV             and generates the Claude Skill
       │                                     │
       ▼                                     ▼
  data/{handle}/posts.csv                   data/{handle}/skill.md
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

## If you cloned the repo directly

You can also use the project's built-in slash commands:

```
/scrape @somehandle 30               # Scrape + analyze + generate skill
/generate-skill @somehandle          # Re-generate skill from existing data
/apply-skill @somehandle "Your content here"   # Rewrite in their style
```

Setup:
```bash
pip install playwright && playwright install chromium
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
