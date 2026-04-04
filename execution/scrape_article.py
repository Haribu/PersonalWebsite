"""
scrape_article.py — Layer 3 Execution Script
=============================================
Enriches queued articles with full body text. Uses Feedly-provided content
when it's substantial enough; falls back to scraping the source URL via
trafilatura for thin or missing content.

Input:  .tmp/queue.json
Output: .tmp/articles.json

Exit codes:
  0 — Success
  1 — Fatal error (input file missing)
"""

import os
import sys
import json

import requests

EXECUTION_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(EXECUTION_DIR)
TMP_DIR = os.path.join(ROOT_DIR, ".tmp")

INPUT_PATH = os.path.join(TMP_DIR, "queue.json")
OUTPUT_PATH = os.path.join(TMP_DIR, "articles.json")

# Threshold: if Feedly content is this long or more, skip scraping
FEEDLY_CONTENT_THRESHOLD = 500

# Request headers to mimic a browser (avoids trivial bot blocks)
SCRAPE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def scrape_url(url: str) -> str:
    """
    Attempt to extract clean article text from a URL using trafilatura.
    Falls back to a basic requests fetch if trafilatura is unavailable.
    Returns empty string on failure.
    """
    if not url:
        return ""

    try:
        import trafilatura

        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            text = trafilatura.extract(
                downloaded,
                include_comments=False,
                include_tables=False,
                no_fallback=False,
            )
            if text:
                return text.strip()
    except ImportError:
        print("  [WARN] trafilatura not installed — attempting raw requests fallback.")
    except Exception as e:
        print(f"  [WARN] trafilatura failed for {url}: {e}")

    # Fallback: raw requests + basic HTML stripping
    try:
        response = requests.get(url, headers=SCRAPE_HEADERS, timeout=20)
        response.raise_for_status()

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")
            # Remove script/style noise
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            # Prefer article/main, fall back to body
            content_tag = soup.find("article") or soup.find("main") or soup.find("body")
            if content_tag:
                return content_tag.get_text(separator=" ", strip=True)
        except ImportError:
            # Absolute last resort: strip all HTML tags manually
            import re

            text = re.sub(r"<[^>]+>", " ", response.text)
            return " ".join(text.split())

    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code in (401, 403, 429):
            print(f"  [WARN] Paywalled or rate-limited ({e.response.status_code}): {url}")
        else:
            print(f"  [WARN] HTTP error scraping {url}: {e}")
    except Exception as e:
        print(f"  [WARN] Failed to scrape {url}: {e}")

    return ""


def enrich_articles(queue: list[dict]) -> list[dict]:
    """
    For each queued article, ensure full_text is populated.
    Prefers Feedly content; scrapes the URL if it's too thin.
    """
    enriched = []

    for article in queue:
        url = article.get("url", "")
        feedly_content = article.get("feedly_content", "")
        title = article.get("issue_title", url[:60])

        print(f"\nProcessing: {title[:70]}")

        if len(feedly_content) >= FEEDLY_CONTENT_THRESHOLD:
            print(f"  ✓ Using Feedly content ({len(feedly_content)} chars)")
            full_text = feedly_content
            source = "feedly"
        else:
            print(f"  → Feedly content thin ({len(feedly_content)} chars), scraping URL...")
            scraped = scrape_url(url)
            if scraped:
                print(f"  ✓ Scraped {len(scraped)} chars from URL")
                full_text = scraped
                source = "scraped"
            else:
                # Fall all the way back to whatever Feedly gave us, even if thin
                print(f"  [WARN] Scraping failed — using available Feedly content.")
                full_text = feedly_content
                source = "feedly_fallback"

        enriched_article = {
            **article,
            "full_text": full_text,
            "text_source": source,
        }
        enriched.append(enriched_article)

    return enriched


def main():
    if not os.path.exists(INPUT_PATH):
        print(f"[FATAL] {INPUT_PATH} not found. Run fetch_queue.py first.", file=sys.stderr)
        sys.exit(1)

    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        queue = json.load(f)

    if not queue:
        print("Queue is empty. Writing empty articles.json.")
        with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)
        sys.exit(0)

    print(f"Enriching {len(queue)} article(s)...\n")
    articles = enrich_articles(queue)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Enriched {len(articles)} article(s). Written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
