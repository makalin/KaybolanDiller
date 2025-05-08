from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslationModel:
    def __init__(self):
        self.models: Dict[str, AutoModelForSeq2SeqLM] = {}
        self.tokenizers: Dict[str, AutoTokenizer] = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Using device: {self.device}")

    def load_model(self, model_name: str, model_path: Optional[str] = None):
        """Load a translation model and its tokenizer."""
        try:
            if model_path:
                self.tokenizers[model_name] = AutoTokenizer.from_pretrained(model_path)
                self.models[model_name] = AutoModelForSeq2SeqLM.from_pretrained(model_path)
            else:
                # Use default model for testing
                self.tokenizers[model_name] = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-tr")
                self.models[model_name] = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-tr")
            
            self.models[model_name].to(self.device)
            logger.info(f"Successfully loaded model: {model_name}")
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            raise

    def translate(self, text: str, model_name: str) -> str:
        """Translate text using the specified model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not loaded")

        try:
            tokenizer = self.tokenizers[model_name]
            model = self.models[model_name]

            # Tokenize input
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate translation
            outputs = model.generate(**inputs, max_length=128)
            
            # Decode output
            translated = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return translated

        except Exception as e:
            logger.error(f"Translation error: {str(e)}")
            raise

# Singleton instance
translation_model = TranslationModel() 