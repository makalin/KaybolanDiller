# Models

Hugging Face model weights are cached automatically under `models/cache/` when `USE_MOCK_TRANSLATION=false`.

Fine-tuned checkpoints for endangered language pairs can be placed here:

```
models/
  cache/          # auto-managed by transformers
  custom/
    en-mes/       # your fine-tuned checkpoint
```

Register custom paths in `api/languages.py` → `MODEL_REGISTRY`.
