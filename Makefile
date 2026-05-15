.PHONY: install api web test dev

install:
	python3 -m venv venv
	./venv/bin/pip install -r requirements.txt
	cd webapp && npm install

api:
	USE_MOCK_TRANSLATION=true ./venv/bin/uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd webapp && npm run dev

test:
	USE_MOCK_TRANSLATION=true ./venv/bin/pytest

dev:
	@echo "Run 'make api' and 'make web' in separate terminals"
