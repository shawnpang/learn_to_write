"""
Analyze scraped posts to extract writing style patterns.
Produces a structured style profile used to generate the Claude Scale.
"""

import re
import json
from pathlib import Path
from collections import Counter


def load_posts(filepath: str | Path) -> list[dict]:
    """Load posts from a saved JSON file."""
    with open(filepath) as f:
        data = json.load(f)
    return data["posts"]


def analyze_style(posts: list[dict]) -> dict:
    """
    Analyze writing patterns from a list of posts.

    Returns a style profile dict covering:
    - Sentence structure
    - Vocabulary patterns
    - Tone markers
    - Formatting habits
    - Engagement correlation
    """
    texts = [p["text"] for p in posts if p.get("text")]

    profile = {
        "total_posts": len(texts),
        "length": _analyze_length(texts),
        "structure": _analyze_structure(texts),
        "vocabulary": _analyze_vocabulary(texts),
        "tone": _analyze_tone(texts),
        "formatting": _analyze_formatting(texts),
        "topics": _extract_topics(texts),
        "top_posts": _get_top_posts(posts),
        "sample_posts": _get_diverse_samples(texts),
    }
    return profile


def _analyze_length(texts: list[str]) -> dict:
    """Analyze post length distribution."""
    lengths = [len(t) for t in texts]
    word_counts = [len(t.split()) for t in texts]
    return {
        "avg_chars": round(sum(lengths) / len(lengths)) if lengths else 0,
        "avg_words": round(sum(word_counts) / len(word_counts)) if word_counts else 0,
        "min_chars": min(lengths) if lengths else 0,
        "max_chars": max(lengths) if lengths else 0,
        "short_posts_pct": round(sum(1 for l in lengths if l < 100) / len(lengths) * 100) if lengths else 0,
        "long_posts_pct": round(sum(1 for l in lengths if l > 200) / len(lengths) * 100) if lengths else 0,
    }


def _analyze_structure(texts: list[str]) -> dict:
    """Analyze sentence and paragraph structure patterns."""
    sentence_counts = []
    uses_line_breaks = 0
    uses_lists = 0
    starts_with_question = 0
    uses_threads = 0

    for text in texts:
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_counts.append(len(sentences))

        if "\n" in text:
            uses_line_breaks += 1
        if re.search(r'^\s*[-•\d]+[.)]?\s', text, re.MULTILINE):
            uses_lists += 1
        if text.strip().startswith(("How", "What", "Why", "When", "Where", "Who", "Is", "Are", "Do", "Does", "Can")):
            starts_with_question += 1
        if "🧵" in text or "thread" in text.lower() or "1/" in text:
            uses_threads += 1

    n = len(texts) or 1
    return {
        "avg_sentences_per_post": round(sum(sentence_counts) / len(sentence_counts), 1) if sentence_counts else 0,
        "line_breaks_pct": round(uses_line_breaks / n * 100),
        "lists_pct": round(uses_lists / n * 100),
        "question_opener_pct": round(starts_with_question / n * 100),
        "thread_pct": round(uses_threads / n * 100),
    }


def _analyze_vocabulary(texts: list[str]) -> dict:
    """Analyze word choice and vocabulary patterns."""
    all_words = []
    for text in texts:
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        all_words.extend(words)

    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "during",
        "before", "after", "above", "below", "between", "and", "but", "or",
        "not", "no", "nor", "so", "yet", "both", "either", "neither", "each",
        "every", "all", "any", "few", "more", "most", "other", "some", "such",
        "than", "too", "very", "just", "about", "up", "out", "if", "then",
        "that", "this", "these", "those", "it", "its", "i", "me", "my", "we",
        "our", "you", "your", "he", "him", "his", "she", "her", "they", "them",
        "their", "what", "which", "who", "whom", "when", "where", "why", "how",
    }

    content_words = [w for w in all_words if w not in stop_words and len(w) > 2]
    word_freq = Counter(content_words)

    # Unique word ratio
    unique_ratio = len(set(all_words)) / len(all_words) if all_words else 0

    return {
        "unique_word_ratio": round(unique_ratio, 3),
        "top_words": word_freq.most_common(30),
        "avg_word_length": round(sum(len(w) for w in all_words) / len(all_words), 1) if all_words else 0,
    }


def _analyze_tone(texts: list[str]) -> dict:
    """Analyze emotional tone and voice markers."""
    markers = {
        "exclamation_marks": sum(t.count("!") for t in texts),
        "question_marks": sum(t.count("?") for t in texts),
        "ellipsis": sum(t.count("...") or t.count("…") for t in texts),
        "all_caps_words": sum(len(re.findall(r'\b[A-Z]{2,}\b', t)) for t in texts),
        "emoji_count": sum(len(re.findall(r'[\U0001f600-\U0001f9ff\U0001fa00-\U0001fa6f\U0001fa70-\U0001faff\u2600-\u26ff\u2700-\u27bf]', t)) for t in texts),
        "hashtag_count": sum(len(re.findall(r'#\w+', t)) for t in texts),
        "mention_count": sum(len(re.findall(r'@\w+', t)) for t in texts),
        "url_count": sum(len(re.findall(r'https?://\S+', t)) for t in texts),
    }

    n = len(texts) or 1
    # Normalize per post
    per_post = {f"{k}_per_post": round(v / n, 2) for k, v in markers.items()}

    # Detect conversational style signals
    informal_markers = sum(
        1 for t in texts
        if re.search(r'\b(lol|lmao|haha|tbh|imo|ngl|fr|bruh|lowkey|highkey|nah|ya|yall|gonna|wanna|gotta)\b', t.lower())
    )

    per_post["informal_pct"] = round(informal_markers / n * 100)

    return per_post


def _analyze_formatting(texts: list[str]) -> dict:
    """Analyze formatting and punctuation habits."""
    starts_lowercase = sum(1 for t in texts if t and t[0].islower())
    no_period_ending = sum(1 for t in texts if t and t.rstrip()[-1:] not in ".!?")
    uses_parentheses = sum(1 for t in texts if "(" in t and ")" in t)
    uses_dashes = sum(1 for t in texts if " - " in t or " — " in t or " – " in t)
    uses_quotes = sum(1 for t in texts if '"' in t or '"' in t or '"' in t)

    n = len(texts) or 1
    return {
        "starts_lowercase_pct": round(starts_lowercase / n * 100),
        "no_period_ending_pct": round(no_period_ending / n * 100),
        "uses_parentheses_pct": round(uses_parentheses / n * 100),
        "uses_dashes_pct": round(uses_dashes / n * 100),
        "uses_quotes_pct": round(uses_quotes / n * 100),
    }


def _extract_topics(texts: list[str]) -> list[str]:
    """Extract frequently discussed topics via hashtags and key phrases."""
    hashtags = []
    for t in texts:
        hashtags.extend(re.findall(r'#(\w+)', t))
    top_hashtags = [tag for tag, _ in Counter(hashtags).most_common(15)]
    return top_hashtags


def _get_top_posts(posts: list[dict], n: int = 10) -> list[dict]:
    """Get the most-engaged posts as exemplars."""
    def _parse_engagement(val: str) -> int:
        if not val:
            return 0
        val = val.strip().replace(",", "")
        if val.endswith("K"):
            return int(float(val[:-1]) * 1000)
        if val.endswith("M"):
            return int(float(val[:-1]) * 1_000_000)
        try:
            return int(val)
        except ValueError:
            return 0

    scored = []
    for p in posts:
        likes = _parse_engagement(p.get("likes", "0"))
        retweets = _parse_engagement(p.get("retweets", "0"))
        score = likes + retweets * 2
        scored.append({**p, "_score": score})

    scored.sort(key=lambda x: x["_score"], reverse=True)
    return [{"text": p["text"], "likes": p["likes"], "retweets": p["retweets"]} for p in scored[:n]]


def _get_diverse_samples(texts: list[str], n: int = 20) -> list[str]:
    """Get a diverse sample of posts across different lengths and styles."""
    if len(texts) <= n:
        return texts

    # Sort by length, pick evenly spaced samples
    sorted_texts = sorted(texts, key=len)
    step = len(sorted_texts) / n
    return [sorted_texts[int(i * step)] for i in range(n)]


def save_profile(handle: str, profile: dict) -> Path:
    """Save the style profile to a JSON file."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    filepath = data_dir / f"{handle}_profile.json"
    with open(filepath, "w") as f:
        json.dump(profile, f, indent=2)
    print(f"Style profile saved to {filepath}")
    return filepath
