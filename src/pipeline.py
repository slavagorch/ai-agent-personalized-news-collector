"""
Merge everything together:
1. Fetch raw articles.
2. Filter via regex.
3. Keep 5 freshest.
4. Summarize each.
5. Email the digest.
"""
import logging
from fetchers import get_tc_feed, get_hn_top
from filters import passes
from summarizer import summarize
from mailer import send

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

def run():
    logging.info("→ Fetching sources")
    articles = list(get_tc_feed()) + list(get_hn_top())
    logging.info(f"  fetched {len(articles)} total")

    logging.info("→ Filtering by keywords")
    picks = [a for a in articles if passes(a)]
    logging.info(f"  kept {len(picks)} matches")

    picks.sort(key=lambda x: x["published"], reverse=True)
    picks = picks[:5]
    logging.info(f"→ Taking top {len(picks)} for summary")

    digest_lines = []
    for art in picks:
        logging.info(f"   summarising: {art['title'][:60]}…")
        art["summary"] = summarize(art)
        digest_lines.append(
            f"• [{art['title']}]({art['url']}) — {art['summary']}"
        )

    markdown = "\n".join(digest_lines) or "No matching articles today."
    logging.info("→ Sending email")
    send(markdown)
    logging.info("✓ Done")


if __name__ == "__main__":
    run()