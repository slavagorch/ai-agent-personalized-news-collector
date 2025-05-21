# AI-Agent-Personalized-News-Collector

A lightweight Python pipeline that fetches AI‑related articles from TechCrunch and Hacker News, filters by keywords, generates two‑sentence summaries offline with DistilBART‑CNN, and emails a daily digest—all free and fully local.

## Why

* Automate reading the latest AI news without paying API fees
* Get concise, relevant updates in your inbox
* Easy to extend with embeddings, feedback loops, or a web UI later

## Features (MVP)

* Fetch up to 10 items from each source
* Regex-based keyword filtering for core AI terms
* Abstractive summarization with a local Hugging Face model (sshleifer/distilbart-cnn-12-6)
* Email delivery via SMTP (Gmail app password or any SMTP)
* Logging for visibility into each step

## Prerequisites

* Python 3.9+
* SMTP-enabled email account (Gmail recommended)

## Installation

```bash
git clone <repo_url>
cd ai-agent-personalized-news-collector
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create a `.env` in the project root with:

```dotenv
# Secrets for email delivery
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@example.com
SMTP_PASS=<app-password>
RECIPIENT=you@example.com
```

## Usage

```bash
# Run once manually
python src/pipeline.py

# Automate (cron example, runs daily at 07:30)
30 7 * * * /path/to/venv/bin/python /path/to/repo/src/pipeline.py
```

### Logging

Pipeline logs progress to the console (fetch → filter → summarize → send).

## Project Structure

```
ai-agent-personalized-news-collector/
├─ .env                # your secrets (gitignored)
├─ requirements.txt    # dependencies
└─ src/
   ├─ fetchers.py      # TechCrunch & HN scrapers with limit=10
   ├─ filters.py       # regex AI-term filter
   ├─ summarizer.py    # offline DistilBART summariser
   ├─ mailer.py        # SMTP email sender with certifi
   └─ pipeline.py      # orchestrator + logging
```

## Next Steps

* Replace regex with embeddings + feedback loop
* Add a web UI or Slack integration
* Extend sources (ArXiv, Twitter, RSS list)
* Persist history and user preferences
