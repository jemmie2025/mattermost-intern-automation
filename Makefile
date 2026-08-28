.PHONY: install test run compose-up compose-down

install:
	python -m pip install --requirement requirements-dev.txt

test:
	pytest -q

run:
	uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload

compose-up:
	docker compose up --build --detach

compose-down:
	docker compose down

