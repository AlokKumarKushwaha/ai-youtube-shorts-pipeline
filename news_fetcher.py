import sys
import urllib.parse
import xml.etree.ElementTree as ET
import html
import re
import json
from pathlib import Path
import requests

if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


from config import BASE_DIR

PROCESSED_FILE = BASE_DIR / "processed_news.json"

CATEGORIES = {
    "top": "https://news.google.com/rss?hl=hi&gl=IN&ceid=IN:hi",
    "tech": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=hi&gl=IN&ceid=IN:hi",
    "world": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=hi&gl=IN&ceid=IN:hi",
    "science": "https://news.google.com/rss/headlines/section/topic/SCIENCE?hl=hi&gl=IN&ceid=IN:hi",
    "sports": "https://news.google.com/rss/headlines/section/topic/SPORTS?hl=hi&gl=IN&ceid=IN:hi",
    "entertainment": "https://news.google.com/rss/headlines/section/topic/ENTERTAINMENT?hl=hi&gl=IN&ceid=IN:hi",
}

def clean_html(text: str) -> str:
    """Removes HTML tags and unescapes entities."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    return html.unescape(clean).strip()

def get_processed_ids() -> set:
    if PROCESSED_FILE.exists():
        try:
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def mark_as_processed(news_id: str):
    processed = get_processed_ids()
    processed.add(news_id)
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(processed), f, ensure_ascii=False, indent=2)

def fetch_latest_news(category_or_query: str = "tech", limit: int = 5, skip_processed: bool = True):
    """
    Fetches latest news from Google News RSS.
    Can be a category ('top', 'tech', 'world', etc.) or any custom search term.
    """
    processed = get_processed_ids() if skip_processed else set()

    if category_or_query.lower() in CATEGORIES:
        url = CATEGORIES[category_or_query.lower()]
    else:
        encoded_query = urllib.parse.quote(category_or_query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=hi&gl=IN&ceid=IN:hi"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    items = root.findall(".//item")

    news_list = []
    for item in items:
        title = item.find("title").text if item.find("title") is not None else ""
        link = item.find("link").text if item.find("link") is not None else ""
        pub_date = item.find("pubDate").text if item.find("pubDate") is not None else ""
        desc = item.find("description").text if item.find("description") is not None else ""

        clean_title = clean_html(title)
        clean_desc = clean_html(desc)

        if not clean_title:
            continue

        # News identifier based on title
        news_id = re.sub(r"\W+", "_", clean_title)[:60].lower()

        if skip_processed and news_id in processed:
            continue

        news_list.append({
            "id": news_id,
            "title": clean_title,
            "description": clean_desc,
            "published": pub_date,
            "link": link
        })

        if len(news_list) >= limit:
            break

    return news_list

if __name__ == "__main__":
    print("Testing News Fetcher...")
    news = fetch_latest_news("tech", limit=3, skip_processed=False)
    for i, n in enumerate(news, 1):
        print(f"\n[{i}] {n['title']}")
        print(f"Date: {n['published']}")
        print(f"Summary: {n['description'][:100]}...")
