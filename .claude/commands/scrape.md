---
description: Scrape posts from an X account and generate a Claude Skill
argument-hint: <@handle> [max_posts]
allowed-tools: [Bash, Read, Write, Glob, Grep, WebSearch]
---

Scrape posts from the X account and generate a Claude Skill: $ARGUMENTS

Steps:
1. Parse the handle from the arguments. Strip any @ prefix or https://x.com/ URL prefix.
2. Default to 200 posts if no count is specified. If the user included a number, use that.
3. Run the Playwright scraper:
   ```
   python3 -m src.scraper <handle> <max_posts>
   ```
4. Read the output CSV from `data/<handle>/posts.csv` and check how many posts we got.
5. **If the scraper got fewer than the target** (X limits anonymous browsing to ~30-60 posts), supplement with web search:
   - Run multiple web searches: `site:x.com/<handle>/status`, `"<display name>" site:x.com <topic>`, etc.
   - Extract tweet text from the search result titles (format: `Name on X: "tweet text" / X`)
   - Deduplicate against existing posts (match on first 80 characters)
   - Append new posts to the CSV (engagement data will be blank for search-sourced posts)
6. Read the full CSV from `data/<handle>/posts.csv`.
7. **Generate the Claude Skill.** Analyze the writing style across all dimensions:

   **Length patterns:**
   - Average post length (chars and words)
   - Distribution: what % are short (<100 chars) vs long (>200 chars)?

   **Sentence structure:**
   - Average sentences per post
   - How often do they use line breaks?
   - Do they use bullet lists, numbered lists?
   - Do they open with questions?
   - Do they write threads?

   **Vocabulary:**
   - What are their most-used content words (filter out stop words)?
   - Vocabulary diversity (unique words / total words)
   - Average word length — do they use simple or complex words?

   **Tone:**
   - Exclamation marks, question marks, ellipsis frequency
   - ALL CAPS words frequency
   - Emoji usage
   - Hashtag and @mention density
   - Informal language (slang like "tbh", "ngl", "gonna", etc.)

   **Formatting:**
   - Do they start posts lowercase?
   - Do they skip ending punctuation?
   - Parenthetical asides, em dashes, quotation marks?

   **Engagement:**
   - Which posts got the most likes/retweets? What do they have in common?
   - Which posts got low engagement? What's different?

   Then generate a comprehensive Claude Skill with these 9 sections:

   ### 1. VOICE IDENTITY (2-3 sentences)
   A vivid description of the writer's overall voice.

   ### 2. SENTENCE MECHANICS
   - Typical sentence length and rhythm
   - How they start sentences
   - Punctuation habits
   - Capitalization patterns
   - Line break usage

   ### 3. WORD CHOICE & VOCABULARY
   - Register (formal, casual, technical, conversational, etc.)
   - Signature words or phrases they repeat
   - Jargon level
   - Slang and abbreviations

   ### 4. STRUCTURAL PATTERNS
   - How they open posts
   - How they build to their point
   - How they close posts
   - Lists, threads, one-liners
   - Typical post length

   ### 5. RHETORICAL DEVICES
   - Questions, analogies, metaphors
   - Emphasis techniques (caps, repetition)
   - Humor style
   - How they handle strong opinions

   ### 6. ENGAGEMENT PATTERNS
   - What types of posts get the most engagement and why
   - How they create hooks
   - Calls to action

   ### 7. DISTINCTIVE QUIRKS
   - Unique habits
   - Recurring themes
   - Things they NEVER do

   ### 8. THE REWRITE RULES
   5-7 concrete rules: "When you see X, change it to Y" or "Always/Never do Z"

   ### 9. EXAMPLE TRANSFORMATIONS
   Take 3 generic statements and show how this person would write them.

8. Be EXTREMELY specific. Use actual quotes from their posts as evidence.
9. Save the skill to `data/<handle>/skill.md`.
10. Report: total posts collected, key style findings, and where both files were saved.
