from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class LanguageInfo(BaseModel):
    code: str
    name: str
    family: str
    is_endangered: bool = False
    native_name: Optional[str] = None


class LanguagesResponse(BaseModel):
    languages: List[LanguageInfo]
    total: int


class TranslationRequest(BaseModel):
    source_text: Optional[str] = Field(None, max_length=5000)
    source_language: Optional[str] = Field(None, min_length=2, max_length=10)
    target_language: Optional[str] = Field(None, min_length=2, max_length=10)
    model: Optional[str] = None

    # Legacy field aliases
    text: Optional[str] = None
    source_lang: Optional[str] = None
    target_lang: Optional[str] = None

    @model_validator(mode="after")
    def merge_aliases(self):
        if not self.source_text and self.text:
            self.source_text = self.text
        if not self.source_language and self.source_lang:
            self.source_language = self.source_lang
        if not self.target_language and self.target_lang:
            self.target_language = self.target_lang
        return self

    def resolved_source(self) -> str:
        return (self.source_language or self.source_lang or "").lower()

    def resolved_target(self) -> str:
        return (self.target_language or self.target_lang or "").lower()


class TranslationResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    translated_text: str
    source_language: str
    target_language: str
    model_used: str
    confidence_score: float
    is_demo: bool = False


class BatchTranslationRequest(BaseModel):
    texts: List[str] = Field(..., min_length=1, max_length=32)
    source_language: str
    target_language: str
    model: Optional[str] = None


class BatchTranslationResponse(BaseModel):
    translations: List[TranslationResponse]
    count: int


class DetectLanguageRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)


class DetectLanguageResponse(BaseModel):
    detected_language: str
    language_name: str
    confidence: float
    alternatives: List[dict] = []


class ModelInfo(BaseModel):
    id: str
    name: str
    description: str
    performance_metrics: dict


class ModelsResponse(BaseModel):
    models: List[ModelInfo]
    source_language: str
    target_language: str


class HealthResponse(BaseModel):
    status: str
    version: str
    mock_mode: bool
    loaded_models: List[str]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None
