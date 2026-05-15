from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Language:
    code: str
    name: str
    family: str
    is_endangered: bool = False
    native_name: Optional[str] = None


LANGUAGES: List[Language] = [
    # High-resource
    Language("en", "English", "Indo-European"),
    Language("tr", "Turkish", "Turkic"),
    Language("de", "German", "Indo-European"),
    Language("fr", "French", "Indo-European"),
    Language("es", "Spanish", "Indo-European"),
    Language("ru", "Russian", "Indo-European"),
    # Turkish dialects
    Language("cy-tr", "Cypriot Turkish", "Turkic", True, "Kıbrıs Türkçesi"),
    Language("rum", "Rumelian Turkish", "Turkic", True, "Rumeli Türkçesi"),
    Language("kar", "Karamanlı Turkish", "Turkic", True, "Karamanlıca"),
    Language("mes", "Meskhetian Turkish", "Turkic", True, "Ahıska Türkçesi"),
    Language("gag", "Gagauz", "Turkic", True, "Gagavuzca"),
    # Turkic
    Language("az", "Azerbaijani", "Turkic"),
    Language("tk", "Turkmen", "Turkic"),
    Language("kk", "Kazakh", "Turkic"),
    Language("ky", "Kyrgyz", "Turkic"),
    Language("uz", "Uzbek", "Turkic"),
    Language("ug", "Uyghur", "Turkic", True),
    Language("tt", "Tatar", "Turkic"),
    Language("ba", "Bashkir", "Turkic"),
    Language("crh", "Crimean Tatar", "Turkic", True),
    Language("cv", "Chuvash", "Turkic", True),
    Language("sah", "Yakut", "Turkic", True),
    Language("alt", "Altai", "Turkic", True),
    # Other endangered (planned / experimental)
    Language("ain", "Ainu", "Ainu", True),
    Language("chr", "Cherokee", "Iroquoian", True),
    Language("eu", "Basque", "Basque", True),
    Language("zza", "Zazaki", "Indo-European", True),
]

LANGUAGE_BY_CODE: Dict[str, Language] = {lang.code: lang for lang in LANGUAGES}

# Helsinki-NLP OPUS-MT models for supported pairs
MODEL_REGISTRY: Dict[Tuple[str, str], dict] = {
    ("en", "tr"): {
        "id": "helsinki-en-tr",
        "name": "Helsinki-NLP OPUS-MT EN→TR",
        "hf_id": "Helsinki-NLP/opus-mt-en-tr",
        "description": "English to Turkish neural MT",
        "bleu_score": 0.42,
        "accuracy": 0.88,
    },
    ("tr", "en"): {
        "id": "helsinki-tr-en",
        "name": "Helsinki-NLP OPUS-MT TR→EN",
        "hf_id": "Helsinki-NLP/opus-mt-tr-en",
        "description": "Turkish to English neural MT",
        "bleu_score": 0.41,
        "accuracy": 0.87,
    },
    ("en", "de"): {
        "id": "helsinki-en-de",
        "name": "Helsinki-NLP OPUS-MT EN→DE",
        "hf_id": "Helsinki-NLP/opus-mt-en-de",
        "description": "English to German neural MT",
        "bleu_score": 0.45,
        "accuracy": 0.90,
    },
    ("de", "en"): {
        "id": "helsinki-de-en",
        "name": "Helsinki-NLP OPUS-MT DE→EN",
        "hf_id": "Helsinki-NLP/opus-mt-de-en",
        "description": "German to English neural MT",
        "bleu_score": 0.44,
        "accuracy": 0.89,
    },
    ("en", "ru"): {
        "id": "helsinki-en-ru",
        "name": "Helsinki-NLP OPUS-MT EN→RU",
        "hf_id": "Helsinki-NLP/opus-mt-en-ru",
        "description": "English to Russian neural MT",
        "bleu_score": 0.40,
        "accuracy": 0.86,
    },
    ("ru", "en"): {
        "id": "helsinki-ru-en",
        "name": "Helsinki-NLP OPUS-MT RU→EN",
        "hf_id": "Helsinki-NLP/opus-mt-ru-en",
        "description": "Russian to English neural MT",
        "bleu_score": 0.39,
        "accuracy": 0.85,
    },
}

# Demo lexicon for rare pairs (placeholder until fine-tuned models ship)
DEMO_LEXICON: Dict[Tuple[str, str], Dict[str, str]] = {
    ("en", "mes"): {
        "hello": "salam",
        "thank you": "sağ ol",
        "goodbye": "hoşça kal",
        "peace": "barış",
    },
    ("mes", "en"): {
        "salam": "hello",
        "sağ ol": "thank you",
        "hoşça kal": "goodbye",
        "barış": "peace",
    },
    ("en", "ain"): {
        "hello": "イランカラペ",
        "thank you": "エヤッキリ",
        "water": "wakka",
    },
    ("ain", "en"): {
        "イランカラペ": "hello",
        "エヤッキリ": "thank you",
        "wakka": "water",
    },
}


def get_language(code: str) -> Optional[Language]:
    return LANGUAGE_BY_CODE.get(code.lower())


def is_valid_language(code: str) -> bool:
    return code.lower() in LANGUAGE_BY_CODE


def get_models_for_pair(source: str, target: str) -> List[dict]:
    key = (source.lower(), target.lower())
    if key in MODEL_REGISTRY:
        return [MODEL_REGISTRY[key]]
    if key in DEMO_LEXICON:
        return [
            {
                "id": f"demo-lexicon-{source}-{target}",
                "name": "Demo Lexicon (beta)",
                "description": "Phrase-level lexicon for endangered language pairs",
                "performance_metrics": {"bleu_score": 0.15, "accuracy": 0.55},
            }
        ]
    return []


def list_language_families() -> Dict[str, List[Language]]:
    families: Dict[str, List[Language]] = {}
    for lang in LANGUAGES:
        families.setdefault(lang.family, []).append(lang)
    return families
