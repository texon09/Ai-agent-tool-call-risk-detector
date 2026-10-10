setup:
	pip install -r requirements-dev.txt

run-api:
	python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

run-ui:
	python -m streamlit run frontend/app.py

test:
	python -m pytest -q

lint:
	python -m ruff check .

format:
	python -m ruff format .

data:
	@echo "Not implemented yet"

train:
	@echo "Not implemented yet"

eval:
	@echo "Not implemented yet"

docker-up:
	docker compose up --build

docker-down:
	docker compose down
