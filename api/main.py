from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="KaybolanDiller API",
    description="API for translating between rare and endangered languages",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str

class TranslationResponse(BaseModel):
    translated_text: str
    confidence: float
    source_lang: str
    target_lang: str

@app.get("/")
async def root():
    return {"message": "Welcome to KaybolanDiller API"}

@app.get("/languages")
async def get_supported_languages():
    # TODO: Implement language list
    return {
        "turkish_dialects": ["Meskhetian", "Karamanlı", "Gagauz", "Rumelian", "Cypriot"],
        "turkic_languages": ["Uyghur", "Chuvash", "Kazakh", "Bashkir", "Crimean Tatar"],
        "other_languages": ["Ainu", "Cherokee", "Basque"]
    }

@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    try:
        # TODO: Implement actual translation logic
        return TranslationResponse(
            translated_text="Sample translation",
            confidence=0.95,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 