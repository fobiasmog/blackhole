test:
	python -m pytest tests/ -v

test-cov:
	python -m pytest tests/ -v --cov=blackhole_io --cov-report=term-missing

format:
	isort src tests && \
	ruff clean && \
	ruff check --fix src tests