import feedparser
import requests
import datetime as dt

TECHCRUNCH_RSS = "https://techcrunch.com/tag/ai/feed/"
HN_API_PREFIX = "https://hacker-news.firebaseio.com/v0"

def get_tc_feed(limit: int = 100):
    """
    Yield up to `limit` AI-tagged TechCrunch articles.
    If limit is None, yields all entries.
    """
    feed = feedparser.parse(TECHCRUNCH_RSS)
    entries = feed.entries if limit is None else feed.entries[:limit]
    for e in entries:
        yield {
            "title":     e.title,
            "url":       e.link,
            "source":    "TechCrunch",
            "published": dt.datetime(*e.published_parsed[:6]),
            "desc":      getattr(e, "summary", ""),
        }

def get_hn_top(limit: int = 100):
    """
    Yield up to `limit` top HN stories that have URLs.
    """
    ids = requests.get(f"{HN_API_PREFIX}/topstories.json").json()[:limit]
    for _id in ids:
        item = requests.get(f"{HN_API_PREFIX}/item/{_id}.json").json()
        if not item or "url" not in item:
            continue
        yield {
            "title":     item["title"],
            "url":       item["url"],
            "source":    "HackerNews",
            "published": dt.datetime.fromtimestamp(item["time"]),
            "desc":      "",
        }