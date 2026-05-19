"""M2 — Product Fetcher: Gets Amazon India products via PAAPI or scrape fallback."""

import json, logging, os, time, random, re, requests
from datetime import datetime, timedelta
from config import (AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_PARTNER_TAG,
                    PRODUCTS_FILE, POSTED_LOG, DATA_DIR, MAX_PRODUCTS_PER_KW,
                    ASIN_REPOST_DAYS)

logger = logging.getLogger("pinbot.products")


def _load_posted_asins() -> set:
    if not os.path.exists(POSTED_LOG):
        return set()
    with open(POSTED_LOG) as f:
        log = json.load(f)
    cutoff = datetime.now() - timedelta(days=ASIN_REPOST_DAYS)
    recent = {e["asin"] for e in log if datetime.fromisoformat(e["posted_at"]) > cutoff}
    return recent


def _build_affiliate_link(asin: str) -> str:
    return f"https://www.amazon.in/dp/{asin}?tag={AMAZON_PARTNER_TAG}"


def _fetch_via_paapi(keyword: str, max_results: int) -> list[dict]:
    """Use python-amazon-paapi if keys are set."""
    if not AMAZON_ACCESS_KEY or not AMAZON_SECRET_KEY:
        return []
    try:
        from amazon.paapi import AmazonApi
        amazon = AmazonApi(
            AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY,
            AMAZON_PARTNER_TAG, "IN"
        )
        items = amazon.search_items(keywords=keyword, item_count=max_results * 2)
        results = []
        for item in (items.items or []):
            try:
                title = item.item_info.title.display_value
                asin  = item.asin
                price_val = None
                currency  = "INR"
                if item.offers and item.offers.listings:
                    p = item.offers.listings[0].price
                    price_val = p.amount
                    currency  = p.currency or "INR"
                img = None
                if item.images and item.images.primary:
                    img = item.images.primary.large.url
                results.append({
                    "asin": asin,
                    "title": title,
                    "price": price_val,
                    "currency": currency,
                    "image_url": img,
                    "affiliate_link": _build_affiliate_link(asin),
                    "keyword": keyword,
                    "source": "paapi",
                })
                if len(results) >= max_results:
                    break
            except Exception:
                continue
        return results
    except Exception as e:
        logger.warning(f"PAAPI error for '{keyword}': {e}")
        return []


def _fetch_via_scrape_fallback(keyword: str, max_results: int) -> list[dict]:
    """Lightweight fallback — scrapes Amazon search page for ASINs + titles."""
    try:
        query = keyword.replace(" ", "+")
        url   = f"https://www.amazon.in/s?k={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0 Safari/537.36",
            "Accept-Language": "en-IN,en;q=0.9",
        }
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            return []

        # Extract ASINs from data-asin attributes
        asins = re.findall(r'data-asin="([A-Z0-9]{10})"', r.text)
        titles = re.findall(r'class="a-size-medium[^"]*"[^>]*><span[^>]*>([^<]{10,120})<', r.text)
        prices = re.findall(r'class="a-price-whole">([0-9,]+)<', r.text)
        imgs   = re.findall(r'class="s-image"[^>]*src="([^"]+)"', r.text)

        results = []
        for i, asin in enumerate(dict.fromkeys(asins)):  # deduplicate preserving order
            if not asin or asin == "":
                continue
            results.append({
                "asin": asin,
                "title": titles[i] if i < len(titles) else keyword.title(),
                "price": float(prices[i].replace(",", "")) if i < len(prices) else None,
                "currency": "INR",
                "image_url": imgs[i] if i < len(imgs) else None,
                "affiliate_link": _build_affiliate_link(asin),
                "keyword": keyword,
                "source": "scrape",
            })
            if len(results) >= max_results:
                break
        return results
    except Exception as e:
        logger.warning(f"Scrape fallback error for '{keyword}': {e}")
        return []


def fetch_products(keywords: list[str]) -> list[dict]:
    os.makedirs(DATA_DIR, exist_ok=True)
    posted_asins = _load_posted_asins()
    all_products = []

    for kw in keywords:
        logger.info(f"Fetching products for: {kw}")

        products = _fetch_via_paapi(kw, MAX_PRODUCTS_PER_KW)
        if not products:
            logger.info(f"  PAAPI empty — trying scrape fallback")
            products = _fetch_via_scrape_fallback(kw, MAX_PRODUCTS_PER_KW)

        # Filter already-posted ASINs
        fresh = [p for p in products if p["asin"] not in posted_asins]
        logger.info(f"  Got {len(products)} products, {len(fresh)} are fresh")
        all_products.extend(fresh)

        # Respectful rate limiting
        time.sleep(random.uniform(1.2, 2.5))

    # Save to cache
    payload = {"fetched_at": datetime.now().isoformat(), "products": all_products}
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(all_products)} fresh products to cache")
    return all_products


def load_products() -> list[dict]:
    if not os.path.exists(PRODUCTS_FILE):
        return []
    with open(PRODUCTS_FILE) as f:
        return json.load(f).get("products", [])
