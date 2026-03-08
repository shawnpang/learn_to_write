---
description: Full pipeline — scrape an X account, analyze style, generate Claude Skill
argument-hint: <@handle> [max_posts]
allowed-tools: [Bash, Read, Write, Glob, Grep, WebSearch]
---

Run the full learn-to-write pipeline for: $ARGUMENTS

This is the all-in-one command. Steps:

1. **Scrape**: Parse the handle and optional post count (default 30). Run:
   ```
   python3 -m src.scraper <handle> <max_posts>
   ```
   Wait for it to finish.

2. **Supplement with web search**: If the scraper got fewer posts than the target (X limits anonymous browsing), run multiple web searches to find more tweets:
   - `site:x.com/<handle>/status`
   - `"<handle>" site:x.com <relevant topics>`
   - Extract tweet text from search result titles, deduplicate, and append to the CSV

3. **Read**: Read the full CSV from `data/<handle>/posts.csv`.

4. **Analyze & Generate Skill**: Analyze the writing style across all dimensions (length, structure, vocabulary, tone, formatting, engagement patterns). Then generate a comprehensive Claude Skill with all 9 sections (Voice Identity, Sentence Mechanics, Word Choice, Structural Patterns, Rhetorical Devices, Engagement Patterns, Distinctive Quirks, Rewrite Rules, Example Transformations). Be extremely specific — use actual quotes from posts as evidence. Save to `data/<handle>/skill.md`.

5. **Report**: Show a summary of what was found — key style characteristics, the most distinctive patterns, and where the skill was saved. Also show 2-3 of their best posts as examples.
