# -------- IMPORTS --------
import functools, requests, re             # std libs for memo-cache, HTTP fetch, regex
from bs4 import BeautifulSoup              # quick HTML → plain-text converter
from transformers import pipeline          # HF helper that wraps a pre-trained model

# -------- PIPELINE FACTORY --------
@functools.lru_cache(maxsize=1)            # build once, reuse for every call
def _pipe():
    return pipeline(                       # create a summarisation pipeline object …
        "summarization",                   # … task type
        model="sshleifer/distilbart-cnn-12-6",   # … pick a lightweight news-tuned model
        tokenizer="sshleifer/distilbart-cnn-12-6",   # matching tokenizer
        framework="pt",                    # use PyTorch backend
        truncation=True,                   # chop long inputs to model’s max length
    )

# -------- PAGE SCRAPER --------
def _scrape(url: str, max_chars: int = 3000) -> str:
    """Return bare article text (first 3 000 chars) or '' on failure."""
    try:
        html = requests.get(url, timeout=10).text  # download HTML (10-s timeout)
    except Exception:
        return ""
    soup = BeautifulSoup(html, "lxml")             # parse HTML
    txt = " ".join(                                # join every <p> as one string
        p.get_text(" ", strip=True) for p in soup.find_all("p")
    )
    txt = re.sub(r"\s+", " ", txt)                 # collapse multiple spaces/newlines
    return txt[:max_chars]                         # trim to max_chars for speed

# -------- PUBLIC ENTRY POINT --------
def summarize(article: dict) -> str:
    """
    Given an article dict from fetchers.py, return a two-sentence
    abstractive summary (or a fallback notice).
    """
    body = _scrape(article["url"])                 # grab raw page text
    if len(body) < 200:                            # page too short or fetch failed
        return "(no article text)"

    pipe = _pipe()                                 # load cached HF pipeline
    result = pipe(                                 # run model inference
        body,
        max_length=60, min_length=25, do_sample=False
    )[0]["summary_text"]
    return result.replace("\n", " ").strip()       # flatten newlines, trim edges