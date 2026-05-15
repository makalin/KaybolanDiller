import logging
import re
from typing import List, Optional, Tuple

from api.config import get_settings
from api.languages import (
    DEMO_LEXICON,
    MODEL_REGISTRY,
    get_language,
    get_models_for_pair,
    is_valid_language,
)
from api.model_handler import translation_model

logger = logging.getLogger(__name__)


class TranslationError(Exception):
    def __init__(self, message: str, code: str = "translation_error"):
        self.message = message
        self.code = code
        super().__init__(message)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _lexicon_translate(text: str, source: str, target: str) -> Optional[Tuple[str, float]]:
    lexicon = DEMO_LEXICON.get((source, target))
    if not lexicon:
        return None

    key = _normalize(text)
    if key in lexicon:
        return lexicon[key], 0.85

    # Word-by-word fallback for short phrases
    words = key.split()
    if len(words) <= 6:
        translated_words = [lexicon.get(w, w) for w in words]
        if translated_words != words:
            return " ".join(translated_words), 0.55

    return None


def _mock_translate(text: str, source: str, target: str) -> Tuple[str, str, float, bool]:
    lex = _lexicon_translate(text, source, target)
    if lex:
        return lex[0], f"demo-lexicon-{source}-{target}", lex[1], True

    src_lang = get_language(source)
    tgt_lang = get_language(target)
    src_name = src_lang.name if src_lang else source
    tgt_name = tgt_lang.name if tgt_lang else target
    mock = f"[{src_name} → {tgt_name}] {text}"
    return mock, "mock-translator", 0.5, True


def translate(
    text: str,
    source: str,
    target: str,
    model_id: Optional[str] = None,
) -> Tuple[str, str, float, bool]:
    source = source.lower()
    target = target.lower()

    if source == target:
        raise TranslationError("Source and target languages must differ", "same_language")

    if not is_valid_language(source) or not is_valid_language(target):
        raise TranslationError(
            f"Unsupported language pair: {source} → {target}",
            "unsupported_language",
        )

    settings = get_settings()

    if settings.use_mock_translation:
        return _mock_translate(text, source, target)

    # Try demo lexicon first for rare pairs
    lex = _lexicon_translate(text, source, target)
    if lex:
        model_info = get_models_for_pair(source, target)
        mid = model_info[0]["id"] if model_info else f"demo-lexicon-{source}-{target}"
        return lex[0], mid, lex[1], True

    pair = (source, target)
    if pair not in MODEL_REGISTRY:
        available = get_models_for_pair(source, target)
        if not available:
            raise TranslationError(
                f"No model available for {source} → {target}. "
                "Enable USE_MOCK_TRANSLATION=true for development, or contribute a model.",
                "no_model",
            )

    model_entry = MODEL_REGISTRY[pair]
    if model_id and model_id != model_entry["id"]:
        # Allow explicit model id if it matches registry entry
        matching = [m for m in [model_entry] if m["id"] == model_id]
        if not matching:
            raise TranslationError(f"Model '{model_id}' not found for this pair", "invalid_model")

    hf_id = model_entry["hf_id"]
    cache_key = model_entry["id"]

    try:
        if cache_key not in translation_model.models:
            translation_model.load_model(cache_key, hf_id)

        translated = translation_model.translate(text, cache_key)
        return translated, model_entry["id"], 0.88, False
    except Exception as exc:
        logger.error("Neural translation failed: %s", exc)
        raise TranslationError(
            f"Translation model failed: {exc}",
            "model_error",
        ) from exc


def translate_batch(
    texts: List[str],
    source: str,
    target: str,
    model_id: Optional[str] = None,
) -> List[Tuple[str, str, float, bool]]:
    return [translate(t, source, target, model_id) for t in texts]
