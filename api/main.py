import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.config import Settings, get_settings
from api.languages import LANGUAGES, get_language, get_models_for_pair, is_valid_language
from api.model_handler import translation_model
from api.schemas import (
    BatchTranslationRequest,
    BatchTranslationResponse,
    DetectLanguageRequest,
    DetectLanguageResponse,
    HealthResponse,
    LanguageInfo,
    LanguagesResponse,
    ModelInfo,
    ModelsResponse,
    TranslationRequest,
    TranslationResponse,
)
from api.services.detection import detect_language
from api.services.translation import TranslationError, translate, translate_batch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_api_key(
    settings: Settings = Depends(get_settings),
    authorization: Optional[str] = Header(None),
) -> None:
    if not settings.api_key:
        return
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid API key")
    token = authorization.removeprefix("Bearer ").strip()
    if token != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(
        "KaybolanDiller API starting (mock=%s, preload=%s)",
        settings.use_mock_translation,
        settings.preload_models,
    )
    if settings.preload_models and not settings.use_mock_translation:
        from api.languages import MODEL_REGISTRY

        for entry in MODEL_REGISTRY.values():
            try:
                translation_model.load_model(entry["id"], entry["hf_id"])
            except Exception as exc:
                logger.warning("Could not preload %s: %s", entry["id"], exc)
    yield
    logger.info("KaybolanDiller API shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        description="API for translating rare and endangered languages",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins + (["*"] if settings.debug else []),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(TranslationError)
    async def translation_error_handler(_: Request, exc: TranslationError):
        status = 400 if exc.code in {"unsupported_language", "same_language", "invalid_model", "no_model"} else 500
        return JSONResponse(
            status_code=status,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": None,
                }
            },
        )

    prefix = settings.api_prefix

    @app.get("/")
    async def root():
        return {
            "message": "Welcome to KaybolanDiller API",
            "docs": "/docs",
            "health": f"{prefix}/health",
            "version": settings.app_version,
        }

    @app.get(f"{prefix}/health", response_model=HealthResponse)
    async def health():
        return HealthResponse(
            status="ok",
            version=settings.app_version,
            mock_mode=settings.use_mock_translation,
            loaded_models=translation_model.list_loaded(),
        )

    @app.get(f"{prefix}/languages", response_model=LanguagesResponse)
    async def get_supported_languages():
        return LanguagesResponse(
            languages=[
                LanguageInfo(
                    code=lang.code,
                    name=lang.name,
                    family=lang.family,
                    is_endangered=lang.is_endangered,
                    native_name=lang.native_name,
                )
                for lang in LANGUAGES
            ],
            total=len(LANGUAGES),
        )

    @app.get(
        f"{prefix}/models/{{source_language}}/{{target_language}}",
        response_model=ModelsResponse,
        dependencies=[Depends(verify_api_key)],
    )
    async def get_translation_models(source_language: str, target_language: str):
        src = source_language.lower()
        tgt = target_language.lower()
        if not is_valid_language(src) or not is_valid_language(tgt):
            raise HTTPException(status_code=404, detail="Language not found")

        raw_models = get_models_for_pair(src, tgt)
        models = [
            ModelInfo(
                id=m["id"],
                name=m["name"],
                description=m.get("description", ""),
                performance_metrics=m.get(
                    "performance_metrics",
                    {"bleu_score": m.get("bleu_score", 0), "accuracy": m.get("accuracy", 0)},
                ),
            )
            for m in raw_models
        ]
        return ModelsResponse(
            models=models,
            source_language=src,
            target_language=tgt,
        )

    @app.post(
        f"{prefix}/translate",
        response_model=TranslationResponse,
        dependencies=[Depends(verify_api_key)],
    )
    async def translate_text(request: TranslationRequest):
        source = request.resolved_source() or (request.source_lang or "")
        target = request.resolved_target() or (request.target_lang or "")
        text = request.source_text or request.text or ""

        if not text.strip():
            raise HTTPException(status_code=400, detail="source_text cannot be empty")
        if len(text) > settings.max_text_length:
            raise HTTPException(status_code=400, detail="Text exceeds maximum length")

        if not source or not target:
            raise HTTPException(status_code=400, detail="source_language and target_language are required")

        if not is_valid_language(source):
            raise HTTPException(status_code=400, detail=f"Invalid source language: {source}")
        if not is_valid_language(target):
            raise HTTPException(status_code=400, detail=f"Invalid target language: {target}")

        try:
            translated, model_used, confidence, is_demo = translate(
                text, source, target, request.model
            )
        except TranslationError:
            raise
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return TranslationResponse(
            translated_text=translated,
            source_language=source,
            target_language=target,
            model_used=model_used,
            confidence_score=confidence,
            is_demo=is_demo,
        )

    @app.post(
        f"{prefix}/translate/batch",
        response_model=BatchTranslationResponse,
        dependencies=[Depends(verify_api_key)],
    )
    async def translate_batch_endpoint(body: BatchTranslationRequest):
        if len(body.texts) > settings.max_batch_size:
            raise HTTPException(status_code=400, detail="Batch size exceeds limit")

        src = body.source_language.lower()
        tgt = body.target_language.lower()

        if not is_valid_language(src) or not is_valid_language(tgt):
            raise HTTPException(status_code=400, detail="Invalid language code")

        results = []
        for text in body.texts:
            if not text.strip():
                raise HTTPException(status_code=400, detail="Batch contains empty text")
            translated, model_used, confidence, is_demo = translate(
                text, src, tgt, body.model
            )
            results.append(
                TranslationResponse(
                    translated_text=translated,
                    source_language=src,
                    target_language=tgt,
                    model_used=model_used,
                    confidence_score=confidence,
                    is_demo=is_demo,
                )
            )

        return BatchTranslationResponse(translations=results, count=len(results))

    @app.post(f"{prefix}/detect", response_model=DetectLanguageResponse)
    async def detect_language_endpoint(body: DetectLanguageRequest):
        if not body.text.strip():
            raise HTTPException(status_code=400, detail="text cannot be empty")

        code, name, confidence, alternatives = detect_language(body.text)
        return DetectLanguageResponse(
            detected_language=code,
            language_name=name,
            confidence=confidence,
            alternatives=alternatives,
        )

    # Legacy routes (backward compatibility)
    @app.post("/translate", response_model=TranslationResponse, include_in_schema=False)
    async def legacy_translate(request: TranslationRequest):
        return await translate_text(request)

    @app.get("/languages", include_in_schema=False)
    async def legacy_languages():
        resp = await get_supported_languages()
        return {
            "turkish_dialects": [l.name for l in LANGUAGES if l.family == "Turkic" and l.is_endangered],
            "turkic_languages": [l.name for l in LANGUAGES if l.family == "Turkic" and not l.is_endangered],
            "other_languages": [l.name for l in LANGUAGES if l.family not in ("Turkic", "Indo-European")],
            "languages": resp.languages,
        }

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
