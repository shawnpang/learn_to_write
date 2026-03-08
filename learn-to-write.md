---
description: Scrape any X account and generate a writing style skill
argument-hint: <@handle> [max_posts]
allowed-tools: [Bash, Read, Write, Glob, Grep, WebSearch]
---

Learn to write like anyone on X: $ARGUMENTS

## Setup (auto — only runs once)

Check if `learn_to_write/src/scraper.py` exists in the current working directory. If not:

```bash
git clone https://github.com/shawnpang/learn_to_write.git
cd learn_to_write && pip install playwright && playwright install chromium
```

If it already exists, skip setup.

## Step 1: Scrape

Parse the handle from the arguments. Strip any `@` prefix or `https://x.com/` URL prefix. Default to **30** posts if no count is specified.

Run the scraper:
```bash
cd learn_to_write && python3 -m src.scraper <handle> <max_posts>
```

Read the output CSV from `learn_to_write/data/<handle>/posts.csv` and check how many posts were collected.

## Step 2: Supplement with web search

If the scraper got fewer than the target (X limits anonymous browsing to ~30-60 posts), supplement with web search:
- Search: `site:x.com/<handle>/status`, `"<display name>" site:x.com`
- Extract tweet text from search result titles (format: `Name on X: "tweet text" / X`)
- Deduplicate against existing posts (match on first 80 characters)
- Append new posts to the CSV (engagement data will be blank for search-sourced posts)

## Step 3: Analyze & Generate Skill

Read the full CSV from `learn_to_write/data/<handle>/posts.csv`.

Analyze the writing style across all dimensions:

**Length patterns:** Average post length, distribution of short vs long posts.

**Sentence structure:** Sentences per post, line breaks, lists, questions, threads.

**Vocabulary:** Most-used content words, vocabulary diversity, word complexity.

**Tone:** Exclamation marks, question marks, ALL CAPS, emoji, hashtags, slang.

**Formatting:** Lowercase starts, skipped punctuation, parentheticals, em dashes.

**Engagement:** What high-performing posts have in common vs low performers.

Then generate a Claude Skill with these 9 sections:

### 1. VOICE IDENTITY (2-3 sentences)
A vivid description of the writer's overall voice.

### 2. SENTENCE MECHANICS
Typical sentence length/rhythm, how they start sentences, punctuation, capitalization, line breaks.

### 3. WORD CHOICE & VOCABULARY
Register, signature phrases, jargon level, slang and abbreviations.

### 4. STRUCTURAL PATTERNS
How they open, build, and close posts. Lists, threads, one-liners. Typical post length.

### 5. RHETORICAL DEVICES
Questions, analogies, emphasis techniques, humor style, how they handle strong opinions.

### 6. ENGAGEMENT PATTERNS
What gets traction and why, hooks, calls to action.

### 7. DISTINCTIVE QUIRKS
Unique habits, recurring themes, things they NEVER do.

### 8. THE REWRITE RULES
5-7 concrete rules: "When you see X, change it to Y" or "Always/Never do Z"

### 9. EXAMPLE TRANSFORMATIONS
Take 3 generic statements and show how this person would write them.

Be EXTREMELY specific. Use actual quotes from their posts as evidence.

Save the skill to `learn_to_write/data/<handle>/skill.md`.

## Step 4: Report

Show: total posts collected, key style findings, 2-3 of their best posts as examples, and where both files were saved.
