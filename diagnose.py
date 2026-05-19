"""PinAffiliateBot diagnostics.

Run this before posting:
    python diagnose.py
"""

import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

PINTEREST_API = "https://api.pinterest.com/v5"
GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

OK = "OK"
WARN = "WARN"
FAIL = "FAIL"


def value_is_real(value: str) -> bool:
    placeholders = {
        "",
        "your_amazon_access_key_here",
        "your_amazon_secret_key_here",
        "yourtag-21",
        "your_pinterest_oauth_token_here",
        "your_tech_board_id",
        "your_home_board_id",
        "your_fitness_board_id",
        "your_deals_board_id",
        "your_tech_board_id_number",
        "your_home_board_id_number",
        "your_fitness_board_id_number",
        "your_deals_board_id_number",
        "your_gemini_api_key_here",
    }
    return value.strip() not in placeholders


def line(status: str, message: str) -> None:
    print(f"  {status:5} {message}")


def check_environment() -> tuple[int, bool]:
    print("1. Environment variables")
    errors = 0

    required_for_posting = [
        "PINTEREST_ACCESS_TOKEN",
        "BOARD_TECH",
        "BOARD_HOME",
        "BOARD_FITNESS",
        "BOARD_DEALS",
    ]
    optional_with_fallback = [
        "AMAZON_ACCESS_KEY",
        "AMAZON_SECRET_KEY",
        "AMAZON_PARTNER_TAG",
        "GEMINI_API_KEY",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHAT_ID",
    ]

    for name in required_for_posting:
        if value_is_real(os.getenv(name, "")):
            line(OK, f"{name} is set")
        else:
            line(FAIL, f"{name} is missing")
            errors += 1

    amazon_ready = all(
        value_is_real(os.getenv(name, ""))
        for name in ["AMAZON_ACCESS_KEY", "AMAZON_SECRET_KEY", "AMAZON_PARTNER_TAG"]
    )

    for name in optional_with_fallback:
        if value_is_real(os.getenv(name, "")):
            line(OK, f"{name} is set")
        elif name.startswith("AMAZON_"):
            line(WARN, f"{name} is missing; product fetcher will try scrape fallback")
        elif name == "GEMINI_API_KEY":
            line(WARN, "GEMINI_API_KEY is missing; captions will use rule-based fallback")
        elif name.startswith("TELEGRAM_"):
            line(WARN, f"{name} is missing; notifications are optional")

    return errors, amazon_ready


def check_pinterest() -> int:
    print("\n2. Pinterest API")
    token = os.getenv("PINTEREST_ACCESS_TOKEN", "")
    if not value_is_real(token):
        line(FAIL, "No Pinterest token to test")
        return 1

    errors = 0
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(
            f"{PINTEREST_API}/user_account",
            headers=headers,
            timeout=15,
        )
        if response.status_code == 200:
            username = response.json().get("username", "unknown")
            line(OK, f"Token valid; logged in as {username}")
        elif response.status_code == 401:
            line(FAIL, "Pinterest token is expired or invalid")
            return 1
        else:
            line(FAIL, f"Pinterest returned {response.status_code}: {response.text[:160]}")
            return 1
    except Exception as exc:
        line(FAIL, f"Could not reach Pinterest API: {exc}")
        return 1

    for env_name, label in [
        ("BOARD_TECH", "tech"),
        ("BOARD_HOME", "home"),
        ("BOARD_FITNESS", "fitness"),
        ("BOARD_DEALS", "deals"),
    ]:
        board_id = os.getenv(env_name, "")
        if not value_is_real(board_id):
            line(FAIL, f"{env_name} is missing")
            errors += 1
            continue

        try:
            response = requests.get(
                f"{PINTEREST_API}/boards/{board_id}",
                headers=headers,
                timeout=15,
            )
            if response.status_code == 200:
                board_name = response.json().get("name", board_id)
                line(OK, f"{label} board exists: {board_name}")
            elif response.status_code == 404:
                line(FAIL, f"{env_name} not found; check the board ID")
                errors += 1
            else:
                line(WARN, f"{env_name} returned {response.status_code}: {response.text[:120]}")
        except Exception as exc:
            line(FAIL, f"Could not verify {env_name}: {exc}")
            errors += 1

    return errors


def check_gemini() -> int:
    print("\n3. Gemini API")
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not value_is_real(api_key):
        line(WARN, "Skipping Gemini test; captions will use fallback")
        return 0

    payload = {
        "contents": [{"parts": [{"text": "Reply with exactly: OK"}]}],
        "generationConfig": {"maxOutputTokens": 5},
    }

    try:
        response = requests.post(
            GEMINI_ENDPOINT,
            params={"key": api_key},
            json=payload,
            timeout=15,
        )
        if response.status_code == 200:
            line(OK, "Gemini API key is accepted")
            return 0
        if response.status_code == 400:
            message = response.json().get("error", {}).get("message", response.text)
            line(FAIL, f"Gemini API key appears invalid: {message[:160]}")
            return 1
        line(WARN, f"Gemini returned {response.status_code}: {response.text[:160]}")
        return 0
    except Exception as exc:
        line(FAIL, f"Could not reach Gemini API: {exc}")
        return 1


def check_directories() -> None:
    print("\n4. Local directories")
    for folder in ["output/images", "data", "logs"]:
        os.makedirs(folder, exist_ok=True)
        line(OK, f"{folder}/ exists")


def main() -> int:
    print("\n" + "=" * 55)
    print("PinAffiliateBot diagnostics")
    print("=" * 55 + "\n")

    errors, amazon_ready = check_environment()
    errors += check_pinterest()
    errors += check_gemini()
    check_directories()

    print("\n" + "=" * 55)
    if errors == 0:
        line(OK, "Posting configuration looks ready")
        if not amazon_ready:
            line(WARN, "Amazon PAAPI is incomplete; scrape fallback may be less reliable")
        print("  Next: python main.py --dry-run")
        print("  Then: python main.py --once")
    else:
        line(FAIL, f"{errors} issue(s) found; fix them before expecting pins to post")
    print("=" * 55 + "\n")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
