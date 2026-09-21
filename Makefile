install:
	pip install .[dev]

lint:
	ruff check .

typecheck:
	mypy src

test:
	pytest -q

docker-build:
	docker build -t sando_masterapi:latest .

docker-run:
	docker compose up
