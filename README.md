# learn_to_write

Turn any X (Twitter) account into a reusable writing style you can apply to anything.

Scrape someone's posts, run a deep style analysis, and generate a **Claude Scale** — a portable prompt that captures exactly how they write. Use it to learn their techniques, or feed it to Claude to rewrite any content in their voice.

## The idea

Everyone has a distinct writing voice. Short punchy takes. Long threaded breakdowns. Lowercase no-punctuation vibes. Formal and polished. The patterns are there — most people just can't articulate what makes a voice *that voice*.

This tool reverse-engineers it. It reads hundreds of someone's posts, measures everything quantifiable about how they write, then uses Claude to synthesize it into a concrete, actionable style guide.

## The pipeline

There are three stages. Each one produces an artifact that feeds into the next.

```
  SCRAPE                    ANALYZE                   GENERATE
  ──────                    ───────                   ────────
  @handle                   Raw posts                 Style profile
     │                         │                          │
     ▼                         ▼                          ▼
  Playwright               Statistical               Claude API
  fresh browser            analysis                   synthesis
     │                         │                          │
     ▼                         ▼                          ▼
  data/{handle}.json       data/{handle}_profile.json scales/{handle}_scale.md
  (raw posts + metrics)    (quantified style)         (the Claude Scale)
```

### Stage 1: Scrape (`src/scraper.py`)

Playwright launches a **fresh Chromium instance** — no cookies, no login, no stored state. This is intentional: your real X account is never involved.

What happens:
1. Opens `x.com/{handle}` in a clean browser context with a realistic user agent, viewport (1920x1080), timezone, and locale
2. Blocks all images, videos, and fonts to minimize bandwidth and speed up scrolling
3. Dismisses any login prompts or cookie banners that X throws at anonymous visitors
4. Scrolls the timeline repeatedly, extracting posts from the DOM after each scroll
5. Deduplicates posts by their first 100 characters (X re-renders posts as you scroll)
6. Stops when it hits the target count or when 5 consecutive scrolls produce no new posts
7. Adds random delays (1-4 seconds) between actions to mimic human browsing

For each post, it captures:
- **Text content** (the actual post)
- **Timestamp** (ISO datetime)
- **Likes, retweets, replies** (engagement counts)
- **Repost flag** (reposts are filtered out — we only want original writing)

Output: `data/{handle}_{timestamp}.json`

```json
{
  "handle": "somewriter",
  "scraped_at": "20260307_143022",
  "count": 247,
  "posts": [
    {
      "text": "The best writing advice is just: delete more.",
      "timestamp": "2026-02-15T09:23:00.000Z",
      "likes": "2.4K",
      "retweets": "312",
      "replies": "89",
      "is_repost": false
    }
  ]
}
```

### Stage 2: Analyze (`src/analyzer.py`)

Takes the raw posts and runs them through six analysis passes to build a quantified style profile.

**Length distribution** — Are they a one-liner person or a paragraph writer?
- Average characters and words per post
- What percentage of posts are short (<100 chars) vs. long (>200 chars)
- Min/max range

**Sentence structure** — How do they build posts?
- Average sentences per post
- How often they use line breaks, bullet lists, threads
- What percentage open with a question

**Vocabulary** — What words define their voice?
- Top 30 most-used content words (stop words filtered out)
- Unique word ratio (vocabulary diversity)
- Average word length (simple vs. complex language)

**Tone markers** — What's the energy?
- Exclamation marks, question marks, ellipsis per post
- ALL CAPS word frequency
- Emoji, hashtag, @mention, and URL density
- Informal language percentage (slang like "tbh", "ngl", "gonna")

**Formatting habits** — The small things that define a voice
- Do they start posts lowercase?
- Do they skip ending punctuation?
- Parenthetical asides, em dashes, quotation usage

**Engagement correlation** — What actually works?
- Top 10 highest-engagement posts (ranked by likes + 2x retweets)
- 20 diverse sample posts picked across the length spectrum

Output: `data/{handle}_profile.json`

```json
{
  "total_posts": 247,
  "length": {
    "avg_chars": 156,
    "avg_words": 28,
    "short_posts_pct": 34,
    "long_posts_pct": 22
  },
  "structure": {
    "avg_sentences_per_post": 2.3,
    "line_breaks_pct": 41,
    "question_opener_pct": 18
  },
  "tone": {
    "exclamation_marks_per_post": 0.8,
    "emoji_count_per_post": 0.3,
    "informal_pct": 12
  },
  "formatting": {
    "starts_lowercase_pct": 45,
    "no_period_ending_pct": 67
  },
  "vocabulary": {
    "unique_word_ratio": 0.412,
    "top_words": [["people", 89], ["think", 67], ["build", 54]],
    "avg_word_length": 4.8
  },
  "top_posts": [...],
  "sample_posts": [...]
}
```

### Stage 3: Generate (`src/scale_generator.py`)

This is where the numbers become a voice. The style profile, top posts, and sample posts are sent to Claude with a detailed prompt asking it to produce a **Claude Scale** — a structured document with nine sections:

| Section | What it captures |
|---------|-----------------|
| **Voice Identity** | 2-3 sentence summary of who this writer is on the page |
| **Sentence Mechanics** | Length, rhythm, punctuation, capitalization, line breaks |
| **Word Choice & Vocabulary** | Register, signature phrases, jargon, slang |
| **Structural Patterns** | How they open, build, and close posts |
| **Rhetorical Devices** | Questions, analogies, humor, emphasis, opinions |
| **Engagement Patterns** | What gets traction, hooks, calls to action |
| **Distinctive Quirks** | Unique habits and things they never do |
| **Rewrite Rules** | 5-7 concrete "When you see X, do Y" rules |
| **Example Transformations** | 3 generic statements rewritten in their style |

The scale is designed to work as a **system prompt**. Paste it into any Claude conversation and Claude will adopt that voice for everything it writes.

Output: `scales/{handle}_scale.md`

### Stage 4: Apply

Once you have a scale, you can rewrite any text in that person's style. The scale is loaded as Claude's system prompt, and your content is sent as the user message with instructions to transform the voice while preserving the meaning.

## Setup

```bash
git clone https://github.com/shawnpang/learn_to_write.git
cd learn_to_write

pip install -r requirements.txt
playwright install chromium

# Set your Anthropic API key
cp .env.example .env
# Edit .env and add your key
```

**Requirements:** Python 3.10+, an Anthropic API key

## Usage

### Run everything at once

```bash
python main.py pipeline somehandle --max-posts 300
```

This scrapes, analyzes, and generates in sequence. At the end you get:
```
Data:    data/somehandle_20260307_143022.json
Profile: data/somehandle_profile.json
Scale:   scales/somehandle_scale.md
```

### Run each step separately

Useful if you want to tweak the analysis or re-generate the scale with a different model.

```bash
# Step 1: Scrape posts
python main.py scrape somehandle --max-posts 300

# Step 2: Build style profile from scraped data
python main.py analyze somehandle data/somehandle_20260307_143022.json

# Step 3: Generate the Claude Scale from the profile
python main.py generate somehandle data/somehandle_profile.json

# Step 4: Rewrite content using the scale
python main.py apply scales/somehandle_scale.md "Your content here"
```

### Options

| Flag | Where | Description |
|------|-------|-------------|
| `--max-posts N` | scrape, pipeline | Number of posts to collect (default: 200) |
| `--visible` | scrape, pipeline | Show the browser window while scraping |
| `--model` | generate, apply, pipeline | Claude model to use (default: claude-sonnet-4-20250514) |

### How to use a Claude Scale

**Option A: CLI rewrite**
```bash
python main.py apply scales/somehandle_scale.md "We are launching a new product next week."
```

**Option B: Paste into Claude**
Open the generated `.md` file, copy the contents, and paste it at the start of any Claude conversation. Everything Claude writes in that conversation will follow the style.

**Option C: Use as a system prompt via the API**
Load the scale file as the `system` parameter in your Anthropic API calls.

## Project structure

```
learn_to_write/
├── main.py                  # CLI — ties everything together
├── src/
│   ├── scraper.py           # Stage 1: Playwright scraper
│   ├── analyzer.py          # Stage 2: Statistical style analysis
│   └── scale_generator.py   # Stage 3: Claude Scale generation + apply
├── data/                    # Scraped posts and style profiles (gitignored)
├── scales/                  # Generated Claude Scales (gitignored)
├── requirements.txt
├── .env.example
└── .gitignore
```

## How the scraper stays safe

The scraper never touches your real X account. Every run:
- Launches a brand new Chromium process with no persistent storage
- Creates a fresh browser context (no cookies, no cache, no history)
- Uses a generic user agent string — not your real browser fingerprint
- Blocks media loading to reduce network footprint
- Adds randomized human-like delays between scrolls
- Only reads publicly visible posts — no authentication, no API keys for X

## Privacy & ethics

- Only scrapes publicly visible content
- No X account login required or used
- Generated scales are for learning and improving your own writing
- Don't use this to impersonate people — use it to learn what makes good writing work
