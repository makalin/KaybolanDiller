# Contributing to KaybolanDiller

Thank you for helping preserve endangered languages through open-source NLP.

## Getting Started

1. Fork and clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   ```
3. Run the API: `./scripts/dev.sh`
4. Run tests: `pytest`

## Adding a Language or Model

1. Register the language in `api/languages.py` with ISO-style code, family, and endangered flag.
2. Add a Helsinki-NLP or custom Hugging Face model mapping in `MODEL_REGISTRY`, or phrase entries in `DEMO_LEXICON` for beta pairs.
3. Add tests in `tests/backend/`.
4. Update `languages.md` and open a pull request.

## Code Style

- Python: PEP 8, type hints where practical
- Keep API schemas aligned with `api.md`
- Use `USE_MOCK_TRANSLATION=true` in CI and local dev unless testing real models

## Pull Requests

- One feature or fix per PR
- Include test coverage for API changes
- Describe language pairs or datasets affected
