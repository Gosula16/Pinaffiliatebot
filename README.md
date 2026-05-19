# PinAffiliateBot

Pinterest + Amazon India affiliate automation.

## What It Does

1. Loads trending product keywords.
2. Fetches matching Amazon India products.
3. Generates Pinterest-ready images.
4. Writes captions with Google Gemini, with a local fallback if Gemini is unavailable.
5. Posts pins to Pinterest boards.
6. Tracks daily posting limits and queues board rotation metadata.
7. Sends optional Telegram alerts.

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local `.env` file from the template:

```bash
cp .env.example .env
```

Fill in these required values:

```bash
AMAZON_ACCESS_KEY=
AMAZON_SECRET_KEY=
AMAZON_PARTNER_TAG=
PINTEREST_ACCESS_TOKEN=
BOARD_TECH=
BOARD_HOME=
BOARD_FITNESS=
BOARD_DEALS=
GEMINI_API_KEY=
```

The caption module uses `GEMINI_API_KEY`. Do not use `ANTHROPIC_API_KEY`; this bot is wired for Google Gemini.

## GitHub Actions Secrets

For scheduled cloud runs, add these repository secrets in GitHub:

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

The workflow runs four times a day and sets `SKIP_WINDOW_CHECK=true`, because GitHub runners use UTC while the bot schedule is intended for IST windows.

## Diagnose Configuration

Before expecting pins to post, run:

```bash
python diagnose.py
```

This checks required environment variables, validates the Pinterest token and board IDs, and sends a tiny Gemini API test request.

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

## Posting Settings

Default settings:

```text
MAX_PINS_PER_DAY=15
PINS_PER_RUN=5
MIN_DELAY_SEC=180
MAX_DELAY_SEC=420
```

`PINS_PER_RUN` is used when `SKIP_WINDOW_CHECK=true`, such as in GitHub Actions.

## Deployment Notes

The bot runs through GitHub Actions. Vercel is only configured to host the static files in `public/`; it does not run the Python bot.

Removed stale platform files:

- `Procfile` was for Heroku.
- `netlify.toml` was for Netlify.
- Root `dashboard.html` duplicated `public/dashboard.html`.
- `setup.bat` was a local Windows helper and is not needed for the repo.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Captions fall back instead of using AI | Confirm `GEMINI_API_KEY` is set and `python diagnose.py` passes |
| Pinterest 401 | Refresh `PINTEREST_ACCESS_TOKEN` |
| Board errors | Use Pinterest board IDs, not board names or URLs |
| No Amazon products | Confirm PAAPI credentials and partner tag are active |
| GitHub run produces no pins | Check Actions logs and uploaded `logs/` artifact |
