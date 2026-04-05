"""
ニュースフェッチャー
RSSフィードからニュースを取得し、AIフィルタリングを行う
"""
import feedparser
import requests
import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
CACHE_DURATION_HOURS = 1  # キャッシュ有効時間


def get_cache_path(key: str) -> str:
    safe_key = key.replace("/", "_").replace(":", "_")
    return os.path.join(CACHE_DIR, f"{safe_key}.json")


def load_cache(key: str) -> Optional[dict]:
    path = get_cache_path(key)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cached_at = datetime.fromisoformat(data.get("cached_at", "2000-01-01"))
        if datetime.now() - cached_at > timedelta(hours=CACHE_DURATION_HOURS):
            return None
        return data
    except Exception:
        return None


def save_cache(key: str, data: dict):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = get_cache_path(key)
    data["cached_at"] = datetime.now().isoformat()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def fetch_feed(feed_url: str, feed_name: str, max_items: int = 20) -> List[Dict]:
    """RSSフィードを取得してニュースリストを返す"""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AINewsBot/1.0)",
    }
    try:
        response = requests.get(feed_url, headers=headers, timeout=10)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
    except requests.exceptions.RequestException:
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            logger.warning(f"Failed to fetch {feed_name}: {e}")
            return []

    articles = []
    cutoff = datetime.now() - timedelta(days=3)  # 3日以内の記事を対象

    for entry in feed.entries[:max_items]:
        try:
            # 日付の取得
            pub_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                pub_date = datetime(*entry.published_parsed[:6])
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                pub_date = datetime(*entry.updated_parsed[:6])

            if pub_date and pub_date < cutoff:
                continue

            # 概要の取得
            summary = ""
            if hasattr(entry, "summary"):
                summary = entry.summary[:500] if entry.summary else ""
            elif hasattr(entry, "description"):
                summary = entry.description[:500] if entry.description else ""

            # HTMLタグを簡易除去
            import re
            summary = re.sub(r"<[^>]+>", "", summary).strip()

            articles.append({
                "title": entry.get("title", "").strip(),
                "url": entry.get("link", ""),
                "summary": summary,
                "published": pub_date.isoformat() if pub_date else datetime.now().isoformat(),
                "source": feed_name,
            })
        except Exception as e:
            logger.debug(f"Error parsing entry: {e}")
            continue

    return articles


def fetch_general_news() -> List[Dict]:
    """一般AIニュースを全フィードから取得"""
    from news_sources import GENERAL_AI_FEEDS

    cache_key = f"general_news_{datetime.now().strftime('%Y%m%d_%H')}"
    cached = load_cache(cache_key)
    if cached:
        return cached["articles"]

    all_articles = []
    for feed_info in GENERAL_AI_FEEDS:
        articles = fetch_feed(feed_info["url"], feed_info["name"])
        all_articles.extend(articles)
        time.sleep(0.5)  # レート制限対策

    # 重複URLを除去
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article["url"] not in seen_urls and article["url"]:
            seen_urls.add(article["url"])
            unique_articles.append(article)

    save_cache(cache_key, {"articles": unique_articles})
    return unique_articles


def fetch_company_news(company_key: str) -> List[Dict]:
    """企業別ニュースを取得"""
    from news_sources import COMPANY_FEEDS

    if company_key not in COMPANY_FEEDS:
        return []

    company = COMPANY_FEEDS[company_key]
    cache_key = f"company_{company_key}_{datetime.now().strftime('%Y%m%d_%H')}"
    cached = load_cache(cache_key)
    if cached:
        return cached["articles"]

    all_articles = []

    # 公式フィード
    for feed_info in company.get("feeds", []):
        articles = fetch_feed(feed_info["url"], feed_info["name"], max_items=15)
        all_articles.extend(articles)
        time.sleep(0.5)

    # Google Newsフィード
    google_url = company.get("google_news_url", "")
    if google_url:
        articles = fetch_feed(google_url, f"{company['display_name']} News", max_items=20)
        all_articles.extend(articles)

    # 重複URLを除去
    seen_urls = set()
    unique_articles = []
    for article in all_articles:
        if article["url"] not in seen_urls and article["url"]:
            seen_urls.add(article["url"])
            unique_articles.append(article)

    save_cache(cache_key, {"articles": unique_articles})
    return unique_articles
