"""
Browser stealth patches and human behavior simulation.
Makes Playwright look like a real person browsing in a real Chrome.
"""

import math
import random
import time

# ---------------------------------------------------------------------------
# Stealth JS — injected before any page script runs
# ---------------------------------------------------------------------------

STEALTH_JS = """
// 1. Hide navigator.webdriver
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

// 2. Add window.chrome object (real Chrome always has this)
window.chrome = {
    runtime: {
        onMessage: { addListener: function() {}, removeListener: function() {} },
        sendMessage: function() {},
        connect: function() { return { onMessage: { addListener: function() {} } }; }
    },
    csi: function() { return {}; },
    loadTimes: function() { return {}; }
};

// 3. Override navigator.plugins to show realistic plugins
Object.defineProperty(navigator, 'plugins', {
    get: () => {
        const plugins = [
            { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer', description: 'Portable Document Format' },
            { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai', description: '' },
            { name: 'Native Client', filename: 'internal-nacl-plugin', description: '' }
        ];
        plugins.length = 3;
        return plugins;
    }
});

// 4. Override navigator.languages
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });

// 5. Fix permissions.query for notifications
const originalQuery = window.navigator.permissions.query;
window.navigator.permissions.query = (parameters) => {
    if (parameters.name === 'notifications') {
        return Promise.resolve({ state: Notification.permission });
    }
    return originalQuery(parameters);
};

// 6. Override WebGL vendor/renderer to look like real hardware
const getParameter = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {
    if (parameter === 37445) return 'Google Inc. (Apple)';
    if (parameter === 37446) return 'ANGLE (Apple, Apple M1 Pro, OpenGL 4.1)';
    return getParameter.call(this, parameter);
};

// 7. Fix iframe contentWindow access pattern
const originalContentWindow = Object.getOwnPropertyDescriptor(HTMLIFrameElement.prototype, 'contentWindow');
Object.defineProperty(HTMLIFrameElement.prototype, 'contentWindow', {
    get: function() {
        const win = originalContentWindow.get.call(this);
        if (win) {
            // Make sure the iframe's navigator also looks clean
            try {
                Object.defineProperty(win.navigator, 'webdriver', { get: () => undefined });
            } catch(e) {}
        }
        return win;
    }
});

// 8. Prevent detection via toString checks on overridden functions
const nativeToString = Function.prototype.toString;
const customFunctions = new Map();
Function.prototype.toString = function() {
    if (customFunctions.has(this)) return customFunctions.get(this);
    return nativeToString.call(this);
};

// 9. Add realistic connection info
Object.defineProperty(navigator, 'connection', {
    get: () => ({
        effectiveType: '4g',
        rtt: 50,
        downlink: 10,
        saveData: false
    })
});

// 10. Add realistic media devices
if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
    const originalEnumerate = navigator.mediaDevices.enumerateDevices;
    navigator.mediaDevices.enumerateDevices = async function() {
        const devices = await originalEnumerate.call(this);
        if (devices.length === 0) {
            return [
                { deviceId: 'default', kind: 'audioinput', label: '', groupId: 'default' },
                { deviceId: 'default', kind: 'videoinput', label: '', groupId: 'default' },
                { deviceId: 'default', kind: 'audiooutput', label: '', groupId: 'default' }
            ];
        }
        return devices;
    };
}
"""

# ---------------------------------------------------------------------------
# User agent pool — recent, real Chrome versions on macOS
# ---------------------------------------------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
]

# Common viewport sizes (width, height) — weighted toward popular resolutions
VIEWPORTS = [
    (1920, 1080),
    (1536, 864),
    (1440, 900),
    (1366, 768),
    (2560, 1440),
    (1680, 1050),
]

# Common timezones
TIMEZONES = [
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Toronto",
    "Europe/London",
]


def get_random_persona() -> dict:
    """Generate a randomized but internally consistent browser persona."""
    ua = random.choice(USER_AGENTS)
    vp = random.choice(VIEWPORTS)
    # Add slight jitter to viewport (+/- 0-20px) — real monitors vary
    w = vp[0] + random.randint(-10, 10)
    h = vp[1] + random.randint(-10, 10)
    tz = random.choice(TIMEZONES)
    # Device scale factor
    dpr = random.choice([1, 1, 2, 2, 2])  # Retina is more common now

    return {
        "user_agent": ua,
        "viewport": {"width": w, "height": h},
        "device_scale_factor": dpr,
        "timezone_id": tz,
        "locale": "en-US",
        "color_scheme": random.choice(["light", "light", "light", "dark"]),
    }


def apply_stealth_scripts(context):
    """Inject stealth JS into every page created in this context."""
    context.add_init_script(STEALTH_JS)


# ---------------------------------------------------------------------------
# Human mouse movement — bezier curves, not teleportation
# ---------------------------------------------------------------------------

def _bezier_point(t: float, p0: tuple, p1: tuple, p2: tuple, p3: tuple) -> tuple:
    """Calculate point on a cubic bezier curve at parameter t."""
    u = 1 - t
    return (
        u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0],
        u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1],
    )


def human_move_mouse(page, target_x: int, target_y: int, steps: int = 0):
    """
    Move mouse from current position to target along a natural-looking bezier curve.
    If steps=0, auto-calculates based on distance.
    """
    # Get current mouse position (default to a random starting point)
    try:
        current = page.evaluate("() => ({ x: window._mouseX || 400, y: window._mouseY || 300 })")
        start_x, start_y = current["x"], current["y"]
    except Exception:
        start_x, start_y = random.randint(200, 600), random.randint(200, 400)

    distance = math.sqrt((target_x - start_x) ** 2 + (target_y - start_y) ** 2)
    if steps == 0:
        steps = max(10, int(distance / 15))  # More steps for longer distances

    # Random control points for the bezier curve — adds natural wobble
    cp1 = (
        start_x + (target_x - start_x) * random.uniform(0.2, 0.5) + random.randint(-50, 50),
        start_y + (target_y - start_y) * random.uniform(0.0, 0.3) + random.randint(-50, 50),
    )
    cp2 = (
        start_x + (target_x - start_x) * random.uniform(0.5, 0.8) + random.randint(-30, 30),
        start_y + (target_y - start_y) * random.uniform(0.7, 1.0) + random.randint(-30, 30),
    )

    for i in range(steps + 1):
        t = i / steps
        # Ease-in-out timing — slow start and end, fast middle
        t = t * t * (3 - 2 * t)
        x, y = _bezier_point(t, (start_x, start_y), cp1, cp2, (target_x, target_y))
        page.mouse.move(x, y)
        # Variable delay — faster in the middle of the movement
        mid_factor = 1 - abs(2 * (i / steps) - 1)  # peaks at 0.5
        delay = random.uniform(0.002, 0.008) + mid_factor * 0.003
        time.sleep(delay)

    # Track position for next movement
    page.evaluate(f"() => {{ window._mouseX = {target_x}; window._mouseY = {target_y}; }}")


# ---------------------------------------------------------------------------
# Human scrolling — variable distance, occasional micro-corrections
# ---------------------------------------------------------------------------

def human_scroll(page, direction: str = "down", intensity: str = "normal"):
    """
    Scroll the page like a human — variable distance with momentum.

    intensity: "small" (reading), "normal" (browsing), "large" (skimming)
    """
    ranges = {
        "small": (100, 300),
        "normal": (400, 900),
        "large": (800, 1400),
    }
    min_dist, max_dist = ranges.get(intensity, ranges["normal"])
    distance = random.randint(min_dist, max_dist)
    if direction == "up":
        distance = -distance

    # Smooth scroll in chunks to simulate trackpad/wheel momentum
    chunks = random.randint(3, 7)
    for i in range(chunks):
        # Each chunk is a portion of total distance, with slight randomness
        chunk_dist = distance / chunks + random.randint(-20, 20)
        page.evaluate(f"window.scrollBy(0, {chunk_dist})")
        time.sleep(random.uniform(0.02, 0.08))

    # Occasionally do a small correction scroll (humans overshoot)
    if random.random() < 0.3:
        time.sleep(random.uniform(0.1, 0.3))
        correction = random.randint(20, 80) * (-1 if direction == "down" else 1)
        page.evaluate(f"window.scrollBy(0, {correction})")


# ---------------------------------------------------------------------------
# Human pausing — reading, thinking, distracted
# ---------------------------------------------------------------------------

def human_pause(min_s: float = 1.0, max_s: float = 3.0):
    """
    Pause with natural variance. Occasionally adds a longer 'distracted' pause
    to simulate checking phone, thinking, etc.
    """
    if random.random() < 0.08:
        # ~8% chance of a longer distraction (5-12 seconds)
        time.sleep(random.uniform(5.0, 12.0))
    else:
        time.sleep(random.uniform(min_s, max_s))


def simulate_reading(page, post_count: int = 0):
    """
    Simulate reading behavior — move mouse around the content area,
    pause at posts, occasionally hover over links.
    """
    viewport = page.viewport_size or {"width": 1920, "height": 1080}

    # Move mouse to content area (center-ish, where posts are)
    content_x = viewport["width"] // 2 + random.randint(-200, 200)
    content_y = random.randint(200, viewport["height"] - 200)
    human_move_mouse(page, content_x, content_y)

    # Pause as if reading (longer for first few posts, gets faster as we scroll)
    fatigue_factor = max(0.3, 1.0 - post_count * 0.005)
    time.sleep(random.uniform(1.0, 3.5) * fatigue_factor)

    # Sometimes hover over a specific element
    if random.random() < 0.15:
        try:
            tweets = page.locator('article[data-testid="tweet"]')
            count = tweets.count()
            if count > 0:
                idx = random.randint(0, min(count - 1, 4))
                box = tweets.nth(idx).bounding_box()
                if box:
                    hover_x = box["x"] + random.randint(20, int(box["width"] * 0.8))
                    hover_y = box["y"] + random.randint(5, int(box["height"] * 0.5))
                    human_move_mouse(page, int(hover_x), int(hover_y))
                    time.sleep(random.uniform(0.5, 1.5))
        except Exception:
            pass


def click_random_post(page):
    """
    Click into a random post to view it, pause as if reading, then go back.
    Builds natural browsing history and cookie state.
    """
    try:
        tweets = page.locator('article[data-testid="tweet"]')
        count = tweets.count()
        if count < 2:
            return

        idx = random.randint(0, min(count - 1, 5))
        tweet = tweets.nth(idx)

        # Find the timestamp link inside the tweet (links to the post)
        time_link = tweet.locator("time").locator("..")
        if not time_link.is_visible():
            return

        box = time_link.bounding_box()
        if not box:
            return

        # Move mouse to the link and click
        target_x = int(box["x"] + box["width"] / 2)
        target_y = int(box["y"] + box["height"] / 2)
        human_move_mouse(page, target_x, target_y)
        time.sleep(random.uniform(0.2, 0.5))
        page.mouse.click(target_x, target_y)

        # Wait for the post page to load
        time.sleep(random.uniform(2.0, 4.0))

        # "Read" the post
        human_scroll(page, direction="down", intensity="small")
        time.sleep(random.uniform(1.0, 3.0))

        # Go back
        page.go_back(wait_until="domcontentloaded", timeout=10000)
        time.sleep(random.uniform(1.0, 2.0))

    except Exception:
        # If anything goes wrong, try to go back
        try:
            page.go_back(wait_until="domcontentloaded", timeout=5000)
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Warm-up — build cookie state before hitting the target profile
# ---------------------------------------------------------------------------

def warm_up_session(page):
    """
    Visit X homepage and browse briefly before navigating to the target.
    Builds cookies, localStorage, and a natural referrer chain.
    """
    print("  Warming up browser session...")

    # Visit the X homepage first
    page.goto("https://x.com", wait_until="domcontentloaded", timeout=30000)
    time.sleep(random.uniform(2.0, 4.0))

    # Accept cookie consent if present
    _dismiss_overlays(page)

    # Move mouse around the homepage — look alive
    viewport = page.viewport_size or {"width": 1920, "height": 1080}
    for _ in range(random.randint(2, 4)):
        x = random.randint(100, viewport["width"] - 100)
        y = random.randint(100, viewport["height"] - 100)
        human_move_mouse(page, x, y)
        time.sleep(random.uniform(0.5, 1.5))

    # Scroll the homepage a bit
    human_scroll(page, direction="down", intensity="normal")
    time.sleep(random.uniform(1.5, 3.0))

    # Maybe click the Explore/search area
    if random.random() < 0.4:
        try:
            explore = page.locator('a[href="/explore"]')
            if explore.is_visible(timeout=2000):
                explore.click()
                time.sleep(random.uniform(2.0, 4.0))
                human_scroll(page, direction="down", intensity="small")
                time.sleep(random.uniform(1.0, 2.0))
                page.go_back(wait_until="domcontentloaded", timeout=10000)
                time.sleep(random.uniform(1.0, 2.0))
        except Exception:
            pass

    print("  Session warmed up.")


def _dismiss_overlays(page):
    """Dismiss login prompts, cookie banners, and other overlays X throws up."""
    # Cookie consent and bottom bars
    for selector in [
        '[data-testid="xMigrationBottomBar"] button',
        'button:has-text("Accept all cookies")',
        'button:has-text("Accept")',
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=1000):
                btn.click()
                time.sleep(random.uniform(0.3, 0.8))
        except Exception:
            pass

    # X's login/signup modal — the main wall that blocks scrolling.
    # Try multiple approaches to kill it.

    # Approach 1: Close button on the modal
    for selector in [
        '[data-testid="app-bar-close"]',
        'div[role="dialog"] [aria-label="Close"]',
        'div[role="dialog"] button[aria-label="Close"]',
        '[role="dialog"] div[role="button"]',
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=800):
                btn.click()
                time.sleep(random.uniform(0.3, 0.6))
                return
        except Exception:
            pass

    # Approach 2: Escape key
    try:
        page.keyboard.press("Escape")
        time.sleep(random.uniform(0.3, 0.6))
    except Exception:
        pass

    # Approach 3: Nuclear — remove the modal and scroll-blocking overlay via JS
    try:
        page.evaluate("""
            () => {
                // Remove login modals
                document.querySelectorAll('[role="dialog"]').forEach(el => el.remove());
                // Remove any overlay/backdrop
                document.querySelectorAll('[data-testid="sheetDialog"]').forEach(el => el.remove());
                document.querySelectorAll('[data-testid="mask"]').forEach(el => el.remove());
                document.querySelectorAll('[data-testid="bottomBar"]').forEach(el => el.remove());
                // Re-enable scrolling on body
                document.body.style.overflow = 'auto';
                document.body.style.position = 'static';
                document.documentElement.style.overflow = 'auto';
                // Remove any fixed overlays that block interaction
                document.querySelectorAll('div[style*="position: fixed"]').forEach(el => {
                    if (el.querySelector('a[href*="login"]') || el.querySelector('a[href*="signup"]')) {
                        el.remove();
                    }
                });
            }
        """)
        time.sleep(random.uniform(0.2, 0.5))
    except Exception:
        pass
