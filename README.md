# PinAffiliateBot

Pinterest + Amazon India affiliate automation. It discovers trending products, generates pin images, writes Gemini captions, and posts to Pinterest automatically through GitHub Actions.

## Root Causes Fixed

1. `GEMINI_API_KEY` was confusingly documented as `ANTHROPIC_API_KEY` in the env template. The bot uses Google Gemini, so the template now uses `GEMINI_API_KEY`.
2. The Gemini request URL was previously built at import time. It is now built when the request is made, after environment variables have loaded.
3. GitHub Actions runs on exact UTC schedules for the intended IST posting windows, so the workflow now sets `SKIP_WINDOW_CHECK=true` and `PINS_PER_RUN=5`.
4. Stale deployment files were removed: `Procfile`, `netlify.toml`, root `dashboard.html`, and `setup.bat`.

## Quick Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file:

```bash
cp .env.example .env
```

Fill in the required values:

```text
AMAZON_ACCESS_KEY
AMAZON_SECRET_KEY
AMAZON_PARTNER_TAG
PINTEREST_ACCESS_TOKEN
BOARD_TECH
BOARD_HOME
BOARD_FITNESS
BOARD_DEALS
GEMINI_API_KEY
```

Optional notification values:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

## Where To Get Keys

| Key | Where to get it |
| --- | --- |
| `AMAZON_ACCESS_KEY` / `AMAZON_SECRET_KEY` | Associates Central > Tools > Product Advertising API |
| `AMAZON_PARTNER_TAG` | Your Amazon Associates tag, usually like `yourname-21` |
| `PINTEREST_ACCESS_TOKEN` | developers.pinterest.com > Your App > Generate Token |
| `BOARD_TECH` / `BOARD_HOME` / `BOARD_FITNESS` / `BOARD_DEALS` | Pinterest API board IDs |
| `GEMINI_API_KEY` | https://aistudio.google.com/app/apikey |
| `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` | Optional, from Telegram |

Pinterest token scopes should include `pins:read`, `pins:write`, and `boards:read`.

## Diagnose Before Running

Run:

```bash
python diagnose.py
```

This checks required environment variables, validates the Pinterest token, verifies configured board IDs, sends a tiny Gemini test request, and confirms local output directories exist.

## Commands

```bash
python main.py --dry-run    # Generate images and captions without posting
python main.py --once       # Run one posting batch
python main.py --loop       # Keep checking posting windows locally
python main.py --trends     # Refresh trends only
python main.py --products   # Fetch products only
python main.py --summary    # Send Telegram daily summary
python diagnose.py          # Check configuration
```

## GitHub Actions

Add these repository secrets in GitHub under Settings > Secrets and variables > Actions:

```text
AMAZON_ACCESS_KEY
AMAZON_SECRET_KEY
AMAZON_PARTNER_TAG
PINTEREST_ACCESS_TOKEN
BOARD_TECH
BOARD_HOME
BOARD_FITNESS
BOARD_DEALS
GEMINI_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

The workflow runs four times per day:

| IST time | UTC cron |
| --- | --- |
| 07:30 | `0 2 * * *` |
| 12:00 | `30 6 * * *` |
| 18:30 | `0 13 * * *` |
| 22:00 | `30 16 * * *` |

The workflow also opts into Node 24 for GitHub JavaScript actions and ignores missing `output/images/` artifacts when no images were created.

## Project Structure

```text
pinaffiliatebot/
|-- main.py
|-- config.py
|-- diagnose.py
|-- modules/
|   |-- trend_engine.py
|   |-- product_fetcher.py
|   |-- image_generator.py
|   |-- caption_writer.py
|   |-- pin_poster.py
|   |-- board_rotation.py
|   |-- notifier.py
|   `-- scheduler.py
|-- public/
|   |-- index.html
|   `-- dashboard.html
|-- .github/workflows/run_bot.yml
|-- .env.example
`-- requirements.txt
```

## Vercel

Vercel hosts only the static dashboard in `public/`. The Python bot runs through GitHub Actions, not Vercel.

Vercel settings:

```text
Framework preset: Other
Output directory: public
Build command: none
```

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Pins still do not post | Run `python diagnose.py`, then inspect the latest GitHub Actions logs |
| Pinterest 401 | Regenerate `PINTEREST_ACCESS_TOKEN` |
| Board ID failure | Use Pinterest API board IDs, not board names or URLs |
| No products | PAAPI may be inactive; the bot will try scrape fallback |
| Gemini falls back | Confirm `GEMINI_API_KEY` is set and valid |
