import logging
from typing import Dict, Optional

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from api.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TranslationModel:
    def __init__(self):
        self.models: Dict[str, AutoModelForSeq2SeqLM] = {}
        self.tokenizers: Dict[str, AutoTokenizer] = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        settings = get_settings()
        self.cache_dir = settings.default_model_cache
        logger.info("Translation engine using device: %s", self.device)

    def load_model(self, model_name: str, model_path: str):
        """Load a translation model and its tokenizer."""
        if model_name in self.models:
            return

        try:
            self.tokenizers[model_name] = AutoTokenizer.from_pretrained(
                model_path,
                cache_dir=self.cache_dir,
            )
            self.models[model_name] = AutoModelForSeq2SeqLM.from_pretrained(
                model_path,
                cache_dir=self.cache_dir,
            )
            self.models[model_name].to(self.device)
            self.models[model_name].eval()
            logger.info("Loaded model: %s (%s)", model_name, model_path)
        except Exception as exc:
            logger.error("Error loading model %s: %s", model_name, exc)
            raise

    def translate(self, text: str, model_name: str, max_length: int = 256) -> str:
        """Translate text using the specified model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not loaded")

        tokenizer = self.tokenizers[model_name]
        model = self.models[model_name]

        inputs = tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=max_length,
                num_beams=4,
                early_stopping=True,
            )

        return tokenizer.decode(outputs[0], skip_special_tokens=True)

    def list_loaded(self) -> list[str]:
        return list(self.models.keys())

    def unload(self, model_name: str) -> bool:
        if model_name in self.models:
            del self.models[model_name]
            del self.tokenizers[model_name]
            if self.device == "cuda":
                torch.cuda.empty_cache()
            return True
        return False


translation_model = TranslationModel()
