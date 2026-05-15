import logging
import re
from typing import List, Tuple

from api.languages import LANGUAGE_BY_CODE, LANGUAGES

logger = logging.getLogger(__name__)

# Script / pattern hints for endangered & Turkic languages
SCRIPT_HINTS = [
    (re.compile(r"[\u0400-\u04FF]"), "ru", 0.35),
    (re.compile(r"[\u3040-\u30FF\u4E00-\u9FFF]"), "ain", 0.25),
    (re.compile(r"[\u10A0-\u10FF]"), "ka", 0.30),
]

COMMON_WORDS = {
    "en": {"the", "and", "is", "hello", "world", "you", "are"},
    "tr": {"ve", "bir", "bu", "için", "merhaba", "dünya", "nasılsın", "teşekkür"},
    "de": {"und", "der", "die", "das", "ist", "hallo", "welt"},
    "fr": {"le", "la", "les", "et", "bonjour", "monde"},
    "es": {"el", "la", "los", "hola", "mundo", "gracias"},
    "ru": {"и", "в", "не", "привет", "мир"},
    "mes": {"salam", "sağ", "hoşça", "barış"},
    "ain": {"イランカラペ", "wakka", "エヤッキリ"},
}


def _score_text(text: str, lang_code: str) -> float:
    words = set(re.findall(r"\w+", text.lower(), flags=re.UNICODE))
    if not words:
        return 0.0
    common = COMMON_WORDS.get(lang_code, set())
    if not common:
        return 0.0
    overlap = len(words & common) / max(len(words), 1)
    return min(overlap * 2.5, 0.95)


def detect_language(text: str) -> Tuple[str, str, float, List[dict]]:
    """Detect language from text. Returns (code, name, confidence, alternatives)."""
    text = text.strip()
    if not text:
        return "unknown", "Unknown", 0.0, []

    scores: List[Tuple[str, float]] = []

    for pattern, code, boost in SCRIPT_HINTS:
        if pattern.search(text):
            scores.append((code, boost))

    for lang in LANGUAGES:
        s = _score_text(text, lang.code)
        if s > 0:
            scores.append((lang.code, s))

    try:
        from langdetect import detect_langs

        for item in detect_langs(text):
            code = item.lang
            if code == "zh-cn":
                code = "zh"
            mapped = "tr" if code == "tr" else code
            if mapped in LANGUAGE_BY_CODE or mapped in {"en", "de", "fr", "es", "ru"}:
                scores.append((mapped, item.prob * 0.9))
    except Exception as exc:
        logger.debug("langdetect unavailable: %s", exc)

    if not scores:
        return "en", "English", 0.3, []

    aggregated: dict[str, float] = {}
    for code, score in scores:
        aggregated[code] = aggregated.get(code, 0.0) + score

    ranked = sorted(aggregated.items(), key=lambda x: x[1], reverse=True)
    best_code, best_score = ranked[0]
    best_score = min(best_score, 0.99)

    lang = LANGUAGE_BY_CODE.get(best_code)
    name = lang.name if lang else best_code.upper()

    alternatives = []
    for code, score in ranked[1:4]:
        alt_lang = LANGUAGE_BY_CODE.get(code)
        alternatives.append(
            {
                "code": code,
                "name": alt_lang.name if alt_lang else code,
                "confidence": round(min(score, 0.99), 3),
            }
        )

    return best_code, name, round(best_score, 3), alternatives
