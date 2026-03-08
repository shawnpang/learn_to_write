"""
Generate a "Claude Scale" — a portable writing style prompt that captures
how a person writes, so Claude can replicate or teach that style.
"""

import json
from pathlib import Path

import anthropic


SCALES_DIR = Path(__file__).parent.parent / "scales"

GENERATION_PROMPT = """You are a world-class writing style analyst. I'm going to give you a detailed statistical profile of someone's writing on X (Twitter), along with their top-performing posts and a diverse sample of their posts.

Your job: produce a **Claude Scale** — a comprehensive, actionable writing style guide that captures exactly how this person writes. This scale will be used as a system prompt so that Claude can either:
1. Write new content that sounds exactly like this person
2. Rewrite any given content to match this person's voice and style

The Claude Scale must be specific and concrete, not generic. It should capture the *essence* of what makes this person's writing distinctive.

## Structure the Claude Scale as follows:

### 1. VOICE IDENTITY (2-3 sentences)
A vivid, precise description of the writer's overall voice. What would you say if describing their writing to someone who's never read them?

### 2. SENTENCE MECHANICS
- Typical sentence length and rhythm
- How they start sentences (do they vary? use fragments? lead with verbs?)
- Punctuation habits (oxford commas, em dashes, ellipsis, exclamation marks, etc.)
- Capitalization patterns
- Paragraph/line break usage

### 3. WORD CHOICE & VOCABULARY
- Register (formal, casual, technical, conversational, etc.)
- Signature words or phrases they use repeatedly
- Jargon level and type
- Do they use slang, abbreviations, or internet-speak?

### 4. STRUCTURAL PATTERNS
- How do they typically open a post?
- How do they build to their point?
- How do they close/end posts?
- Do they use lists, threads, one-liners?
- Typical post length

### 5. RHETORICAL DEVICES
- Do they use questions, analogies, metaphors, callbacks?
- How do they use emphasis (caps, italics, repetition)?
- Humor style (if any)
- How do they handle controversial or strong opinions?

### 6. ENGAGEMENT PATTERNS
- What types of posts get the most engagement and why?
- How do they create hooks?
- Do they use CTAs (calls to action)?

### 7. DISTINCTIVE QUIRKS
- Any unique formatting, punctuation, or structural habits
- Recurring themes or framings
- Things they NEVER do (equally important)

### 8. THE REWRITE RULES
Provide 5-7 concrete, actionable rewrite rules in the format:
"When you see X, change it to Y" or "Always/Never do Z"
These should be the most impactful rules for matching this person's style.

### 9. EXAMPLE TRANSFORMATIONS
Take 3 generic statements and show how this person would write them, with brief explanations of what changed and why.

---

Here is the style profile data:

**Account:** @{handle}

**Stats:**
{stats}

**Top Performing Posts (by engagement):**
{top_posts}

**Diverse Sample Posts:**
{samples}

Now generate the Claude Scale. Be extremely specific. Use actual examples from their posts. The goal is that someone reading this scale could immediately start writing convincingly in this person's voice."""


def generate_scale(handle: str, profile: dict, model: str = "claude-sonnet-4-20250514") -> str:
    """
    Generate a Claude Scale from a style profile using the Anthropic API.

    Args:
        handle: X username
        profile: Style profile dict from analyzer
        model: Claude model to use

    Returns:
        The generated Claude Scale as a markdown string
    """
    client = anthropic.Anthropic()

    # Format the data for the prompt
    stats_str = json.dumps(
        {k: v for k, v in profile.items() if k not in ("top_posts", "sample_posts", "topics")},
        indent=2,
    )

    top_posts_str = "\n\n".join(
        f"[Likes: {p['likes']}, Retweets: {p['retweets']}]\n{p['text']}"
        for p in profile.get("top_posts", [])
    )

    samples_str = "\n\n---\n\n".join(profile.get("sample_posts", []))

    prompt = GENERATION_PROMPT.format(
        handle=handle,
        stats=stats_str,
        top_posts=top_posts_str,
        samples=samples_str,
    )

    print(f"Generating Claude Scale for @{handle}...")
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    scale_text = response.content[0].text
    return scale_text


def save_scale(handle: str, scale_text: str) -> Path:
    """Save the Claude Scale to a markdown file."""
    SCALES_DIR.mkdir(exist_ok=True)
    filepath = SCALES_DIR / f"{handle}_scale.md"
    with open(filepath, "w") as f:
        f.write(f"# Claude Scale: @{handle}\n\n")
        f.write(scale_text)
    print(f"Claude Scale saved to {filepath}")
    return filepath


def apply_scale(scale_path: str | Path, content: str, model: str = "claude-sonnet-4-20250514") -> str:
    """
    Apply a Claude Scale to rewrite content in the target style.

    Args:
        scale_path: Path to the Claude Scale markdown file
        content: The content to rewrite
        model: Claude model to use

    Returns:
        Rewritten content
    """
    client = anthropic.Anthropic()

    with open(scale_path) as f:
        scale = f.read()

    response = client.messages.create(
        model=model,
        max_tokens=2048,
        system=scale,
        messages=[
            {
                "role": "user",
                "content": f"Rewrite the following content in the exact style described in your system prompt. Preserve the core meaning but transform the voice, structure, and tone to match.\n\nContent to rewrite:\n{content}",
            }
        ],
    )

    return response.content[0].text
