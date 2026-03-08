---
description: Analyze scraped posts and generate a Claude Scale
argument-hint: <@handle>
allowed-tools: [Read, Write, Glob, Grep, Bash]
---

Generate a Claude Scale for: $ARGUMENTS

Steps:
1. Find the most recent CSV for this handle in `data/`. If there are multiple, use the latest one.
2. Read the entire CSV file.
3. Analyze the writing style deeply. Look at ALL of the following:

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

4. Now generate the Claude Scale. This is a comprehensive, actionable writing style guide with these sections:

   ### 1. VOICE IDENTITY (2-3 sentences)
   A vivid description of the writer's overall voice.

   ### 2. SENTENCE MECHANICS
   - Typical sentence length and rhythm
   - How they start sentences
   - Punctuation habits
   - Capitalization patterns
   - Line break usage

   ### 3. WORD CHOICE & VOCABULARY
   - Register (formal, casual, technical, etc.)
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

5. Be EXTREMELY specific. Use actual quotes from their posts as evidence. The goal is that someone reading this scale could immediately write in this person's voice.

6. Save the scale to `scales/<handle>_scale.md`.

7. Report what you found and where the scale was saved.
