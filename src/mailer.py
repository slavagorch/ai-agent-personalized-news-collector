"""
Send the Markdown digest via plain-text email.
"""
import os, smtplib, ssl, certifi          # ← new import
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send(markdown: str):
    msg = MIMEText(markdown, "plain", "utf-8")
    msg["Subject"] = "Daily AI digest"
    msg["From"] = os.getenv("SMTP_USER")
    msg["To"]   = os.getenv("RECIPIENT")

    # point SSL context at certifi’s root store
    ctx = ssl.create_default_context(cafile=certifi.where())

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as s:
        s.starttls(context=ctx)
        s.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASS"))
        s.send_message(msg)