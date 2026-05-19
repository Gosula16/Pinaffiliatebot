import os
from dotenv import load_dotenv

load_dotenv()

# ── Amazon PAAPI ──────────────────────────────────────────────
AMAZON_ACCESS_KEY   = os.getenv("AMAZON_ACCESS_KEY", "")
AMAZON_SECRET_KEY   = os.getenv("AMAZON_SECRET_KEY", "")
AMAZON_PARTNER_TAG  = os.getenv("AMAZON_PARTNER_TAG", "yourtag-21")
AMAZON_MARKETPLACE  = "www.amazon.in"

# ── Pinterest ─────────────────────────────────────────────────
PINTEREST_TOKEN     = os.getenv("PINTEREST_ACCESS_TOKEN", "")
PINTEREST_BOARDS    = {
    "tech":    os.getenv("BOARD_TECH",    ""),
    "home":    os.getenv("BOARD_HOME",    ""),
    "fitness": os.getenv("BOARD_FITNESS", ""),
    "deals":   os.getenv("BOARD_DEALS",  ""),
}

# ── Anthropic ─────────────────────────────────────────────────
GEMINI_API_KEY      = os.getenv("GEMINI_API_KEY", "")

# ── Bot Behaviour ─────────────────────────────────────────────
MAX_PINS_PER_DAY    = int(os.getenv("MAX_PINS_PER_DAY", 15))
MIN_DELAY_SEC       = int(os.getenv("MIN_DELAY_SEC", 180))   # 3 min
MAX_DELAY_SEC       = int(os.getenv("MAX_DELAY_SEC", 420))   # 7 min
MAX_PRODUCTS_PER_KW = 3          # products fetched per keyword
ASIN_REPOST_DAYS    = 30         # days before same ASIN can be reposted

# ── Posting Windows (24h IST) ─────────────────────────────────
POST_WINDOWS = [
    {"start": "07:30", "end": "09:00", "pins": 5},
    {"start": "12:00", "end": "13:00", "pins": 4},
    {"start": "18:30", "end": "20:00", "pins": 5},
    {"start": "22:00", "end": "23:00", "pins": 3},
]

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
OUTPUT_IMAGES   = os.path.join(BASE_DIR, "output", "images")
DATA_DIR        = os.path.join(BASE_DIR, "data")
LOGS_DIR        = os.path.join(BASE_DIR, "logs")
PRODUCTS_FILE   = os.path.join(DATA_DIR, "products.json")
POSTED_LOG      = os.path.join(DATA_DIR, "posted_log.json")
TRENDS_FILE     = os.path.join(DATA_DIR, "trends.json")
DAILY_STATS     = os.path.join(DATA_DIR, "daily_stats.json")

# ── Evergreen fallback keywords (used if pytrends fails) ──────
FALLBACK_KEYWORDS = [
    "best wireless earbuds under 2000",
    "budget smartphone india 2026",
    "best laptop under 40000",
    "home gym equipment india",
    "kitchen gadgets amazon india",
    "best power bank 2026",
    "gaming accessories budget",
    "work from home essentials",
    "best smartwatch under 3000",
    "portable bluetooth speaker india",
]

# ── Image Templates ───────────────────────────────────────────
IMAGE_TEMPLATES = [
    {"bg": (20, 20, 30),    "text": (255,255,255), "badge": (230, 57, 70),  "name": "dark_red"},
    {"bg": (245, 240, 230), "text": (30, 30, 30),  "badge": (39, 174, 96),  "name": "cream_green"},
    {"bg": (240, 248, 255), "text": (29, 53, 87),  "badge": (69, 123, 157), "name": "light_blue"},
    {"bg": (255, 255, 255), "text": (20, 20, 20),  "badge": (230, 57, 70),  "name": "minimal_white"},
    {"bg": (29, 53, 87),    "text": (255,255,255), "badge": (241, 196, 15), "name": "navy_gold"},
]
