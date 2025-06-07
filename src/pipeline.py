"""
Merge everything together:
1. Fetch raw articles.
2. Filter via regex.
3. Keep 5 freshest.
4. Summarize each.
5. Send via Telegram.
"""
import logging
from fetchers import get_tc_feed, get_hn_top
from filters import passes
from summarizer import summarize
from tg_bot import send_tg
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)

def run():
    logging.info("→ Fetching sources")
    articles = list(get_tc_feed()) + list(get_hn_top())
    logging.info(f"  fetched {len(articles)} total")

    # log the top-5 headlines
    for idx, art in enumerate(articles[:5], start=1):
        logging.info(f"    {idx}. {art['title']}")

    logging.info("→ Filtering by keywords")
    picks = [a for a in articles if passes(a)]
    logging.info(f"  kept {len(picks)} matches")

    picks.sort(key=lambda x: x["published"], reverse=True)
    picks = picks[:4]
    logging.info(f"→ Taking top {len(picks)} for summary")

    for art in picks:
        logging.info(f"   summarising: {art['title'][:60]}…")
        art["summary"] = summarize(art)

    logging.info("→ Sending a message in Tg")
    asyncio.run(send_tg(picks))
    logging.info("✓ Done")

if __name__ == "__main__":
    run()
