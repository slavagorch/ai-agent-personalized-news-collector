import re

PATTERN = re.compile(
    r"(Python|AI|LLM|GPT|LangChain|AutoGen|vector\s?DB|open[-\s]?source)", re.I
)

def passes(article: dict) -> bool:
    text = f"{article['title']} {article['desc']}"
    return bool(PATTERN.search(text))