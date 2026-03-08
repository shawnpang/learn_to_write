---
description: Rewrite content using a Claude Scale
argument-hint: <@handle> <content to rewrite>
allowed-tools: [Read, Write, Glob]
---

Apply a Claude Scale to rewrite content: $ARGUMENTS

Steps:
1. Parse the handle and the content from the arguments. The first word starting with @ is the handle, everything after is the content.
2. Find the scale file at `scales/<handle>_scale.md`. Read it.
3. Using the style guide in the scale, rewrite the provided content to match this person's exact voice, structure, and tone. Preserve the core meaning but transform everything else.
4. Show the original and rewritten versions side by side.
5. Briefly explain what you changed and why (2-3 sentences).
