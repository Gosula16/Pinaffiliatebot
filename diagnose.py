"""Quick configuration checks for PinAffiliateBot."""

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


def masked(value: str) -> str:
    if not value:
        return "missing"
    if len(value) <= 8:
        return "set"
    return f"{value[:4]}...{value[-4:]}"


def check_required_env() -> bool:
    print("Environment")
    required = [
        "AMAZON_ACCESS_KEY",
        "AMAZON_SECRET_KEY",
        "AMAZON_PARTNER_TAG",
        "PINTEREST_ACCESS_TOKEN",
        "GEMINI_API_KEY",
    ]
    board_keys = ["BOARD_TECH", "BOARD_HOME", "BOARD_FITNESS", "BOARD_DEALS"]
    ok = True
    for name in required + board_keys:
        value = os.getenv(name, "")
        status = "OK" if value else "MISSING"
        print(f"  {status:7} {name}: {masked(value)}")
        ok = ok and bool(value)
    return ok


def check_pinterest() -> bool:
    token = os.getenv("PINTEREST_ACCESS_TOKEN", "")
    if not token:
        print("\nPinterest: skipped, PINTEREST_ACCESS_TOKEN missing")
        return False

    print("\nPinterest")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        account = requests.get(
            f"{PINTEREST_API}/user_account",
            headers=headers,
            timeout=20,
        )
        if account.status_code == 401:
            print("  FAIL    token rejected by Pinterest")
            return False
        account.raise_for_status()
        print("  OK      token is accepted")
    except Exception as exc:
        print(f"  FAIL    token check failed: {exc}")
        return False

    board_ids = {
        name: os.getenv(name, "")
        for name in ["BOARD_TECH", "BOARD_HOME", "BOARD_FITNESS", "BOARD_DEALS"]
        if os.getenv(name, "")
    }
    boards_ok = True
    for name, board_id in board_ids.items():
        try:
            response = requests.get(
                f"{PINTEREST_API}/boards/{board_id}",
                headers=headers,
                timeout=20,
            )
            if response.ok:
                board = response.json()
                print(f"  OK      {name}: {board.get('name', board_id)}")
            else:
                print(f"  FAIL    {name}: {response.status_code} {response.text[:120]}")
                boards_ok = False
        except Exception as exc:
            print(f"  FAIL    {name}: {exc}")
            boards_ok = False
    return boards_ok


def check_gemini() -> bool:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        print("\nGemini: skipped, GEMINI_API_KEY missing")
        return False

    print("\nGemini")
    payload = {
        "contents": [{"parts": [{"text": "Reply with exactly: ok"}]}],
        "generationConfig": {"maxOutputTokens": 10},
    }
    try:
        response = requests.post(
            GEMINI_ENDPOINT,
            params={"key": api_key},
            json=payload,
            timeout=20,
        )
        if response.ok:
            print("  OK      API key is accepted")
            return True
        print(f"  FAIL    {response.status_code} {response.text[:200]}")
        return False
    except Exception as exc:
        print(f"  FAIL    Gemini check failed: {exc}")
        return False


def main() -> int:
    env_ok = check_required_env()
    pinterest_ok = check_pinterest()
    gemini_ok = check_gemini()

    print("\nSummary")
    if env_ok and pinterest_ok and gemini_ok:
        print("  OK      configuration looks ready")
        return 0
    print("  FAIL    fix the items above before expecting pins to post")
    return 1


if __name__ == "__main__":
    sys.exit(main())
