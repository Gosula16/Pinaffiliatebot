"""M4 - Caption Writer: Generates unique Pinterest captions via Google Gemini API."""

import json
import logging
import re

import requests

from config import GEMINI_API_KEY

logger = logging.getLogger("pinbot.captions")

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

SYSTEM_PROMPT = """You write Pinterest pin captions for Amazon India affiliate products.
Rules:
- Sound natural and helpful, NOT like an advertisement
- Mention the price naturally inside the sentence
- End with a soft call-to-action: "Check link", "See full details", "Worth a look"
- Use 3-6 hashtags only - NO generic ones like #love #beautiful #instagood
- No ALL CAPS anywhere in title or description
- Return ONLY valid JSON - no preamble, no markdown fences, no explanation"""

USER_TEMPLATE = """Write a Pinterest pin caption for this Amazon India product:
Title: {title}
Price: Rs. {price}
Category: {category}
Keyword: {keyword}

Return JSON exactly like this (no extra text):
{{
  "title": "pin title here - 50-100 chars, main keyword first",
  "description": "natural helpful description - 200-400 chars, includes price, ends with soft CTA",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3", "hashtag4"]
}}"""


def _guess_category(product: dict) -> str:
    kw = (product.get("keyword", "") + " " + product.get("title", "")).lower()
    if any(w in kw for w in ["earbuds", "headphone", "laptop", "phone", "tablet", "charger", "speaker", "gadget", "gaming"]):
        return "Electronics & Gadgets"
    if any(w in kw for w in ["kitchen", "mixer", "cooker", "blender", "pan", "knife", "appliance"]):
        return "Kitchen & Home"
    if any(w in kw for w in ["gym", "fitness", "yoga", "protein", "dumbbell", "sports", "cycle"]):
        return "Fitness & Sports"
    if any(w in kw for w in ["desk", "chair", "lamp", "office", "work from home", "monitor"]):
        return "Work From Home"
    if any(w in kw for w in ["skin", "face", "hair", "beauty", "cream", "serum", "shampoo"]):
        return "Beauty & Personal Care"
    return "Amazon India Deals"


def _call_gemini(prompt: str) -> str | None:
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not configured; using fallback captions")
        return None

    try:
        payload = {
            "contents": [{
                "parts": [{"text": SYSTEM_PROMPT + "\n\n" + prompt}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 400,
            },
        }
        response = requests.post(
            GEMINI_ENDPOINT,
            params={"key": GEMINI_API_KEY},
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
        return text
    except Exception as e:
        logger.warning(f"Gemini API error: {e}")
        return None


def generate_caption(product: dict) -> dict:
    """Returns dict with title, description, hashtags."""
    category = _guess_category(product)
    price = int(product.get("price") or 0)
    price_str = f"{price:,}" if price else "check listing"

    prompt = USER_TEMPLATE.format(
        title=product.get("title", "")[:120],
        price=price_str,
        category=category,
        keyword=product.get("keyword", ""),
    )

    raw = _call_gemini(prompt)

    if raw:
        try:
            result = json.loads(raw)
            if all(k in result for k in ["title", "description", "hashtags"]):
                logger.info(f"Gemini caption OK for ASIN {product.get('asin')}")
                return result
        except json.JSONDecodeError as e:
            logger.warning(f"Gemini JSON parse failed: {e} - using fallback")

    return _fallback_caption(product)


def _fallback_caption(product: dict) -> dict:
    """Rule-based fallback when Gemini is unavailable."""
    title = product.get("title", "Great Product")[:60]
    price = int(product.get("price") or 0)
    kw = product.get("keyword", "deals").lower()
    category = _guess_category(product)

    price_str = f"Rs. {price:,}" if price else "at a great price"
    desc = (
        f"Looking for the best {kw} in India? This top-rated pick is available for "
        f"{price_str} on Amazon - excellent value for money. "
        f"Check the link for full details and today's pricing."
    )
    tags = [
        kw.replace(" ", ""),
        "amazonindia",
        "budgetbuys",
        "indiatech" if "tech" in category.lower() else "amazondeals",
        "bestproducts",
    ]
    return {
        "title": f"{title} | Top Pick India 2026",
        "description": desc[:500],
        "hashtags": tags,
    }
