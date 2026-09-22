import json
import re
from functools import lru_cache
from pathlib import Path

_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "timeline.json"

_STOPWORDS = {
    "a", "o", "as", "os", "de", "da", "do", "das", "dos", "e", "é", "em", "um", "uma",
    "que", "como", "para", "por", "com", "no", "na", "nos", "nas", "qual", "quais",
    "quando", "onde", "foi", "era", "sao", "são", "ou", "se", "the", "of", "in", "on",
    "and", "what", "how", "was", "were", "is", "are",
}


@lru_cache
def _load() -> dict:
    with _DATA_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def list_eras() -> list[dict]:
    return list(_load()["eras"])


def list_timeline(era: str | None = None) -> list[dict]:
    marcos = _load()["marcos"]
    if era:
        marcos = [m for m in marcos if m["era"] == era]
    return sorted(marcos, key=lambda m: m["ano"])


def get_marco(marco_id: str) -> dict | None:
    for marco in _load()["marcos"]:
        if marco["id"] == marco_id:
            return marco
    return None


def _tokenize(text: str) -> set[str]:
    words = re.findall(r"[a-zà-ú0-9]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 1}


def search_relevant(query: str, max_results: int = 5) -> list[dict]:
    """Keyword search over titulo, tags, tecnica e ano. Retorna [] se nada casar."""
    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    scored: list[tuple[float, dict]] = []
    for marco in _load()["marcos"]:
        score = 0.0
        score += 3 * len(query_tokens & _tokenize(marco["titulo"]))
        score += 2 * len(query_tokens & _tokenize(" ".join(marco["tags"])))
        score += 2 * len(query_tokens & _tokenize(marco["tecnica"]))
        if str(marco["ano"]) in query_tokens:
            score += 3

        if score > 0:
            scored.append((score, marco))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [marco for _, marco in scored[:max_results]]
