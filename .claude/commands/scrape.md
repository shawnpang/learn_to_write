---
description: Scrape posts from an X account
argument-hint: <@handle> [max_posts]
allowed-tools: [Bash, Read, Glob, WebSearch]
---

Scrape posts from the X account: $ARGUMENTS

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
6. Report: total posts collected, how many from scraper vs search, and show 3-5 examples.
