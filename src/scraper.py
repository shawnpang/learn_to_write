"""
Scrape posts from any public X (Twitter) account using Playwright.
Uses a fresh browser context each run to avoid account association.
"""

import json
import time
import random
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, Browser, BrowserContext


DATA_DIR = Path(__file__).parent.parent / "data"
BROWSER_DATA_DIR = Path(__file__).parent.parent / "browser_data"


def _random_delay(min_s: float = 1.0, max_s: float = 3.0):
    """Human-like random delay between actions."""
    time.sleep(random.uniform(min_s, max_s))


def _create_fresh_context(browser: Browser) -> BrowserContext:
    """Create a completely fresh browser context with realistic fingerprint."""
    context = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        locale="en-US",
        timezone_id="America/New_York",
        color_scheme="light",
    )
    # Block unnecessary resources to speed up loading
    context.route(
        "**/*.{png,jpg,jpeg,gif,svg,mp4,webm,woff2,woff}",
        lambda route: route.abort(),
    )
    return context


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
    Scrape posts from an X account.

    Args:
        handle: X username (without @)
        max_posts: Maximum number of posts to collect
        headless: Run browser in headless mode
        scroll_pause: Seconds to wait between scrolls

    Returns:
        List of post dicts with text, timestamp, engagement metrics
    """
    handle = handle.lstrip("@")
    all_posts = []
    seen_texts = set()

    with sync_playwright() as p:
        # Launch fresh browser - no persistent storage
        browser = p.chromium.launch(headless=headless)
        context = _create_fresh_context(browser)
        page = context.new_page()

        print(f"Navigating to @{handle}...")
        page.goto(f"https://x.com/{handle}", wait_until="networkidle", timeout=30000)
        _random_delay(2.0, 4.0)

        # Dismiss any login prompts or cookie banners
        try:
            close_btn = page.locator('[data-testid="xMigrationBottomBar"] button')
            if close_btn.is_visible(timeout=3000):
                close_btn.click()
        except Exception:
            pass

        try:
            # Also try dismissing the "Sign in" overlay
            page.keyboard.press("Escape")
            _random_delay(0.5, 1.0)
        except Exception:
            pass

        print(f"Scrolling and collecting posts (target: {max_posts})...")
        stall_count = 0
        max_stalls = 5

        while len(all_posts) < max_posts:
            posts = _extract_posts(page)
            new_count = 0

            for post in posts:
                text_key = post["text"][:100]  # dedupe by first 100 chars
                if text_key not in seen_texts:
                    seen_texts.add(text_key)
                    all_posts.append(post)
                    new_count += 1

            if new_count == 0:
                stall_count += 1
                if stall_count >= max_stalls:
                    print(f"No new posts after {max_stalls} scrolls. Stopping.")
                    break
            else:
                stall_count = 0

            print(f"  Collected {len(all_posts)}/{max_posts} posts...")

            # Scroll down
            page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
            _random_delay(scroll_pause, scroll_pause + 1.5)

        context.close()
        browser.close()

    print(f"Done. Scraped {len(all_posts)} posts from @{handle}.")
    return all_posts[:max_posts]


def save_posts(handle: str, posts: list[dict]) -> Path:
    """Save scraped posts to a JSON file."""
    DATA_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = DATA_DIR / f"{handle}_{timestamp}.json"
    with open(filepath, "w") as f:
        json.dump(
            {"handle": handle, "scraped_at": timestamp, "count": len(posts), "posts": posts},
            f,
            indent=2,
        )
    print(f"Saved to {filepath}")
    return filepath
