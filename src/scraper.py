"""
Scrape posts from any public X (Twitter) account using Playwright.
Uses stealth patches, persistent browser profiles, and human behavior
simulation to avoid bot detection. Never logs in — never touches your account.

X limits anonymous browsing to ~30-60 posts per session. Running the scraper
again merges new posts with existing data automatically.
"""

from __future__ import annotations

import csv
import random
import sys
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright

from src.stealth import (
    apply_stealth_scripts,
    get_random_persona,
    human_scroll,
    human_pause,
    simulate_reading,
    warm_up_session,
    _dismiss_overlays,
)


DATA_DIR = Path(__file__).parent.parent / "data"
PROFILES_DIR = Path(__file__).parent.parent / "browser_profiles"


def _extract_posts(page) -> list[dict]:
    """Extract post data from the currently loaded timeline."""
    posts = page.evaluate("""
        () => {
            const articles = document.querySelectorAll('article[data-testid="tweet"]');
            return Array.from(articles).map(article => {
                const textEl = article.querySelector('[data-testid="tweetText"]');
                const timeEl = article.querySelector('time');
                const likesEl = article.querySelector('[data-testid="like"] span');
                const retweetsEl = article.querySelector('[data-testid="retweet"] span');
                const repliesEl = article.querySelector('[data-testid="reply"] span');

                // Check if it's a repost (retweet)
                const socialContext = article.querySelector('[data-testid="socialContext"]');
                const isRepost = socialContext
                    ? socialContext.textContent.includes('reposted')
                    : false;

                return {
                    text: textEl ? textEl.innerText : '',
                    timestamp: timeEl ? timeEl.getAttribute('datetime') : null,
                    likes: likesEl ? likesEl.textContent : '0',
                    retweets: retweetsEl ? retweetsEl.textContent : '0',
                    replies: repliesEl ? repliesEl.textContent : '0',
                    is_repost: isRepost,
                };
            }).filter(p => p.text && !p.is_repost);
        }
    """)
    return posts


def scrape_account(
    handle: str,
    max_posts: int = 200,
    headless: bool = True,
    scroll_pause: float = 2.0,
) -> list[dict]:
    """
    Scrape posts from an X account with stealth.

    Uses a persistent browser profile so cookies accumulate across runs,
    making the browser look like a returning visitor. Merges with any
    existing scraped data for this handle.

    Args:
        handle: X username (without @)
        max_posts: Maximum number of posts to collect
        headless: Run browser in headless mode
        scroll_pause: Base seconds between scrolls

    Returns:
        List of post dicts with text, timestamp, engagement metrics
    """
    handle = handle.lstrip("@")

    # Load existing posts from previous runs
    all_posts, seen_texts = _load_existing_posts(handle)
    if all_posts:
        print(f"Loaded {len(all_posts)} posts from previous runs.")
        if len(all_posts) >= max_posts:
            print(f"Already have {len(all_posts)} posts (target: {max_posts}). Done.")
            return all_posts[:max_posts]

    persona = get_random_persona()
    profile_dir = PROFILES_DIR / "default"
    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=headless,
            viewport=persona["viewport"],
            user_agent=persona["user_agent"],
            device_scale_factor=persona["device_scale_factor"],
            locale=persona["locale"],
            timezone_id=persona["timezone_id"],
            color_scheme=persona["color_scheme"],
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        )

        apply_stealth_scripts(context)
        page = context.pages[0] if context.pages else context.new_page()

        # Warm up — build cookies and referrer chain
        warm_up_session(page)

        # Navigate to profile
        print(f"Navigating to @{handle}...")
        page.goto(f"https://x.com/{handle}", wait_until="domcontentloaded", timeout=30000)

        # Wait for timeline to actually render
        try:
            page.wait_for_selector('article[data-testid="tweet"]', timeout=15000)
        except Exception:
            pass
        human_pause(3.0, 5.0)

        _dismiss_overlays(page)
        simulate_reading(page, post_count=0)

        print(f"Scrolling and collecting posts (target: {max_posts})...")
        stall_count = 0
        max_stalls = 8
        scroll_count = 0

        while len(all_posts) < max_posts:
            posts = _extract_posts(page)
            new_count = 0

            for post in posts:
                text_key = post["text"][:100]
                if text_key not in seen_texts:
                    seen_texts.add(text_key)
                    all_posts.append(post)
                    new_count += 1

            if new_count == 0:
                stall_count += 1
                if stall_count >= 2:
                    _dismiss_overlays(page)
                    human_pause(1.0, 2.0)
                if stall_count >= max_stalls:
                    print(f"  No new posts after {max_stalls} scrolls. Stopping.")
                    break
            else:
                stall_count = 0

            print(f"  Collected {len(all_posts)}/{max_posts} posts...")
            scroll_count += 1

            # Dismiss overlays periodically
            if scroll_count % 3 == 0:
                _dismiss_overlays(page)

            simulate_reading(page, post_count=len(all_posts))

            intensity = random.choice(["normal", "normal", "normal", "large", "small"])
            human_scroll(page, direction="down", intensity=intensity)
            human_pause(scroll_pause, scroll_pause + 2.0)

            # Occasional scroll back up
            if random.random() < 0.1:
                human_scroll(page, direction="up", intensity="small")
                human_pause(0.5, 1.5)

            # Periodic longer breaks
            if scroll_count % random.randint(20, 30) == 0:
                pause_time = random.uniform(5.0, 15.0)
                print(f"  Taking a {pause_time:.0f}s break...")
                human_pause(pause_time, pause_time + 2.0)

        context.close()

    print(f"Done. Total: {len(all_posts)} unique posts from @{handle}.")
    return all_posts[:max_posts]


def _load_existing_posts(handle: str) -> tuple[list[dict], set]:
    """Load posts from an existing CSV for this handle."""
    DATA_DIR.mkdir(exist_ok=True)
    csv_file = DATA_DIR / f"{handle}.csv"
    posts = []
    seen = set()

    if csv_file.exists():
        try:
            with open(csv_file, encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = row["text"][:100]
                    if key not in seen:
                        seen.add(key)
                        posts.append(row)
        except Exception:
            pass

    return posts, seen


def save_csv(handle: str, posts: list[dict]) -> Path:
    """Save scraped posts to a single CSV file (overwrites previous)."""
    DATA_DIR.mkdir(exist_ok=True)
    filepath = DATA_DIR / f"{handle}.csv"

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "timestamp", "likes", "retweets", "replies"])
        writer.writeheader()
        for post in posts:
            writer.writerow({
                "text": post["text"],
                "timestamp": post.get("timestamp", ""),
                "likes": post.get("likes", "0"),
                "retweets": post.get("retweets", "0"),
                "replies": post.get("replies", "0"),
            })

    print(f"Saved {len(posts)} posts to {filepath}")
    return filepath


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: python3 -m src.scraper <handle> [max_posts] [--visible]")
        print("  handle:    X username (without @)")
        print("  max_posts: number of posts to scrape (default: 200)")
        print("  --visible: show browser window")
        print()
        print("Run multiple times to accumulate more posts — data merges automatically.")
        sys.exit(1)

    handle = args[0].lstrip("@")
    max_posts = 200
    headless = True

    for arg in args[1:]:
        if arg == "--visible":
            headless = False
        elif arg.isdigit():
            max_posts = int(arg)

    posts = scrape_account(handle, max_posts=max_posts, headless=headless)
    save_csv(handle, posts)
