import datetime as dt
from pathlib import Path

def write_digest(picks, out_path: str):
    lines = [f"# AI digest – {dt.date.today():%Y-%m-%d}\n"]
    for art in picks:
        lines.append(f"## {art['title']}\n")
        lines.append(f"{art['summary']}\n")
        lines.append(f"[Read more]({art['url']})  \n— {art['source']}, "
                     f"{art['published']:%d %b %Y}\n")
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines), encoding="utf-8")